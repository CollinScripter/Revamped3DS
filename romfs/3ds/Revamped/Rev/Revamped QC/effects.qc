
// Effects code (EFF) --

// TE effects/muzzleflash/messages

// modular efs
var float ef_red  = 0;           // used for glow on pent item
var float ef_pent = EF_DIMLIGHT; // used for pent effect on player
var float ef_blue = 0;           // used for glow on quad
var float ef_quad = EF_DIMLIGHT; // used for quad effect on player

// base te write functions
void WriteVector (float msg, vector org) =
{
	WriteCoord (msg, org_x);
	WriteCoord (msg, org_y);
	WriteCoord (msg, org_z);
};

#ifdef NETQUAKE
void(vector org, float effect) _EFF_PointEffect =
{
	WriteByte (MSG_BROADCAST, SVC_TEMPENTITY);
	WriteByte (MSG_BROADCAST, effect);
	WriteVector (MSG_BROADCAST, org);
};

void(entity ent, vector org, vector org2, float effect) _EFF_BeamEffect =
{
	WriteByte (MSG_BROADCAST, SVC_TEMPENTITY);
	WriteByte (MSG_BROADCAST, effect);
	WriteEntity (MSG_BROADCAST, ent);
	WriteVector (MSG_BROADCAST, org);
	WriteVector (MSG_BROADCAST, org2);
};

void(vector org, float damage, float effect) _EFF_CountEffect =
{
	WriteByte (MSG_BROADCAST, SVC_TEMPENTITY);
	WriteByte (MSG_BROADCAST, effect);
	WriteByte (MSG_BROADCAST, damage);
	WriteVector (MSG_BROADCAST, org);
};

#define EFF_PointEffect(a,b,c) _EFF_PointEffect(a,b)
#define EFF_BeamEffect(a,b,c,d,e) _EFF_BeamEffect(a,b,c,d)
#define EFF_CountEffect(a,b,c,d) _EFF_CountEffect(a,b,c)
#else
void(vector org, float effect, float mcast) EFF_PointEffect =
{
	WriteByte (MSG_MULTICAST, SVC_TEMPENTITY);
	WriteByte (MSG_MULTICAST, effect);
	WriteVector (MSG_MULTICAST, org);
	multicast (org, mcast);
};

void(entity ent, vector org, vector org2, float effect, float mcast) EFF_BeamEffect =
{
	WriteByte (MSG_MULTICAST, SVC_TEMPENTITY);
	WriteByte (MSG_MULTICAST, effect);
	WriteEntity (MSG_MULTICAST, ent);
	WriteVector (MSG_MULTICAST, org);
	WriteVector (MSG_MULTICAST, org2);
	multicast (org, mcast);
};

void(vector org, float damage, float effect, float mcast) EFF_CountEffect =
{
	WriteByte (MSG_MULTICAST, SVC_TEMPENTITY);
	WriteByte (MSG_MULTICAST, effect);
	WriteByte (MSG_MULTICAST, damage);
	WriteVector (MSG_MULTICAST, org);
	multicast (org, mcast);
};
#endif

/*
================
SpawnBlood
================
*/
void(vector org, float damage) _SpawnBlood_TEBlood =
{
	te_blood(org, '0 0 0', damage*2);
};

void(vector org, float damage) _SpawnBlood =
{
#ifdef NETQUAKE
	particle (org, '0 0 0', 73, damage*2);
#else
	EFF_CountEffect(org, damage, TE_BLOOD, MULTICAST_PVS);
#endif
};
/*
void() NadeTouch =
{
if (other.nade_lives > 4)
{
sprint (other, "Can't pick up anymore grenades/n");
return;
}
other.nade_lives = other.nade_lives + 1;
};

*/
void() s_smokee6 = [5,		SUB_Remove] {};
void() s_smokee5 = [4,		s_smokee6] {};
void() s_smokee4 = [3,		s_smokee5] {};
void() s_smokee3 = [2,		s_smokee4] {};
void() s_smokee2 = [1,		s_smokee3] {};
void() s_smokee1 = [0,		s_smokee2] {};

void() s_needle3 = [2,		SUB_Remove] {};
void() s_needle2 = [1,		s_needle3] {};
void() s_needle1 = [0,		s_needle2] {};

void() s_plasma14 = [13,		SUB_Remove] {};
void() s_plasma13 = [12,		s_plasma14] {};
void() s_plasma12 = [11,		s_plasma13] {};
void() s_plasma11 = [10,		s_plasma12] {};
void() s_plasma10 = [9,		s_plasma11] {};
void() s_plasma9 = [8,		s_plasma10] {};
void() s_plasma8 = [7,		s_plasma9] {};
void() s_plasma7 = [6,		s_plasma8] {};
void() s_plasma6 = [5,		s_plasma7] {};
void() s_plasma5 = [4,		s_plasma6] {};
void() s_plasma4 = [3,		s_plasma5] {};
void() s_plasma3 = [2,		s_plasma4] {};
void() s_plasma2 = [1,		s_plasma3] {};
void() s_plasma1 = [0,		s_plasma2] {};

void(vector org) createpinkdust =
{
	local entity s;


	s = self; // save old self

	self = spawn();

	self.movetype = MOVETYPE_NONE;
	self.velocity = '0 0 0';
	self.touch = SUB_Null;
	setmodel (self, "progs/needler_dust.spr");
	setorigin (self, org);
	self.solid = SOLID_NOT;
	s_needle1();
	self = s; // restore old self
	
};
void(vector org) createplasma =
{
	local entity s;


	s = self; // save old self

	self = spawn();

	self.movetype = MOVETYPE_NONE;
	self.velocity = '0 0 0';
	self.touch = SUB_Null;
	setmodel (self, "sprites/s_plasma4.spr");
	setorigin (self, org);
	self.solid = SOLID_NOT;
	s_plasma1();
	self = s; // restore old self
	
};

void() s_plasmaa5 = [4,		SUB_Remove] {};
void() s_plasmaa4 = [3,		s_plasmaa5] {createplasma(self.origin);};
void() s_plasmaa3 = [2,		s_plasmaa4] {};
void() s_plasmaa2 = [1,		s_plasmaa3] {};
void() s_plasmaa1 = [0,		s_plasmaa2] {};

void(vector org) plasmaexplo =
{
	local entity s;
	local float r;
	r = random();


	s = self; // save old self

	self = spawn();

	self.movetype = MOVETYPE_NONE;
	self.velocity = '0 0 0';
	self.touch = SUB_Null;
	setmodel (self, "sprites/plasma3.spr");
	setorigin (self, org);
	self.solid = SOLID_NOT;
	
	// So that debris comes out in random spurts over It coming out in the same number every time --Mexicouger

	s_plasmaa1 ();

	self = s; // restore old self
};
void(vector org) pistolsmoke =
{
	local entity s;


	s = self; // save old self

	self = spawn();

	self.movetype = MOVETYPE_FLY;
	

	self.velocity = v_forward;
	self.velocity = (self.velocity * 80);
	self.touch = SUB_Null;
	setmodel (self, "sprites/s_smoke2.spr");
	setorigin (self, ((org + (v_forward * 15)) + '0 0 12'));
	self.solid = SOLID_NOT;
	s_smokee1();
	self = s; // restore old self
};

// #if defined(NETQUAKE) || defined(MONSTERS)


void() s_explode14 = [13,		SUB_Remove] {};
void() s_explode13 = [12,		s_explode14] {};
void() s_explode12 = [11,		s_explode13] {};
void() s_explode11 = [10,		s_explode12] {};
void() s_explode10 = [9,		s_explode11] {};
void() s_explode9 = [8,		s_explode10] {};
void() s_explode8 = [7,		s_explode9] {};
void() s_explode7 = [6,		s_explode8] {};
void() s_explode6 = [5,		s_explode7] {};
void() s_explode5 = [4,		s_explode6] {};
void() s_explode4 = [3,		s_explode5] {};
void() s_explode3 = [2,		s_explode4] {};
void() s_explode2 = [1,		s_explode3] {};
void() s_explode1 = [0,		s_explode2] {};

void(vector org) CreateExplosion =
{
	local entity s;
	local float r;
	r = random();


	s = self; // save old self

	self = spawn();

	self.movetype = MOVETYPE_NONE;
	self.velocity = '0 0 0';
	self.touch = SUB_Null;
	setmodel (self, "progs/s_explod.spr");
	setorigin (self, org);
	self.solid = SOLID_NOT;
	sound (self, CHAN_WEAPON, "weapons/r_exp3.wav", 1, ATTN_NORM);
	// So that debris comes out in random spurts over It coming out in the same number every time --Mexicouger
		s_explode1 ();

	self = s; // restore old self
};
// #endif

void(vector org) _TE_explosion =
{
	EFF_PointEffect(org, TE_EXPLOSION, MULTICAST_PHS);
#ifdef NETQUAKE
	CreateExplosion(org);
#endif
};

void(vector org) _TE_gunshot =
{
#ifdef NETQUAKE
	EFF_PointEffect(org, TE_GUNSHOT, MULTICAST_PVS);
#else
	EFF_CountEffect(org, 3, TE_GUNSHOT, MULTICAST_PVS);
#endif
};

void(vector org) _TE_spike =
{
	EFF_PointEffect(org, TE_SPIKE, MULTICAST_PHS);
};

void(vector org) _TE_knightspike =
{
	EFF_PointEffect(org, TE_KNIGHTSPIKE, MULTICAST_PHS);
};

void(vector org) _TE_wizspike =
{
	EFF_PointEffect(org, TE_WIZSPIKE, MULTICAST_PHS);
};

void(vector org) _TE_superspike =
{
	EFF_PointEffect(org, TE_SUPERSPIKE, MULTICAST_PHS);
};

void(vector org) _TE_teleport =
{
	EFF_PointEffect(org, TE_TELEPORT, MULTICAST_PHS);
};

void(vector org) _TE_lavasplash = 
{
	EFF_PointEffect(org, TE_LAVASPLASH, MULTICAST_PVS);
};

void(vector org) _TE_tarexplosion = 
{
	EFF_PointEffect(org, TE_TAREXPLOSION, MULTICAST_PHS);
};

void(entity ent, vector start, vector end) _TE_lightning1 =
{
	EFF_BeamEffect (ent, start, end, TE_LIGHTNING1, MULTICAST_PHS);
};

void(entity ent, vector start, vector end) _TE_lightning2 =
{
	EFF_BeamEffect (ent, start, end, TE_LIGHTNING2, MULTICAST_PHS);
};

void(entity ent, vector start, vector end) _TE_lightning3 =
{
	EFF_BeamEffect (ent, start, end, TE_LIGHTNING3, MULTICAST_PHS);
};

void(vector org) TE_lightningblood =
{
#ifdef NETQUAKE
	particle(org, '0 0 100', 225, 120);
#else
	EFF_PointEffect(org, TE_LIGHTNINGBLOOD, MULTICAST_PVS);
#endif
};

// function pointers for TE calls
var void(vector org, float damage) SpawnBlood = _SpawnBlood;
var void(vector org) TE_explosion = _TE_explosion;
var void(vector org) TE_gunshot = _TE_gunshot;
var void(vector org) TE_spike = _TE_spike;
var void(vector org) TE_knightspike = _TE_knightspike;
var void(vector org) TE_wizspike = _TE_wizspike;
var void(vector org) TE_superspike = _TE_superspike;
var void(vector org) TE_teleport = _TE_teleport;
var void(vector org) TE_lavasplash = _TE_lavasplash;
var void(vector org) TE_tarexplosion = _TE_tarexplosion;
var void(entity ent, vector start, vector end) TE_lightning1 = _TE_lightning1;
var void(entity ent, vector start, vector end) TE_lightning2 = _TE_lightning2;
var void(entity ent, vector start, vector end) TE_lightning3 = _TE_lightning3;

// set effects function, takes function pointers and assigns them based on detected builtins
void() EFF_SetEffects =
{
	if (eng_support & ENG_EFRED)
	{
		ef_pent = 128;
		ef_red = 128;
	}

	if (eng_support & ENG_EFBLUE)
	{
		ef_blue = 64;
		ef_quad = 64;
	}

	if (eng_support & ENG_TEBUILTINS)
	{
		// use TE_ builtins instead
		TE_explosion = _te_explosion;
		TE_gunshot = _te_gunshot;
		TE_spike = _te_spike;
		TE_knightspike = _te_knightspike;
		TE_wizspike = _te_wizspike;
		TE_superspike = _te_superspike;
		TE_teleport = _te_teleport;
		TE_lavasplash = _te_lavasplash;
		TE_tarexplosion = _te_tarexplosion;
		TE_lightning1 = _te_lightning1;
		TE_lightning2 = _te_lightning2;
		TE_lightning3 = _te_lightning3;
	}

	if (eng_support & ENG_TEBLOOD)
		SpawnBlood = _SpawnBlood_TEBlood; // use TE_Blood builtin instead
};

// view kicks
void(entity ent) VK_smallkick =
{
#ifdef NETQUAKE
	self.punchangle_x = -2;
#else
	msg_entity = ent;
	WriteByte (MSG_ONE, SVC_SMALLKICK);
#endif
}

void(entity ent) VK_bigkick =
{
#ifdef NETQUAKE
	self.punchangle_x = -4;
#else
	msg_entity = ent;
	WriteByte (MSG_ONE, SVC_BIGKICK);
#endif
}
void(entity ent) VK_hugekick =
{
#ifdef NETQUAKE
	self.punchangle_x = -8;
#else
	msg_entity = ent;
	WriteByte (MSG_ONE, SVC_HUGEKICK);
#endif
}

// muzzle flash
void() muzzleflash =
{
#ifdef NETQUAKE
	self.effects |= EF_MUZZLEFLASH;
#else
	WriteByte (MSG_MULTICAST, SVC_MUZZLEFLASH);
	WriteEntity (MSG_MULTICAST, self);
	multicast (self.origin, MULTICAST_PVS);
#endif
};

// touch blood functions
void(float damage) spawn_touchblood =
{
	local vector    vel;

	vel = normalize (self.velocity);
	vel = normalize(vel + v_up*(random()- 0.5) + v_right*(random()- 0.5));
	vel = vel + 2*trace_plane_normal;
	vel = vel * 0.4;
	SpawnBlood (self.origin + vel, damage);
}; 
/*
============================================
HUD weapon ammo counter. Counts ammo and displays 
Number of bullets.

============================================
*/
void() AmmoCounter =
{
if (self.weapon == IT_SHOTGUN)	
{
	stuffcmd (self, "cl_ar_ammo 0\n");		
	stuffcmd (self, "cl_shotgun_ammo 0\n");
	stuffcmd (self, "cl_needler_ammo 0\n");
	stuffcmd (self, "cl_rocket_ammo 0\n");
	stuffcmd (self, "cl_weaponhud  0\n");
	
	if (self.ammo_shells == 12)
	stuffcmd (self, "cl_pistol_ammo 12\n");
	if (self.ammo_shells == 11)
	stuffcmd (self, "cl_pistol_ammo 11\n");
	if (self.ammo_shells == 10)
	stuffcmd (self, "cl_pistol_ammo 10\n");
	if (self.ammo_shells == 9)
	stuffcmd (self, "cl_pistol_ammo 9\n");
	if (self.ammo_shells == 8)
	stuffcmd (self, "cl_pistol_ammo 8\n");
	if (self.ammo_shells == 7)
	stuffcmd (self, "cl_pistol_ammo 7\n");
	if (self.ammo_shells == 6)
	stuffcmd (self, "cl_pistol_ammo 6\n");
	if (self.ammo_shells == 5)
	stuffcmd (self, "cl_pistol_ammo 5\n");
	if (self.ammo_shells == 4)
	stuffcmd (self, "cl_pistol_ammo 4\n");
	if (self.ammo_shells == 3)
	stuffcmd (self, "cl_pistol_ammo 3\n");
	if (self.ammo_shells == 2)
	stuffcmd (self, "cl_pistol_ammo 2\n");
	if (self.ammo_shells == 1)
	stuffcmd (self, "cl_pistol_ammo 1\n");
	if (self.ammo_shells == 0)
	stuffcmd (self, "cl_pistol_ammo 0\n");
	}
	if (self.weapon == IT_SUPER_SHOTGUN)
	{
	stuffcmd (self, "cl_ar_ammo 0\n");
	stuffcmd (self, "cl_pistol_ammo 0\n");
	stuffcmd (self, "cl_needler_ammo 0\n");
	stuffcmd (self, "cl_rocket_ammo 0\n");
	stuffcmd (self, "cl_weaponhud  0\n");
	
	if (self.ammo_shells2 == 6)
	stuffcmd (self, "cl_shotgun_ammo 6\n");
	if (self.ammo_shells2 == 5)
	stuffcmd (self, "cl_shotgun_ammo 5\n");
	if (self.ammo_shells2 == 4)
	stuffcmd (self, "cl_shotgun_ammo 4\n");
	if (self.ammo_shells2 == 3)
	stuffcmd (self, "cl_shotgun_ammo 3\n");
	if (self.ammo_shells2 == 2)
	stuffcmd (self, "cl_shotgun_ammo 2\n");
	if (self.ammo_shells2 == 1)
	stuffcmd (self, "cl_shotgun_ammo 1\n");
	if (self.ammo_shells2 == 0)
	stuffcmd (self, "cl_shotgun_ammo 0\n");
	}
	if (self.weapon == IT_NAILGUN)
	{
	stuffcmd (self, "cl_pistol_ammo 0\n");
	stuffcmd (self, "cl_shotgun_ammo 0\n");
	stuffcmd (self, "cl_needler_ammo 0\n");
	stuffcmd (self, "cl_rocket_ammo 0\n");
	stuffcmd (self, "cl_weaponhud  0\n");

	if (self.ammo_nails == 32)
	stuffcmd (self, "cl_ar_ammo 32\n");
	if (self.ammo_nails == 31)
	stuffcmd (self, "cl_ar_ammo 31\n");
	if (self.ammo_nails == 30)
	stuffcmd (self, "cl_ar_ammo 30\n");
	if (self.ammo_nails == 29)
	stuffcmd (self, "cl_ar_ammo 29\n");
	if (self.ammo_nails == 28)
	stuffcmd (self, "cl_ar_ammo 28\n");
	if (self.ammo_nails == 27)
	stuffcmd (self, "cl_ar_ammo 27\n");
	if (self.ammo_nails == 26)
	stuffcmd (self, "cl_ar_ammo 26\n");
	if (self.ammo_nails == 25)
	stuffcmd (self, "cl_ar_ammo 25\n");
	if (self.ammo_nails == 24)
	stuffcmd (self, "cl_ar_ammo 24\n");
	if (self.ammo_nails == 23)
	stuffcmd (self, "cl_ar_ammo 23\n");
	if (self.ammo_nails == 22)
	stuffcmd (self, "cl_ar_ammo 22\n");
	if (self.ammo_nails == 21)
	stuffcmd (self, "cl_ar_ammo 21\n");
	if (self.ammo_nails == 20)
	stuffcmd (self, "cl_ar_ammo 20\n");
	if (self.ammo_nails == 19)
	stuffcmd (self, "cl_ar_ammo 19\n");
	if (self.ammo_nails == 18)
	stuffcmd (self, "cl_ar_ammo 18\n");
	if (self.ammo_nails == 17)
	stuffcmd (self, "cl_ar_ammo 17\n");
	if (self.ammo_nails == 16)
	stuffcmd (self, "cl_ar_ammo 16\n");
	if (self.ammo_nails == 15)
	stuffcmd (self, "cl_ar_ammo 15\n");
	if (self.ammo_nails == 14)
	stuffcmd (self, "cl_ar_ammo 14\n");
	if (self.ammo_nails == 13)
	stuffcmd (self, "cl_ar_ammo 13\n");
	if (self.ammo_nails == 12)
	stuffcmd (self, "cl_ar_ammo 12\n");
	if (self.ammo_nails == 11)
	stuffcmd (self, "cl_ar_ammo 11\n");
	if (self.ammo_nails == 10)
	stuffcmd (self, "cl_ar_ammo 10\n");
	if (self.ammo_nails == 9)
	stuffcmd (self, "cl_ar_ammo 9\n");
	if (self.ammo_nails == 8)
	stuffcmd (self, "cl_ar_ammo 8\n");
	if (self.ammo_nails == 7)
	stuffcmd (self, "cl_ar_ammo 7\n");
	if (self.ammo_nails == 6)
	stuffcmd (self, "cl_ar_ammo 6\n");
	if (self.ammo_nails == 5)
	stuffcmd (self, "cl_ar_ammo 5\n");
	if (self.ammo_nails == 4)
	stuffcmd (self, "cl_ar_ammo 4\n");
	if (self.ammo_nails == 3)
	stuffcmd (self, "cl_ar_ammo 3\n");
	if (self.ammo_nails == 2)
	stuffcmd (self, "cl_ar_ammo 2\n");
	if (self.ammo_nails == 1)
	stuffcmd (self, "cl_ar_ammo 1\n");
	if (self.ammo_nails == 0)
	stuffcmd (self, "cl_ar_ammo 0\n");
	}	
	if (self.weapon == IT_ROCKET_LAUNCHER)
	{
	stuffcmd (self, "cl_ar_ammo 0\n");	//Turns off other ammo counters
	stuffcmd (self, "cl_pistol_ammo 0\n");
	stuffcmd (self, "cl_needler_ammo 0\n");
	stuffcmd (self, "cl_shotgun_ammo 0\n");
	stuffcmd (self, "cl_weaponhud  0\n");		//Keeps Needler Weapon Icon off
	
	if (self.ammo_rockets == 2)
	stuffcmd (self, "cl_rocket_ammo 2\n");
	if (self.ammo_rockets == 1)
	stuffcmd (self, "cl_rocket_ammo 1\n");
	if (self.ammo_rockets == 0)
	stuffcmd (self, "cl_rocket_ammo 0\n");
	}
	if (self.weapon == IT_LIGHTNING)
	{
	stuffcmd (self, "cl_ar_ammo 0\n");		
	stuffcmd (self, "cl_shotgun_ammo 0\n");
	stuffcmd (self, "cl_needler_ammo 0\n");
	stuffcmd (self, "cl_rocket_ammo 0\n");
	stuffcmd (self, "cl_pistol_ammo 0\n");
	}
	if (self.weapon == IT_AXE)
	{
	stuffcmd (self, "cl_ar_ammo 0\n");		
	stuffcmd (self, "cl_shotgun_ammo 0\n");
	stuffcmd (self, "cl_needler_ammo 0\n");
	stuffcmd (self, "cl_rocket_ammo 0\n");
	stuffcmd (self, "cl_pistol_ammo 0\n");
	}
	if (self.weapon == WEAPON_NEEDLER)
	{
	stuffcmd (self, "cl_weaponhud  1\n");		//Turns needler Icon on.
	stuffcmd (self, "cl_pistol_ammo 0\n");
	stuffcmd (self, "cl_shotgun_ammo 0\n");
	stuffcmd (self, "cl_ar_ammo 0\n");
	stuffcmd (self, "cl_rocket_ammo 0\n");
	
	if (self.ammo_needler == 20)
	stuffcmd (self, "cl_needler_ammo 20\n");
	if (self.ammo_needler == 19)
	stuffcmd (self, "cl_needler_ammo 19\n");
	if (self.ammo_needler == 18)
	stuffcmd (self, "cl_needler_ammo 18\n");
	if (self.ammo_needler == 17)
	stuffcmd (self, "cl_needler_ammo 17\n");
	if (self.ammo_needler == 16)
	stuffcmd (self, "cl_needler_ammo 16\n");
	if (self.ammo_needler == 15)
	stuffcmd (self, "cl_needler_ammo 15\n");
	if (self.ammo_needler == 14)
	stuffcmd (self, "cl_needler_ammo 14\n");
	if (self.ammo_needler == 13)
	stuffcmd (self, "cl_needler_ammo 13\n");
	if (self.ammo_needler == 12)
	stuffcmd (self, "cl_needler_ammo 12\n");
	if (self.ammo_needler == 11)
	stuffcmd (self, "cl_needler_ammo 11\n");
	if (self.ammo_needler == 10)
	stuffcmd (self, "cl_needler_ammo 10\n");
	if (self.ammo_needler == 9)
	stuffcmd (self, "cl_needler_ammo 9\n");
	if (self.ammo_needler == 8)
	stuffcmd (self, "cl_needler_ammo 8\n");
	if (self.ammo_needler == 7)
	stuffcmd (self, "cl_needler_ammo 7\n");
	if (self.ammo_needler == 6)
	stuffcmd (self, "cl_needler_ammo 6\n");
	if (self.ammo_needler == 5)
	stuffcmd (self, "cl_needler_ammo 5\n");
	if (self.ammo_needler == 4)
	stuffcmd (self, "cl_needler_ammo 4\n");
	if (self.ammo_needler == 3)
	stuffcmd (self, "cl_needler_ammo 3\n");
	if (self.ammo_needler == 2)
	stuffcmd (self, "cl_needler_ammo 2\n");
	if (self.ammo_needler == 1)
	stuffcmd (self, "cl_needler_ammo 1\n");
	if (self.ammo_needler == 0)
	stuffcmd (self, "cl_needler_ammo 0\n");
	}
	if (self.weapon == WEAPON_PRIFLE)
	{
	stuffcmd (self, "cl_ar_ammo 0\n");		
	stuffcmd (self, "cl_shotgun_ammo 0\n");
	stuffcmd (self, "cl_needler_ammo 0\n");
	stuffcmd (self, "cl_rocket_ammo 0\n");
	stuffcmd (self, "cl_pistol_ammo 0\n");
	}
};
/*
==========================================

Gernade counter for the HUD. Displays a players Number 
Of nades.

==========================================
*/
void() NadeCounter =
{
if (self.selnade == GRENADE_REGULAR)
	{
	stuffcmd (self, "cl_plasmanade 2\n");
	if (self.nade_lives == 4)
	stuffcmd (self, "cl_nadenum 5\n");
	if (self.nade_lives == 3)
	stuffcmd (self, "cl_nadenum 4\n");
	if (self.nade_lives == 2)
	stuffcmd (self, "cl_nadenum 3\n");
	if (self.nade_lives == 1)
	stuffcmd (self, "cl_nadenum 2\n");
	if (self.nade_lives == 0)
	stuffcmd (self, "cl_nadenum 1\n");
	}
else if (self.selnade == GRENADE_STICKY)
	{
	stuffcmd (self, "cl_plasmanade 1\n");
	if (self.plasma_lives == 4)
	stuffcmd (self, "cl_nadenum 5\n");
	if (self.plasma_lives == 3)
	stuffcmd (self, "cl_nadenum 4\n");
	if (self.plasma_lives == 2)
	stuffcmd (self, "cl_nadenum 3\n");
	if (self.plasma_lives == 1)
	stuffcmd (self, "cl_nadenum 2\n");
	if (self.plasma_lives == 0)
	stuffcmd (self, "cl_nadenum 1\n");
	}


};