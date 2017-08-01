/*
*/
void (entity targ, entity inflictor, entity attacker, float damage, INTEGER mod) T_Damage;
void () player_run;
void(entity inflictor, entity attacker, float damage, float radius, entity ignore, INTEGER mod) T_RadiusDamage;
void(vector org, float damage) SpawnBlood;
void() SuperDamageSound;
void () player_reload1;

// called by worldspawn
void() W_Precache =
{
	precache_sound ("weapons/r_exp3.wav");  // new rocket explosion
	precache_sound ("weapons/rocket1i.wav");        // spike gun
	precache_sound ("weapons/sgun1.wav");
	precache_sound ("weapons/guncock.wav"); // player shotgun
	precache_sound ("weapons/ric1.wav");    // ricochet (used in c code)
	precache_sound ("weapons/ric2.wav");    // ricochet (used in c code)
	precache_sound ("weapons/ric3.wav");    // ricochet (used in c code)
	precache_sound ("weapons/spike2.wav");  // super spikes
	precache_sound ("weapons/tink1.wav");   // spikes tink (used in c code)
	precache_sound ("weapons/grenade.wav"); // grenade launcher
	precache_sound ("weapons/bounce.wav");          // grenade bounce
	precache_sound ("weapons/shotgn2.wav"); // super shotgun

	// Solitude precaches
	
	// Weapons (first-person)
	precache_model ("progs/v_shotgun.mdl");
	precache_model ("progs/v_rocket.mdl");
	precache_model ("progs/v_uzi.mdl");
	precache_model ("progs/v_sniper.mdl");
	precache_model ("progs/v_plpist.mdl");
	precache_model ("progs/v_needle.mdl");
	precache_model ("progs/v_plrifle.mdl");
	
	// Grenades
	precache_model ("progs/fraggren.mdl");
	precache_model ("progs/plasgren.mdl");
	
	// Dropped weapons
	precache_model ("progs/g_shot.mdl");
	precache_model ("progs/g_pistol.mdl");
	precache_model ("progs/g_nail.mdl");
	precache_model ("progs/g_uzi.mdl");
	precache_model ("progs/g_rocket.mdl");
	precache_model ("progs/g_sniper.mdl");
	precache_model ("progs/g_axe.mdl");		// sword
	precache_model ("progs/g_needler.mdl");
	precache_model ("progs/g_plpist.mdl");	
	precache_model ("progs/g_plrifl.mdl");
	
	// projectiles
	precache_model ("progs/PL_BULL.spr");
	precache_model ("progs/minirocket.mdl");
	precache_model ("progs/needproy.mdl");		// Needler Projectile
	precache_model ("progs/needpro2.mdl");		// Embedded needle
	
};

#define crandom() (2*(random()-0.5))

// The weapon the player spawns with
void () W_StartWeapon =
{
	self.items = WEAPON_PISTOL;
	self.ammo_shells = W_GetMaxClip(self.weapon, 1);
	self.exshells = 999;		// fun with bots :D
	self.currentammo = W_GetMaxClip(self.weapon, 1);
	
	W_UpdateAmmoCounts(self);
};
	
/*
Ammo update functions
*/
// xavior: FIXME instead of using W_SetCurrentAmmo!
void(entity ent) W_UpdateAmmoCounts =
{
	// solitude
	switch (ent.weapon)
	{
		case WEAPON_PISTOL:
			ent.currentammo = ent.ammo_shells;
			ent.armorvalue = ent.exshells;
			break;
		case WEAPON_SHOT:
			ent.currentammo = ent.ammo_shells2;
			ent.armorvalue = ent.exshells2;
			break;
		case WEAPON_AR:
			ent.currentammo = ent.ammo_nails;
			ent.armorvalue = ent.exnails;
			break;
		case WEAPON_UZI:
			ent.currentammo = ent.ammo_hshells;
			ent.armorvalue = ent.exhshells;
			break;
		case WEAPON_RL:
			ent.currentammo = ent.ammo_rockets;
			ent.armorvalue = ent.exrockets;
			break;
		case WEAPON_SNIPER:
			ent.currentammo = ent.ammo_sniper;
			ent.armorvalue = ent.exsniper;
			break;
		case WEAPON_PPISTOL:
			ent.currentammo = ent.ammo_ppistol;
			ent.armorvalue = ent.exppistol;
			break;
		case WEAPON_SWORD:
			ent.currentammo = ent.ammo_sword;
			ent.armorvalue = ent.exsword;
			break;
		case WEAPON_NEEDLER:
			ent.currentammo = ent.ammo_needler;
			ent.armorvalue = ent.exneedler;
			break;
		case WEAPON_PRIFLE:
			ent.currentammo = ent.ammo_prifle;
			ent.armorvalue = ent.exprifle;
			break;
		default:
			ent.currentammo = 12;
			break;
	}
};

// Damage per individual bullets
float (float t_wep) W_BulletDamage =
{
	switch (t_wep) {
		case WEAPON_PISTOL:
			return 15;
			break;
		case WEAPON_SHOT:
			return 8;
			break;
		case WEAPON_AR:
			return 7.5;
			break;
		case WEAPON_UZI:
			return 4.8;
			break;
		default:
			return 4;
			break;
	}
	return 4;
};

// cliptype 1 = max size per clip
// cliptype 0 = max extra ammo the player can carry
float (float wep, float cliptype) W_GetMaxClip =
{
	// solitude
	switch (wep)
	{
		case WEAPON_PISTOL:
			if (cliptype)
				return 12;
			else
				return 90;
			break;
		case WEAPON_SHOT:
			if (cliptype)
				return 6;
			else
				return 30;
			break;
		case WEAPON_AR:
			if (cliptype)
				return 60;
			else
				return 90;
			break;
		case WEAPON_UZI:
			if (cliptype)
				return 45;
			else
				return 90;
			break;
		case WEAPON_RL:
			if (cliptype)
				return 2;
			else
				return 90;
			break;
		case WEAPON_SNIPER:
			if (cliptype)
				return 5;
			else
				return 90;
			break;
		case WEAPON_PPISTOL:
			if (cliptype)
				return 100;
			else
				return 90;
			break;
		case WEAPON_SWORD:
			if (cliptype)
				return 0;		// should be 0 - infinite
			else
				return 0;
			break;
		case WEAPON_NEEDLER:
			if (cliptype)
				return 20;
			else
				return 90;
			break;
		case WEAPON_PRIFLE:
			if (cliptype)
				return 100;
			else
				return 90;
			break;
		default:
			if (cliptype)
				return 1;
			else
				return 90;
			break;
	}
	return 1;
};

float (entity ent) W_CanFire =
{
	switch (ent.weapon)
	{
		case IT_AXE:
			return TRUE;
			break;
		case WEAPON_PISTOL:
			if (ent.ammo_shells <= 0)
				return FALSE;
			break;
		case WEAPON_SHOT:
			if (ent.ammo_shells2 <= 0)
				return FALSE;
			break;
		case WEAPON_AR:
			if (ent.ammo_nails <= 0)
				return FALSE;
			break;
		case WEAPON_UZI:
			if (ent.ammo_hshells <= 0)
				return FALSE;
			break;
		case WEAPON_RL:
			if (ent.ammo_rockets <= 0)
				return FALSE;
			break;
		case WEAPON_SNIPER:
			if (ent.ammo_sniper <= 0)
				return FALSE;
			break;
		case WEAPON_PPISTOL:
			if (ent.ammo_ppistol <= 0)
				return FALSE;
			break;
		case WEAPON_SWORD:
			if (ent.ammo_sword <= 0)
				return FALSE;
			break;
		case WEAPON_NEEDLER:
			if (ent.ammo_needler <= 0)
				return FALSE;
			break;
		case WEAPON_PRIFLE:
			if (ent.ammo_prifle <= 0)
				return FALSE;
			break;
		default:
			return TRUE;
			break;
	}
	return TRUE;
};

void ( float famt ) Set_FOV =
{
	stuffcmd( self, "fov " );
	stuffcmd( self, ftos( famt ) );
	stuffcmd( self, "\n" );
};

void () WeaponZoom =
{
	float tozoom;

	if (self.health < 1)
		return;
	
	switch (self.weapon)
	{
		case WEAPON_SNIPER:
			if (self.pfov < FOV_DEFAULT)
				tozoom = 15;
			else
				tozoom = 45;
			break;
		case WEAPON_SWORD:
			tozoom = FOV_DEFAULT;		// no zoom for sword
			break;
		default:
			tozoom = 45;
			break;
	}
	if (self.pfov == tozoom)
		tozoom = FOV_DEFAULT;
	
	Set_FOV( tozoom );
	self.pfov = tozoom;
};
	
/*
================
W_FireAxe
================
*/
void(float lunge) W_FireSword =
{
	local   vector  source;
	local   vector  org;

	makevectors (self.v_angle);
	source = self.origin + '0 0 16';
	traceline (source, source + v_forward*64, FALSE, self);

	if (trace_fraction == 1.0)
		return;
	
	org = trace_endpos - v_forward*4;

	if (trace_ent.takedamage)
	{
		SpawnBlood (org, 20);
		if (lunge)
			T_Damage (trace_ent, self, self, 150, MOD_AXE);
		else
			T_Damage (trace_ent, self, self, 75, MOD_AXE);

	}
	else
	{       // hit wall

		sound (self, CHAN_WEAPON, "player/axhit2.wav", 1, ATTN_NORM);

		TE_gunshot(org);
	}
};


//============================================================================

/*
================
SpawnMeatSpray
================
*/
void(vector org, vector vel) SpawnMeatSpray =
{
	local   entity missile;

	missile = spawn ();
	missile.owner = self;
	missile.movetype = MOVETYPE_BOUNCE;
	missile.solid = SOLID_NOT;

	makevectors (self.angles);

	missile.velocity = vel;
	missile.velocity_z = missile.velocity_z + 250 + 50*random();

	missile.avelocity = '3000 1000 2000';
	
// set missile duration
	missile.nextthink = time + 1;
	missile.think = SUB_Remove;

	setmodel (missile, "progs/zom_gib.mdl");
	setsize (missile, '0 0 0', '0 0 0');            
	setorigin (missile, org);
};

/*
==============================================================================

MULTI-DAMAGE

Collects multiple small damages into a single damage

==============================================================================
*/

entity  multi_ent;
float   multi_damage;
INTEGER multi_mod;

vector  blood_org;
float   blood_count;

vector  puff_org;
float   puff_count;

void() ClearMultiDamage =
{
	multi_ent = world;
	multi_damage = 0;
	blood_count = 0;
	puff_count = 0;
	multi_mod = MOD_NONE;
};

void() ApplyMultiDamage =
{
	if (!multi_ent)
		return;
	T_Damage (multi_ent, self, self, multi_damage, multi_mod);
};

void(entity hit, float damage, INTEGER mod) AddMultiDamage =
{
	if (!hit)
		return;
	
	if (hit != multi_ent || mod != multi_mod)
	{
		ApplyMultiDamage ();
		multi_damage = damage;
		multi_ent = hit;
	}
	else
		multi_damage = multi_damage + damage;
};

void() Multi_Finish =
{
	if (puff_count)
		TE_gunshot(puff_org);

	if (blood_count)
		SpawnBlood(blood_org, blood_count);
};

/*
==============================================================================
BULLETS
==============================================================================
*/

/*
================
TraceAttack
================
*/
void(float damage, vector dir, INTEGER mod) TraceAttack =
{
	local   vector  vel, org;
	
	vel = normalize(dir + v_up*crandom() + v_right*crandom());
	vel = vel + 2*trace_plane_normal;
	vel = vel * 200;

	org = trace_endpos - dir*4;

	if (trace_ent.takedamage)
	{
		blood_count = blood_count + 1;
		blood_org = org;
		AddMultiDamage (trace_ent, damage, mod);
	}
	else
	{
		puff_count = puff_count + 1;
	}
};

/*
================
FireBullets

Used by shotgun, super shotgun, and enemy soldier firing
Go to the trouble of combining multiple pellets into a single damage call.
================
*/
void(float shotcount, vector dir, vector spread, INTEGER mod) FireBullets =
{
	local   vector direction;
	local   vector  src;
	
	makevectors(self.v_angle);

	src = self.origin + v_forward*10;
	src_z = self.absmin_z + self.size_z * 0.7;

	ClearMultiDamage ();

	traceline (src, src + dir*2048, FALSE, self);
	puff_org = trace_endpos - dir*4;

	while (shotcount > 0)
	{
		direction = dir + crandom()*spread_x*v_right + crandom()*spread_y*v_up;
		traceline (src, src + direction*2048, FALSE, self);
		if (trace_fraction != 1.0)
			TraceAttack (W_BulletDamage(self.weapon), direction, mod);

		shotcount = shotcount - 1;
	}
	ApplyMultiDamage ();
	Multi_Finish ();
};

/*
================
W_FirePistol
================
*/
void() W_FirePistol =
{
	local vector dir;

	sound (self, CHAN_WEAPON, "weapons/guncock.wav", 1, ATTN_NORM); 

	VK_smallkick(self);
	
	self.ammo_shells -= 1;
	W_UpdateAmmoCounts(self);

	dir = aim (self, 100000);
	FireBullets (1, dir, '0 0 0', MOD_SHOTGUN);
};

void () Cooldown_Think =
{
	local entity oself;
	oself = self;

	if (self.owner == world || self.owner.classname != "player") {
		remove(self);
		return;
	}
	if (self.owner.items & WEAPON_PPISTOL) {
		if (self.owner.exppistol > 0) {
			self.owner.exppistol -= 1;
			W_UpdateAmmoCounts(self.owner);
		}
	}
	if (self.owner.items & WEAPON_PRIFLE) {
		if (self.owner.exprifle > 0) {
			self.owner.exprifle -= 1;
			W_UpdateAmmoCounts(self.owner);
		}
	}
	
	self.nextthink = time + .05;
};

void ( float t_weap, float w_heat ) W_AddHeat =
{
	if (self.pp_cooldown == world) {
		self.pp_cooldown = spawn();
		self.pp_cooldown.owner = self;
		self.pp_cooldown.weapon = t_weap;
		self.pp_cooldown.think = Cooldown_Think;
		self.pp_cooldown.nextthink = time + .05;
	}

	switch ( t_weap ) {
		case WEAPON_PPISTOL:
			self.exppistol += w_heat;
			break;
		case WEAPON_PRIFLE:
			self.exprifle += w_heat;
			break;
	}
};

void () Plasma_Diffuse =
{
	self.velocity = '0 0 0';
	self.think = SUB_Remove;
	self.nextthink = time + .3;
	self.touch = SUB_Null;
	if (other.classname == "player") {
		T_Damage (other, self, self.owner, 13*self.health, MOD_SOLITUDE);
		self.nextthink = time + .15;
	}
};

void( float w_heat ) W_FirePPistol =
{
	local entity plasma;
	local float ptake;
	
	sound (self, CHAN_WEAPON, "weapons/guncock.wav", 1, ATTN_NORM); 

	//VK_smallkick(self);
	
	if (w_heat < 3)
		ptake = 1;
	else if (w_heat < 7)
		ptake = 2;
	else if (w_heat < 12)
		ptake = 3;
	else if (w_heat < 15)
		ptake = 4;
	else
		ptake = 6;
		
	self.ammo_ppistol -= ptake;
	if (self.ammo_ppistol < 0)
		self.ammo_ppistol = 0;
	W_UpdateAmmoCounts(self);

	plasma = spawn ();
	plasma.health = ptake;
	plasma.owner = self;
	plasma.movetype = 9;
	plasma.solid = 2;
	makevectors (self.v_angle);
	plasma.velocity = v_forward;
	plasma.velocity = (plasma.velocity * 5000);			// Note: needs sv_maxvelocity set to something like 10,000 at least!
	plasma.angles = vectoangles (plasma.velocity);
	plasma.touch = Plasma_Diffuse;
	plasma.nextthink = (time + 5);
	plasma.think = Plasma_Diffuse;
	setmodel (plasma, "progs/PL_BULL.spr");
	setsize (plasma, '0 0 0', '0 0 0');
	setorigin (plasma, ((self.origin + (v_forward * 8)) + '0 0 16'));  //setorigin (plasma, ((self.origin + (v_forward * 8)) + '0 0 16'));
	
	if (ptake > 5)
		ptake = 10;
	
	W_AddHeat ( self.weapon, ptake * 10);
};

void () W_FireShotgun =
{
	local vector dir;

	sound (self, CHAN_WEAPON, "weapons/shotgn2.wav", WEAPON_SHOTGUN, ATTN_NORM);
	self.punchangle_x = CONTENT_EMPTY;
	self.ammo_shells2 -= 1;
	self.currentammo -= 1;
	dir = aim (self, 100000);
	FireBullets (10, dir, '0.15 0.15 0', MOD_SOLITUDE);
	//FireBullets (WEAPON_SHOTGUN, dir, '0.07 0.07 0', MOD_SOLITUDE);
};

void () W_FireAR =
{
	local vector dir;

	sound (self, CHAN_WEAPON, "weapons/shotgn2.wav", WEAPON_SHOTGUN, ATTN_NORM);
	self.punchangle_x = CONTENT_EMPTY;
	self.ammo_nails -= 1;
	self.currentammo -= 1;
	dir = aim (self, 100000);
	FireBullets (1, dir, '0.07 0.07 0', MOD_SOLITUDE);
};

void (float int) W_FireSpikes;
void() W_FireUzi =
{
	local vector dir;

	sound (self, CHAN_WEAPON, "weapons/shotgn2.wav", WEAPON_SHOTGUN, ATTN_NORM);
	self.punchangle_x = CONTENT_EMPTY;
	self.ammo_hshells -= 1;
	self.currentammo = self.ammo_hshells;
	dir = aim (self, 100000);
	FireBullets (1, dir, '0.07 0.07 0', MOD_SOLITUDE);
/*
	VK_smallkick(self);
	PRJ_FireProjectile(self,
		"progs/s_spike.mdl",
		self.origin + '0 0 16',
		aim(self, 1000) * 1000,
		PE_SUPERSPIKE,
		18,
		MOD_SUPERSPIKE,
		6);
*/
};

void () W_FireNail2 =
{
	local vector dir;

	sound (self, CHAN_WEAPON, "weapons/shotgn2.wav", WEAPON_SHOTGUN, ATTN_NORM);
	self.punchangle_x = CONTENT_EMPTY;
	self.ammo_shells2 = (self.ammo_shells2 - WEAPON_SHOTGUN);
	self.currentammo = (self.ammo_shells2 - WEAPON_SHOTGUN);
	dir = aim (self, 100000);
	FireBullets (WEAPON_SHOTGUN, dir, '0.07 0.07 0', MOD_SOLITUDE);
};

void () SB_Touch =
{
	local vector p_a, p_b;
	local float zdif;
	
	self.velocity = '0 0 0';
	if (other.takedamage) {
		p_a_z = self.origin_z;
		
		p_b_z = other.origin_z;
		
		zdif = vlen(p_a - p_b);
		//_bprint(ftos(zdif),"\n");
		if (zdif > 20)
			T_Damage (other, self, self.owner, 150, MOD_SOLITUDE);
		else
			T_Damage (other, self, self.owner, 70, MOD_SOLITUDE);
	}
	else
	{
		puff_org = self.origin;
	}
	remove(self);
};

void() W_FireSniper =
{
	local entity fshell;

	sound (self, CHAN_WEAPON, "weapons/guncock.wav", 1, ATTN_NORM); 

	VK_smallkick(self);
	
	self.ammo_sniper -= 1;
	W_UpdateAmmoCounts(self);
	

	fshell = spawn ();
	fshell.owner = self;
	fshell.movetype = 9;
	fshell.solid = 2;
	makevectors (self.v_angle);
	fshell.velocity = v_forward;
	fshell.velocity = (fshell.velocity * 999999);			// Note: needs sv_maxvelocity set to something like 10,000 at least!
	fshell.angles = vectoangles (fshell.velocity);
	fshell.touch = SB_Touch;
	fshell.nextthink = (time + 5);
	fshell.think = SUB_Remove;
	setmodel (fshell, "progs/minirocket.mdl");
	setsize (fshell, '0 0 0', '0 0 0');
	setorigin (fshell, ((self.origin + (v_forward * 8)) + '0 0 16'));  //setorigin (fshell, ((self.origin + (v_forward * 8)) + '0 0 16'));
};

void () NeedleExplode =
{
	self.enemy.needles -= 1;
	T_Damage (self.enemy, self, self.owner, 15, MOD_SOLITUDE);
	WriteByte (MSG_BROADCAST, SVC_TEMPENTITY);
	WriteByte (MSG_BROADCAST, TE_EXPLOSION);
	WriteCoord (MSG_BROADCAST, self.origin_x);
	WriteCoord (MSG_BROADCAST, self.origin_y);
	WriteCoord (MSG_BROADCAST, self.origin_z);
	remove(self);
};

void () NeedlePreExplode =
{
	local vector m_height;
	m_height_x = self.armorvalue;
	
	if (self.enemy.health <= 0) {
		remove(self);
		return;
	}
	
	if (time > self.health) {
		NeedleExplode();
		return;
	}
	
	self.origin = self.enemy.origin + m_height;

	self.nextthink = time + .02;
};

void ( entity f_plyr, entity t_plyr, float at_height ) Add_Needle =
{
	local entity needle;
	local float f_p_height;
	f_p_height = at_height - t_plyr.origin_x;
	
	if (other == world) {
		_bprint( "Add_Needle: Cannot assign to world! FIX!!\n");
		return;
	}
	
	if (other.health <= 0)
		return;
		
	t_plyr.needles += 1;
		
	if (t_plyr.needles >= 7) {
		t_plyr.needles -= 7;
		T_Damage (t_plyr, self, f_plyr, 150, MOD_SOLITUDE);
		WriteByte (MSG_BROADCAST, SVC_TEMPENTITY);
		WriteByte (MSG_BROADCAST, TE_EXPLOSION);
		WriteCoord (MSG_BROADCAST, self.origin_x);
		WriteCoord (MSG_BROADCAST, self.origin_y);
		WriteCoord (MSG_BROADCAST, self.origin_z);
		remove(self);
		return;
	}
		
	needle = spawn();
	needle.classname = "needle";
	needle.touch = SUB_Null;
	needle.solid = SOLID_NOT;
	needle.movetype = MOVETYPE_FLY;
	needle.health = time + 3;
	needle.armorvalue = f_p_height;
	needle.enemy = t_plyr;
	needle.owner = f_plyr;
	setmodel (needle, "progs/needpro2.mdl");
	needle.think = NeedlePreExplode;
	needle.nextthink = time;
};


vector(entity proj) bounce_off_wall =		// returns the velocity for bouncing off walls
{
	local vector vec;
	local float backoff, change;

// get the trace_plane_normal of the surface we hit
	makevectors (proj.angles);
	v_forward_z = v_forward_z * -1;
	traceline (proj.origin, proj.origin + v_forward*64, FALSE, proj);

	if (trace_fraction == 1)
		return proj.velocity;

// the entity's velocity is not what we want, so set default
	proj.velocity = v_forward * 500;//proj.old_velocity;

// calculate dot product
	backoff = (proj.velocity * trace_plane_normal);
	backoff = backoff * 1.5;

// finish
	change = trace_plane_normal_x * backoff;
	vec_x = proj.velocity_x - change;

	if (vec_x > -0.1 && vec_x < 0.1)
		vec_x = 0;

	change = trace_plane_normal_y * backoff;
	vec_y = proj.velocity_y - change;

	if (vec_y > -0.1 && vec_y < 0.1)
		vec_y = 0;

	change = trace_plane_normal_z * backoff;
	vec_z = proj.velocity_z - change;

	if (vec_z > -0.1 && vec_z < 0.1)
		vec_z = 0;

// set correct angles of our new velocity
	proj.angles = vectoangles (vec);

	// this is required to make downward slopes not stop the projectile
	proj.flags = proj.flags - ( proj.flags & FL_ONGROUND );

	return vec;
}

void () bounce_a =
{
	self.velocity = bounce_off_wall( self );
	
	self.nextthink = (time + 0.2);
	self.think = NeedlerHome;
};

void () Bounce_Off_Walls =
{
	self.nextthink = time;
	self.think = bounce_a;

	if (self.velocity == '0 0 0')
		remove (self);
};


void () Needler_Touch =
{
	if (other.takedamage != FALSE && other.health > 0) {
		T_Damage (other, self, self.owner, 5, MOD_SOLITUDE);	
		Add_Needle(self.owner, other, self.origin_x);
	}
	else if (self.lives > 0) {
		Bounce_Off_Walls ();
		self.lives -= 1;
		return;
	}
	
	remove(self);
};

void() NeedlerHome =
{
	local vector dir, vtemp, wantdir;
	local entity te;
	local float maxmove;
	maxmove = 55;		// maximum xyz value we're allowed to change in mid-air

	if (self.enemy != world && self.enemy.health > 0) {
		vtemp = (self.enemy.origin + '0 0 10');
		dir = normalize ((vtemp - self.origin));
		wantdir = (dir * 550);
		wantdir_x = wantdir_x - self.velocity_x;
		if (wantdir_x > maxmove)
			wantdir_x = maxmove;
		if (wantdir_x < -maxmove)
			wantdir_x = -maxmove;
		wantdir_y = wantdir_y - self.velocity_y;
		if (wantdir_y > maxmove)
			wantdir_y = maxmove;
		if (wantdir_y < -maxmove)
			wantdir_y = -maxmove;
		wantdir_z = wantdir_z - self.velocity_z;
		if (wantdir_z > maxmove)
			wantdir_z = maxmove;
		if (wantdir_z < -maxmove)
			wantdir_z = -maxmove;
		

		self.velocity += wantdir;//(dir * 550);
	}
	else {
		te = findradius(self.origin, 950);
		while (te)
		{
			if ( (te.classname == "player" || te.flags & FL_MONSTER) && te.health > 0 && te != self.owner)
			{
				self.enemy = te;
				//bprint("found enemy!\n");
			}
			te = te.chain;
		}
	}
	self.angles = vectoangles (self.velocity);
	
	self.nextthink = (time + 0.5);
	self.think = NeedlerHome;
};
	
void() W_FireNeedler =
{
	local entity fshell;
	local vector spread;

	//sound (self, CHAN_WEAPON, "weapons/guncock.wav", 1, ATTN_NORM); 

	spread = '0.04 0.04 0';
	
	VK_smallkick(self);
	
	self.needler_heat += 1;
	self.ammo_needler -= 1;
	W_UpdateAmmoCounts(self);
	

	fshell = spawn ();
	fshell.owner = self;
	fshell.movetype = 9;
	fshell.solid = 2;
	makevectors (self.v_angle);
	fshell.velocity = v_forward + crandom()*spread_x*v_right + crandom()*spread_y*v_up;
	fshell.velocity = (fshell.velocity * 550);
	fshell.angles = vectoangles (fshell.velocity);
	fshell.touch = Needler_Touch;
	fshell.armorvalue = time + 15;		// amount of time the needler projectile should stay alive
	fshell.nextthink = (time + 0.2);
	fshell.think = NeedlerHome;
	fshell.lives = 1;					// number of times the needle will bounce off walls
	setmodel (fshell, "progs/needproy.mdl");
	setsize (fshell, '0 0 0', '0 0 0');
	setorigin (fshell, ((self.origin + (v_forward * 8)) + '0 0 16'));  //setorigin (fshell, ((self.origin + (v_forward * 8)) + '0 0 16'));
}

void () W_FirePlasmaRifle =
{
	local entity plasma;
	local vector spread;
	spread = '0.02 0.02 0';
	
	self.prifle_heat += 1;
	//sound (self, CHAN_WEAPON, "weapons/guncock.wav", 1, ATTN_NORM); 

	
	//VK_smallkick(self);
		
	self.ammo_prifle -= 1;
	if (self.ammo_prifle < 0)
		self.ammo_prifle = 0;
	W_UpdateAmmoCounts(self);

	plasma = spawn ();
	plasma.health = 1;
	plasma.owner = self;
	plasma.movetype = 9;
	plasma.solid = 2;
	makevectors (self.v_angle);
	plasma.velocity =  v_forward + crandom()*spread_x*v_right + crandom()*spread_y*v_up;
	plasma.velocity = (plasma.velocity * 6000);			// Note: needs sv_maxvelocity set to something like 10,000 at least!
	plasma.angles = vectoangles (plasma.velocity);
	plasma.touch = Plasma_Diffuse;
	plasma.nextthink = (time + 5);
	plasma.think = Plasma_Diffuse;
	setmodel (plasma, "progs/PL_BULL.spr");
	setsize (plasma, '0 0 0', '0 0 0');
	setorigin (plasma, ((self.origin + (v_forward * 8)) + '0 0 16'));  //setorigin (plasma, ((self.origin + (v_forward * 8)) + '0 0 16'));
	
	W_AddHeat ( self.weapon, 10);
};

float(vector veca, vector vecb) crossproduct = 
{
	local float result;
	result = veca_x * vecb_y - vecb_x * veca_y;
	return result;
};

void () W_Melee =
{
	local vector source;
	local vector org;
	
	local vector def;

	makevectors (self.v_angle);
	source = (self.origin + '0 0 16');
	traceline (source, (source + (v_forward * IT_LIGHTNING)), FALSE, self);
	if ((trace_fraction == WEAPON_SHOTGUN))
	{
		self.punchangle_x = CONTENT_EMPTY;
		return;
	}
	self.punchangle_x = CONTENT_SOLID;
	org = (trace_endpos - (v_forward * WEAPON_SPIKES));
	
	makevectors (trace_ent.v_angle);
	def = v_right;
	
	if (trace_ent.takedamage)
	{
		trace_ent.axhitme = WEAPON_SHOTGUN;
		SpawnBlood (org, 20);
		
		makevectors (self.v_angle);
		if (crossproduct (def, v_forward) > 0)
			T_Damage (trace_ent, self, self, 50, MOD_SOLITUDE);		// more damage for a blow to the back
		else
			T_Damage (trace_ent, self, self, 20, MOD_SOLITUDE);
	}
	else
	{
		//sound (self, CHAN_WEAPON, "player/gib.wav", WEAPON_SHOTGUN, ATTN_NORM);		// gib sound for hitting a wall? :D
		WriteByte (MSG_BROADCAST, SVC_TEMPENTITY);
		WriteByte (MSG_BROADCAST, TE_GUNSHOT);
		WriteCoord (MSG_BROADCAST, org_x);
		WriteCoord (MSG_BROADCAST, org_y);
		WriteCoord (MSG_BROADCAST, org_z);
	}
};

/*
==============================================================================

ROCKETS

==============================================================================
*/

/*
================
W_FireRocket
================
*/
void() W_FireRocket =
{
	self.ammo_rockets -= 1;
	W_UpdateAmmoCounts(self);
	
	sound (self, CHAN_WEAPON, "weapons/sgun1.wav", 1, ATTN_NORM);

	VK_smallkick(self);
	PRJ_FireProjectile(self, 
		"progs/missile.mdl", 
		self.origin + v_forward*8 + '0 0 16', 
		aim(self, 1000) * 1000,
		PE_EXPLOSION, 
		100+random()*20, 
		MOD_ROCKET, 
		5);
	PRJ_SetRadiusDamage(120, 160, MOD_ROCKETRADIUS);
};

/*
===============================================================================
LIGHTNING
===============================================================================
*/

void(entity from, float damage, INTEGER lmod) LightningHit =
{
	TE_lightningblood(trace_endpos);

	T_Damage (trace_ent, from, from, damage, lmod);
};

/*
=================
LightningDamage
=================
*/
void(vector p1, vector p2, entity from, float damage, INTEGER lmod) LightningDamage =
{
	local entity            e1, e2;
	local vector            f;
	
	f = p2 - p1;
	f = normalize(f);
	f_x = 0 - f_y;
	f_y = f_x;
	f_z = 0;
	f = f*16;

	e1 = e2 = world;

	traceline (p1, p2, FALSE, self);

	if (trace_ent.takedamage)
		LightningHit (from, damage, lmod);
	e1 = trace_ent;

	traceline (p1 + f, p2 + f, FALSE, self);
	if (trace_ent != e1 && trace_ent.takedamage)
		LightningHit (from, damage, lmod);
	e2 = trace_ent;

	traceline (p1 - f, p2 - f, FALSE, self);
	if (trace_ent != e1 && trace_ent != e2 && trace_ent.takedamage)
		LightningHit (from, damage, lmod);
};


void() W_FireLightning =
{
	local   vector          org;
	local   float           cells;
	local   INTEGER		expmod;

	if (self.ammo_cells_real < 1)
	{
		W_WeaponSwitch (W_BestWeapon ());
		return;
	}

// explode if under water
	if (self.waterlevel > 1)
	{
		if (deathmatch > 3)
		{
			if (random() <= 0.5)
			{
				T_Damage (self, self, self.owner, 4000, MOD_SELFWATER);
				return;
			}
		}

		cells = self.ammo_cells_real;
		self.ammo_cells_real = 0;
		W_WeaponSwitch (W_BestWeapon ());
		expmod = MOD_SHAFTWATER;
		if (self.watertype == CONTENT_SLIME)
			expmod = MOD_SHAFTSLIME;
		else if (self.watertype == CONTENT_LAVA)
			expmod = MOD_SHAFTLAVA;
		T_RadiusDamage (self, self, 35*cells, 40+35*cells, world, expmod);
		return;
	}

	if (self.lightning_sound < time)
	{
		sound (self, CHAN_WEAPON, "weapons/lhit.wav", 1, ATTN_NORM);
		self.lightning_sound = time + 0.6;
	}
	VK_smallkick(self);

	if (deathmatch != 4)
	{
		self.ammo_cells_real -= 1;
		W_UpdateAmmoCounts(self);
	}

	org = self.origin + '0 0 16';
	
	traceline (org, org + v_forward*600, TRUE, self);

	TE_lightning2(self, org, trace_endpos);

	LightningDamage (self.origin, trace_endpos + v_forward*4, self, 30, MOD_SHAFT);
};

void () GrenadeExplode =
{
	T_RadiusDamage (self, self.owner, 120, 120, world, MOD_SOLITUDE);
	WriteByte (MSG_BROADCAST, SVC_TEMPENTITY);
	WriteByte (MSG_BROADCAST, TE_EXPLOSION);
	WriteCoord (MSG_BROADCAST, self.origin_x);
	WriteCoord (MSG_BROADCAST, self.origin_y);
	WriteCoord (MSG_BROADCAST, self.origin_z);
	remove(self);
	//BecomeExplosion ();
};

void () Stick =
{
	if (((self.enemy != world) && (self.enemy.health > WEAPON_SHOTGUN)))
	{
		self.think = Stick;
		self.touch = Stick;
		self.origin = self.enemy.origin;
	}
	else
	{
		GrenadeExplode ();
	}
	self.exshells = (self.exshells + WEAPON_SHOTGUN);
	if ((self.exshells > 15))
	{
		GrenadeExplode ();
	}
	self.nextthink = (time + 0.1);
};

void () StickyTouch =
{
	if (((other == self.owner) || (other == world)))
	{
		return;
	}
	self.exshells = MSG_BROADCAST;
	self.movetype = MOVETYPE_NOCLIP;
	self.think = Stick;
	self.touch = Stick;
	self.nextthink = (time + 0.1);
	self.avelocity = VEC_ORIGIN;
	self.velocity = VEC_ORIGIN;
	self.enemy = other;
};

/*
================
W_FireGrenade
================
*/
void() W_FireGrenade =
{
	local vector vel;

	if (deathmatch != 4)
	{
		self.ammo_rockets_real -= 1;
		W_UpdateAmmoCounts(self);
	}
	
	sound (self, CHAN_WEAPON, "weapons/grenade.wav", 1, ATTN_NORM);

	if (self.v_angle_x)
		vel = v_forward*600 + v_up * 200 + crandom()*v_right*10 + crandom()*v_up*10;
	else
	{
		vel = aim(self, 10000) * 600;
		vel_z = 200;
	}

	VK_smallkick(self);
	PRJ_FireProjectile(self, "progs/grenade.mdl", self.origin, vel, PE_EXPLOSIONGROUND, 0, 0, 2.5);
	PRJ_SetRadiusDamage(120, 160, MOD_GRENADE);
	PRJ_SetBouncyProjectile();

	if (deathmatch == 4)
	{
		self.attack_finished = time + 1.1;
		T_Damage (self, self, self.owner, 10, MOD_GRENADE);
	}
};

float (entity p1, entity p2) Get_ZDiff =
{
	local vector p_a, p_b;
	local float zdif;
	
	p_a_z = p1.origin_z;
	
	p_b_z = p2.origin_z;
	
	zdif = vlen(p_a - p_b);

	return (zdif);
}

void () StickyNade_Stick =
{
	local vector zd;
	
	if (self.enemy != world && self.enemy.health > 0) {
		zd_z = self.armorvalue;

		self.origin = self.enemy.origin + zd;
	}
	
	if (self.weapon < time) {
		GrenadeExplode();
		return;
	}
	
	self.nextthink = time + 0.1;
};

void () GrenadeBounce =
{
	local vector spot1;
	local vector spot2;

	if (self.selnade == GRENADE_STICKY)
	{
		if ((pointcontents (self.origin) == -6.000000))
		{
			remove (self);
			return;
		}
		if (other.takedamage)
		{
			if (other.origin != '0 0 0') {
				self.armorvalue = Get_ZDiff( self, other );
				self.weapon = self.nextthink;
				self.think = StickyNade_Stick;
				self.enemy = other;
				self.nextthink = time;
			}
			else {
				sound (self, 1, "effects/bodyhit2.wav", 1, 1);
			}
			return;
		}
		if (other.speed)
		{
			sound (self, 1, "weapons/bounce.wav", 1, 1);
			return;
		}
		else
		{
			sound (self, 1, "weapons/bounce.wav", 1, 1);
			self.movetype = 0.000000;
//			self.solid = 0.000000;
			self.solid = 2.000000;	// so they can be EMP'd
			spot1 = self.origin - (normalize (self.velocity) * 20.000000);
			spot2 = self.origin + (normalize (self.velocity) * 20.000000);
			traceline (spot1, spot2, 0.000000, self);
			self.angles = (vectoangles (trace_plane_normal) + '90.000000 0.000000 0.000000');
			setorigin (self, (self.origin + (trace_plane_normal * 6.000000)));
		}
	}
	else
	{
		sound (self, 1.000000, "weapons/bounce.wav", 1.000000, 1.000000);
	}
	if ((self.velocity == '0.000000 0.000000 0.000000'))
	{
		self.avelocity = '0.000000 0.000000 0.000000';
	}
};

void () W_ThrowGrenade =
{
	local entity missile;
	//local entity mpuff;

	sound (self, CHAN_WEAPON, "weapons/grenade.wav", WEAPON_SHOTGUN, ATTN_NORM);
	missile = spawn ();
	missile.owner = self;
	missile.movetype = MOVETYPE_BOUNCE;
	missile.solid = SOLID_BBOX;
	missile.classname = "grenade";
	makevectors (self.v_angle);
	if (self.v_angle_x)
	{
		missile.velocity = ((((v_forward * 250) + (v_up * 200)) + ((crandom () * v_right) * TE_LAVASPLASH)) + ((crandom () * v_up) * TE_LAVASPLASH));
	}
	else
	{
		missile.velocity = aim (self, 10000);
		missile.velocity = (missile.velocity * 250);
		missile.velocity_z = 150;
	}
	
	missile.avelocity = '300 300 300';		// FIXME: position your grenade model properly! it orbits instead of spinning!
	missile.angles = vectoangles (missile.velocity);
	missile.selnade = self.selnade;
	missile.touch = GrenadeBounce;
	missile.nextthink = (time + 2.5);
	missile.think = GrenadeExplode;
	if (self.selnade == GRENADE_STICKY)
		setmodel (missile, "progs/plasgren.mdl");
	else
		setmodel (missile, "progs/fraggren.mdl");
	
	setsize (missile, VEC_ORIGIN, VEC_ORIGIN);
	setorigin (missile, ((self.origin + '0 0 16') + (v_right * CONTENT_SKY)));
};

//=============================================================================
void(float ox) W_FireSpikes =
{
	if (self.ammo_nails_real < 1)
	{
		W_WeaponSwitch (W_BestWeapon ());
		return;
	}

	sound (self, CHAN_WEAPON, "weapons/rocket1i.wav", 1, ATTN_NORM);
	if (deathmatch != 4)
	{
		self.ammo_nails_real -= 1;
		W_UpdateAmmoCounts(self);
	}

	VK_smallkick(self);
	PRJ_FireProjectile(self,
		"progs/spike.mdl",
		self.origin + '0 0 16' + v_right*ox,
		aim(self, 1000) * 1000,
		PE_SPIKE,
		9,
		MOD_SPIKE,
		6);
};

void() W_FireSuperSpikes22 =
{
	if (self.ammo_nails_real < 2)
	{
		W_FireSpikes(0);
		return;
	}
	
	sound (self, CHAN_WEAPON, "weapons/spike2.wav", 1, ATTN_NORM);
	if (deathmatch != 4)
	{
		//self.ammo_nails_real -= 2;
		self.ammo_hshells -= 2;
		W_UpdateAmmoCounts(self);
	}

	VK_smallkick(self);
	PRJ_FireProjectile(self,
		"progs/s_spike.mdl",
		self.origin + '0 0 16',
		aim(self, 1000) * 1000,
		PE_SUPERSPIKE,
		18,
		MOD_SUPERSPIKE,
		6);
};

/*
===============================================================================

PLAYER WEAPON USE

===============================================================================
*/
// different from W_CheckNoAmmo due to SSG/SNG being able to fire 1 shot instead of 2...
BOOL(float wep) W_HasAmmo =
{
	switch (wep)
	{
	case IT_SHOTGUN:
		return self.ammo_shells_real >= 1;
	case IT_SUPER_SHOTGUN:
		return self.ammo_shells_real >= 2;
	case IT_NAILGUN:
		return self.ammo_nails_real >= 1;
	case IT_SUPER_NAILGUN:
		return self.ammo_nails_real >= 2;
	case IT_GRENADE_LAUNCHER:
	case IT_ROCKET_LAUNCHER:
		return self.ammo_rockets_real >= 1;
	case IT_LIGHTNING:
		return self.ammo_cells_real >= 1;
	}

	return TRUE;
};

void() W_UpdateWeapon =
{
	player_run ();          // get out of any weapon firing states

	self.items = self.items - ( self.items & (IT_SHELLS | IT_NAILS | IT_ROCKETS | IT_CELLS) );

	switch (self.weapon)
	{
	case WEAPON_PISTOL:
		self.weaponmodel = "progs/v_shot.mdl";
		self.items = self.items | IT_SHELLS;
		self.ammo_type = AT_SHELLS;
		break;
	case WEAPON_SHOT:
		self.weaponmodel = "progs/v_shot2.mdl";
		self.items = self.items | IT_SHELLS;
		self.ammo_type = AT_SHELLS;
		break;
	case WEAPON_AR:
		self.weaponmodel = "progs/v_nail.mdl";
		self.items = self.items | IT_NAILS;
		self.ammo_type = AT_NAILS;
		break;
	case WEAPON_UZI:
		self.weaponmodel = "progs/v_uzi.mdl";
		self.items = self.items | IT_NAILS;
		self.ammo_type = AT_NAILS; // solitude: ammo_hshells
		break;
	case WEAPON_SNIPER:
		self.weaponmodel = "progs/v_sniper.mdl";
		self.items = self.items | IT_SHELLS;
		self.ammo_type = AT_SHELLS;
		break;
	case WEAPON_RL:
		self.weaponmodel = "progs/v_rocket.mdl";
		self.items = self.items | IT_ROCKETS;
		self.ammo_type = AT_ROCKETS;
		break;
	case WEAPON_PPISTOL:
		self.weaponmodel = "progs/v_plpist.mdl";
		self.items = self.items | IT_CELLS;
		self.ammo_type = AT_CELLS;
		break;
	case WEAPON_SWORD:
		self.weaponmodel = "progs/v_axe.mdl";
		self.items = self.items | IT_CELLS;
		self.ammo_type = AT_CELLS;
		break;
	case WEAPON_NEEDLER:
		self.weaponmodel = "progs/v_needle.mdl";
		self.items = self.items | IT_CELLS;
		self.ammo_type = AT_CELLS;
		break;
	case WEAPON_PRIFLE:
		self.weaponmodel = "progs/v_plrifle.mdl";
		self.items = self.items | IT_CELLS;
		self.ammo_type = AT_CELLS;
		break;
	default:
		self.weaponmodel = "";
	}

	self.weaponframe = 0;
};

void(float weap) W_WeaponSwitch =
{
	if (self.weaponmodel != "" && self.weaponframe > 0 && self.weaponframe < 4)			// xavior: hackish - may need other checks in the future (frames 1 - 4 are generally firing frames)
		return;

	// skip weapon model/ammo_type update if this isn't a new weapon
	if (self.weapon != weap)
	{
		self.weapon = weap;
		W_UpdateWeapon();
	}

	// always update ammo count
	W_UpdateAmmoCounts(self);
	
	Set_FOV ( FOV_DEFAULT );
	self.pfov = FOV_DEFAULT;
};

float() W_BestWeapon =
{
	float fl;

	if (cvar("nobest") == 0)		// solitude: debug
		return (self.weapon);
		
	if (self.waterlevel <= 1)
		fl = IT_LIGHTNING;
	else
		fl = IT_SUPER_NAILGUN;

	while (1)
	{
		if ( (self.items & fl) && W_HasAmmo(fl) )
			return fl;

		// best weapon order
		switch (fl)
		{
		case IT_LIGHTNING:
			fl = IT_SUPER_NAILGUN;
			break;
		case IT_SUPER_NAILGUN:
			fl = IT_SUPER_SHOTGUN;
			break;
		case IT_SUPER_SHOTGUN:
			fl = IT_NAILGUN;
			break;
		case IT_NAILGUN:
			fl = IT_SHOTGUN;
			break;
		case IT_SHOTGUN:
		default:
			return IT_AXE; // so we don't get an infinite loop with certain engines
		}
	}
};

BOOL() W_CheckNoAmmo =
{
	if (self.currentammo > 0)
		return TRUE;

	if (self.weapon == IT_AXE)
		return TRUE;
	
	W_WeaponSwitch (W_BestWeapon ());
	
// drop the weapon down
	return FALSE;
};

/*
============
W_Attack

An attack impulse can be triggered now
============
*/
void()	player_shot1;

// Halo stuff
void () player_hshot;
void () player_hshot_melee;
void () player_uzi_reload;
void () player_shot_melee;
void () player_shot2_melee;
void () player_nail_melee;
void () player_shot_throw;
void () player_shot2_throw;
void () player_nail_throw;

void () player_rl_reload;
void () player_rl_throw;
void () player_rl_melee;

void () player_uzi_throw;

void () player_sniper_melee;
void () player_sniper_throw;

//void()	player_nail1;
void () player_ar1;
void()	player_nail2;
void()	muzzleflash;

void() W_Attack =
{
	float r;
	local float heat_multi, i;
	local vector source;

	if (!W_CanFire (self))
		return;
		
	makevectors (self.v_angle);                 // calculate forward angle for velocity
	self.show_hostile = time + 1;   // wake monsters up

	if (self.weaponstate == WS_IDLE) // start delay
		self.delay = time + 0.1;

	// animations are dealt with here
	switch (self.weapon) 
	{
	case WEAPON_PISTOL:
		muzzleflash();
		//_bprint(ftos(self.weaponframe), "\n");
		self.weaponframe = 1;
		self.wepanim = 1;
		self.weaponframe_time = time + 0.1;
		break;
	case IT_NAILGUN:
		muzzleflash();
		self.weaponframe = 1;
		self.wepanim = 1;
		break;
	case IT_SUPER_NAILGUN:
		self.weaponframe = WEAPON_SHOTGUN;
		player_nail2();
		/*
		muzzleflash();
		if (self.weaponframe == 0)
			self.weaponframe = 1;

		if (self.weaponframe & 1)
			player_nail1();
		else
			player_nail2();
		break;		
		*/
	case IT_GRENADE_LAUNCHER:
	case IT_ROCKET_LAUNCHER:
		self.weaponframe = 1;
		muzzleflash();
		//player_rocket1();
		break;
	case WEAPON_PPISTOL:
		heat_multi = 1;

		i = 0;
		while (i < 8) {
			i++;
			if (self.weaponheat < i*heat_multi) {
				self.weaponframe = 4 + i;
				break;
			}
		}
		
		self.weaponheat++;
		if (i >= 8) {
			if (self.weaponframe > 13)
				self.weaponframe = 12;
			else
				self.weaponframe++;
		}

		if (self.weaponheat > 14)
			self.weaponheat = 15;
		if (!self.button0 || self.weaponheat > 15) {
			muzzleflash();
			W_FirePPistol ( self.weaponheat );
			self.weaponheat = 0;
			self.weaponframe_time = time + 0.1;

			if (self.exppistol >= 100) {
				self.wepanim = 0;
				self.exppistol = 99;
				W_UpdateAmmoCounts(self);
				self.weaponframe = 16;
				player_reload1();
			}
			else {
				self.weaponframe = 1;
				self.wepanim = 1;
			}
		}
		else
			self.weaponframe_time = time + 0.2;
			
		break;
	case WEAPON_SWORD:
		// See if we should perform a lunge
		makevectors (self.v_angle);
		source = self.origin + '0 0 16';
		traceline (source, source + v_forward*120, FALSE, self);
		
		if (trace_ent.classname == "player" && trace_ent.health > 0) {
			self.weaponframe = 9;
			self.velocity = v_forward*620;
		}
		else {
			r = random();

			if (r < 0.5)
				self.weaponframe = 19;
			else
				self.weaponframe = 26;
		}
		self.wepanim = 1;
		self.weaponframe_time = time + 0.1;
		break;
	case WEAPON_PRIFLE:
		muzzleflash();
		self.weaponframe = 1;
		self.wepanim = 1;
		self.weaponframe_time = time + 0.065;
		break;
	case WEAPON_PISTOL:
		muzzleflash();
		self.weaponframe = 1;
		self.wepanim = 1;
		self.weaponframe_time = time + 0.1;
		break;
	default:
		muzzleflash();
		self.weaponframe = 1;
		self.wepanim = 1;
		self.weaponframe_time = time + 0.1;
		break;
	}

	SuperDamageSound();

	// firing is done here (r is used for round time instead of a temp here)
	switch (self.weapon)
	{
	case WEAPON_PISTOL:
		W_FirePistol ();
		r = 0.3;
		break;
	case WEAPON_SHOT:
		W_FireShotgun ();
		r = 0.65;
		break;
	case WEAPON_AR:
		W_FireAR();
		r = 0.12;
		break;
	case WEAPON_RL:
		W_FireRocket();
		r = 1.6;
		break;
	case WEAPON_UZI:
		W_FireUzi();
		r = 0.1;
		break;
	case WEAPON_SNIPER:
		W_FireSniper();
		r = 0.8;
		break;
	case WEAPON_PPISTOL:
		//W_FirePPistol();
		r = 0.1;
		break;
	case WEAPON_SWORD:
		//W_FireSword(0);
		r = 0.6;
		break;
	case WEAPON_NEEDLER:
		W_FireNeedler();
		if (self.needler_heat > 10)
			r = 0.07;
		else if (self.needler_heat > 5)
			r = 0.12;
		else
			r = 0.17;
		break;
	case WEAPON_PRIFLE:
		W_FirePlasmaRifle();
		if (self.prifle_heat > 8)
			r = 0.125;
		else if (self.prifle_heat > 3)
			r = 0.15;
		else
			r = 0.175;
		break;
	}

		
	if (self.weaponstate == WS_IDLE)
		self.weaponstate = WS_FIRING1;

	// advance attack time
	if (self.attack_finished <= time)
		self.attack_finished = self.attack_finished + r;
		
	// Frikbot - reloading
	if (self.ishuman != TRUE) {
	//_bprint(ftos(self.currentammo),"\n");
		if (self.currentammo <= 0) {
			reload ();
			self.currentammo = 1;		// so he doesn't run to the player
			return;
		}
	}
};

/*
============
W_ChangeWeapon

============
*/
void() W_ChangeWeapon =
{
	local   float   fl;
	
	switch (self.impulse)
	{
	case 1:
		fl = IT_AXE;
		break;
	case 2:
		fl = IT_SHOTGUN;
		break;
	case 3:
		fl = IT_SUPER_SHOTGUN;
		break;
	case 4:
		fl = IT_NAILGUN;
		break;
	case 5:
		fl = IT_SUPER_NAILGUN;
		break;
	case 6:
		fl = IT_GRENADE_LAUNCHER;
		break;
	case 7:
		fl = IT_ROCKET_LAUNCHER;
		break;
	case 8:
		fl = IT_LIGHTNING;
		break;
	}
	
	
	if (!(self.items & fl))
	{       // don't have the weapon or the ammo
		sprint1 (self, PRINT_HIGH, "no weapon.\n");
		return;
	}
	
/*	if (!W_HasAmmo(fl))
	{       // don't have the ammo
		sprint1 (self, PRINT_HIGH, "not enough ammo.\n");
		return;
	}*/

//
// set weapon, set ammo
//
	W_WeaponSwitch (fl);
};

/*
============
CheatCommand
============
*/
void() CheatCommand =
{
      if (deathmatch || coop)
		return;

#ifndef IMPULSE9
	bprint("Impulse 9 disabled. Use Impulses 14 through 26 to spawn all weapons.\n");
#else
	self.ammo_rockets_real = 100;
	self.ammo_nails_real = 200;
	self.ammo_shells_real = 100;
	self.ammo_cells_real = 100;
	self.items |= IT_AXE |
		IT_SHOTGUN |
		IT_SUPER_SHOTGUN |
		IT_NAILGUN |
		IT_SUPER_NAILGUN |
		IT_GRENADE_LAUNCHER |
		IT_ROCKET_LAUNCHER |
		IT_LIGHTNING |
		IT_KEY1 | IT_KEY2;

	W_WeaponSwitch (IT_ROCKET_LAUNCHER);
#endif
};

/*
============
CycleWeaponCommand

Go to the next weapon with ammo
============
*/
void() CycleWeaponCommand =
{
	local float w;
	w = self.weapon;

	while (1)
	{
		switch (w)
		{
		case IT_LIGHTNING:
			w = IT_AXE;
			break;
		case IT_AXE:
			w = IT_SHOTGUN;
			break;
		case IT_SHOTGUN:
			w = IT_SUPER_SHOTGUN;
			break;
		case IT_SUPER_SHOTGUN:
			w = IT_NAILGUN;
			break;
		case IT_NAILGUN:
			w = IT_SUPER_NAILGUN;
			break;
		case IT_SUPER_NAILGUN:
			w = IT_GRENADE_LAUNCHER;
			break;
		case IT_GRENADE_LAUNCHER:
			w = IT_ROCKET_LAUNCHER;
			break;
		case IT_ROCKET_LAUNCHER:
			w = WEAPON_NEEDLER;
			break;
		case WEAPON_NEEDLER:
			w = WEAPON_PRIFLE;
			break;
		case WEAPON_PRIFLE:
			w = IT_LIGHTNING;
			break;
		}
	
		if ( (self.items & w) /*&& W_HasAmmo(w)*/ )
		{
			W_WeaponSwitch (w);
			return;
		}
	}

};


/*
============
CycleWeaponReverseCommand

Go to the prev weapon with ammo
============
*/
void() CycleWeaponReverseCommand =
{
	local float w;
	w = self.weapon;

	while (1)
	{
		switch (w)
		{
		case IT_LIGHTNING:
			w = IT_ROCKET_LAUNCHER;
			break;
		case IT_ROCKET_LAUNCHER:
			w = IT_GRENADE_LAUNCHER;
			break;
		case IT_GRENADE_LAUNCHER:
			w = IT_SUPER_NAILGUN;
			break;
		case IT_SUPER_NAILGUN:
			w = IT_NAILGUN;
			break;
		case IT_NAILGUN:
			w = IT_SUPER_SHOTGUN;
			break;
		case IT_SUPER_SHOTGUN:
			w = IT_SHOTGUN;
			break;
		case IT_SHOTGUN:
			w = IT_AXE;
			break;
		case IT_AXE:
			w = IT_LIGHTNING;
			break;
		}
	
		if ( (self.items & w) && W_HasAmmo(w) )
		{
			W_WeaponSwitch (w);
			return;
		}
	}

};


/*
============
ServerflagsCommand

Just for development
============
*/
void() ServerflagsCommand =
{
      if (deathmatch || coop)
		return;

	serverflags = serverflags * 2 + 1;
};

// self heal
void () Heal =
{
	self.health = (self.health + WEAPON_SHOTGUN);
};

// Solitude Reload
void () reload =
{
	if (self.armorvalue > 0 && self.currentammo != W_GetMaxClip(self.weapon, 1)) {
		switch (self.weapon) {
			case WEAPON_PISTOL:
			{
				self.weaponframe = WEAPON_BIG;
				break;
			}
			case WEAPON_SHOT:
			{
				self.weaponframe = 11;
				break;
			}
			case WEAPON_AR:
			{
				self.weaponframe = 5;
				break;
			}
			case WEAPON_RL:
			{
				self.weaponframe = 11;
				break;
			}
			case WEAPON_NEEDLER:
			{
				self.weaponframe = 5;
				break;
			}
			case WEAPON_PPISTOL:
			{
				return;			// No manual reload
			}
			default:
			{
				self.weaponframe = 4;
				break;
			}
		}
		player_reload1 ();		// now that we set the start frame, begin the reload
	}
};

/*
============
ImpulseCommands

============
*/
void() ImpulseCommands =
{
	if (self.weaponheat)
		return;

	switch (self.impulse) {
	case 1 .. 8:
		W_ChangeWeapon ();
		break;
	case 9:
		CheatCommand ();
		break;
	case 10:
		CycleWeaponCommand ();
		break;
	case 11:
		WeaponZoom ();
		break;
	case 13:
		if (self.pickup_time > time) {
			self.canpickup_time = time + .1;
			return;
		}
		if (self.pickup_time > time) {
			self.canpickup_time = time + .1;
			return;
		}
//		if (time < self.attack_finished)
//			return;

		Set_FOV ( FOV_DEFAULT );
		self.pfov = FOV_DEFAULT;
		reload ();
		break;
	case 14:
		ThrowWeapon(WEAPON_PISTOL, 0);
		break;
	case 15:
		ThrowWeapon(WEAPON_SHOT, 0);
		break;
	case 16:
		ThrowWeapon(WEAPON_AR, 0);
		break;
	case 17:
		ThrowWeapon(WEAPON_UZI, 0);
		break;
	case 18:
		ThrowWeapon(WEAPON_RL, 0);
		break;
	case 19:
		ThrowWeapon(WEAPON_SNIPER, 0);
		break;
	case 20:
		ThrowWeapon(WEAPON_PPISTOL, 0);
		break;
	case 21:
		ThrowWeapon(WEAPON_SWORD, 0);
		break;
	case 22:
		ThrowWeapon(WEAPON_NEEDLER, 0);
		break;
	case 23:
		ThrowWeapon(WEAPON_PRIFLE, 0);
		break;
	case 25:
		ThrowWeapon(666, 0);
		break;
	case 26:
		ThrowWeapon(667, 0);
		break;
	case 50:
		stuffcmd( self, "play sound/music/Solitude_MainTheme_Low.wav\n" );
		break;
	case 29:
	{
		Set_FOV ( FOV_DEFAULT );
		self.pfov = FOV_DEFAULT;
		pre_player_melee ();
		break;
	}
	case 27:
	{
		if (self.selnade == 0)
		{
			self.selnade = 1;
			_sprint (self, "Selected Sticky Grenade\n");
		}
		else
		{
			if (self.selnade == 1)
			{
				self.selnade = 0;
				_sprint (self, "Selected Regular Grenade\n");
			}
		}
		break;
	}
	case 28:
	{
		Set_FOV ( FOV_DEFAULT );
		self.pfov = FOV_DEFAULT;
		pre_player_throw_grenade ();
		break;
	}
		
	}


	self.impulse = 0;
};

/*
============
W_HandlePlayerFrame

Handle player weapon model
============
*/
// ADDME: This function is actually very useful, but my lazy self is not making full use out of it.
// what shoudl be done in the future is allow this function to handle ALL first-person weapon anims
// including melee, throwgren, fire, etc. Right now it only handles a few weapons firing. The rest
// is done in player.qc >.<
// - avirox
void() W_HandlePlayerFrame =
{
	if (!self.weaponframe && !self.wepanim)
		return;
		
	if (self.weaponframe_time >= time)
		return;

	switch (self.weapon)
	{
	case WEAPON_PISTOL:
		if (self.weaponframe > 3)		// assume that we're not firing and that animations should be handled in player.qc or elsewhere
			return;
		self.weaponframe = self.weaponframe + 1;
		self.weaponframe_time = time + 0.1;
		if (self.weaponframe > 3)
			self.weaponframe = 0;
			
		//_bprint(ftos(self.weaponframe),"\n");
		break;
	case WEAPON_SHOT:
		if (self.weaponframe > 4)		// assume that we're not firing and that animations should be handled in player.qc or elsewhere
			return;
		self.weaponframe = self.weaponframe + 1;
		self.weaponframe_time = time + 0.1;
		if (self.weaponframe > 4)
			self.weaponframe = 0;
			
		//_bprint(ftos(self.weaponframe),"\n");
		break;
	case WEAPON_AR:
		if (self.weaponframe > 3)	
			return;
		self.weaponframe = self.weaponframe + 1;
		self.weaponframe_time = time + 0.1;
		if (self.weaponframe > 3)
			self.weaponframe = 0;
		break;
		
	case WEAPON_UZI:
		// cycle until fire button is released
		if (self.weaponframe > 3)	
			return;
		if (self.currentammo == 0) {
			self.weaponframe = 0;
			return;
		}
		if (self.weaponstate != WS_IDLE)
 		{
			self.weaponframe_time = time + 0.1;
  			self.weaponframe = self.weaponframe + 1;
  			if (self.weaponframe > 2)
  				self.weaponframe = 1;
  		}
  		else
  			self.weaponframe = 0;

		break;
	case WEAPON_RL:
		if (self.weaponframe > 11)		// assume that we're not firing and that animations should be handled in player.qc or elsewhere
			return;
		self.weaponframe = self.weaponframe + 1;
		self.weaponframe_time = time + 0.1;
		if (self.weaponframe > 10)
			self.weaponframe = 0;
		break;
	case WEAPON_SNIPER:
		if (self.weaponframe > 3)		// assume that we're not firing and that animations should be handled in player.qc or elsewhere
			return;
		self.weaponframe = self.weaponframe + 1;
		self.weaponframe_time = time + 0.1;
		if (self.weaponframe > 3)
			self.weaponframe = 0;
		break;
	case WEAPON_PPISTOL:
		if (self.weaponframe > 3)		// assume that we're not firing and that animations should be handled in player.qc or elsewhere
			return;
		self.weaponframe = self.weaponframe + 1;
		self.weaponframe_time = time + 0.1;
		if (self.weaponframe > 3)
			self.weaponframe = 0;
		break;
	case WEAPON_SWORD:
		if (self.weaponframe > 18 && self.weaponframe < 25) {			// Lunge attack
			self.weaponframe = self.weaponframe + 1;
			self.weaponframe_time = time + 0.1;
			if (self.weaponframe == 21)
				W_FireSword(1);
			if (self.weaponframe > 24)
				self.weaponframe = 0;
		}
		else if (self.weaponframe > 25 && self.weaponframe < 32) {
			self.weaponframe = self.weaponframe + 1;
			self.weaponframe_time = time + 0.1;
			if (self.weaponframe == 29)
				W_FireSword(0);
			if (self.weaponframe > 31)
				self.weaponframe = 0;
		}
		else {
			self.weaponframe = self.weaponframe + 1;
			self.weaponframe_time = time + 0.1;
			if (self.weaponframe == 15)
				W_FireSword(0);			
			if (self.weaponframe > 18)
				self.weaponframe = 0;
		}
		break;
	case WEAPON_NEEDLER:
		if (self.weaponframe > 3)		// assume that we're not firing and that animations should be handled in player.qc or elsewhere
			return;
		self.weaponframe = self.weaponframe + 1;
		self.weaponframe_time = time + 0.1;
		if (self.weaponframe > 3)
			self.weaponframe = 0;
		break;
	case WEAPON_PRIFLE:
		if (self.weaponframe > 3)		// assume that we're not firing and that animations should be handled in player.qc or elsewhere
			return;
		self.weaponframe = self.weaponframe + 1;
		self.weaponframe_time = time + 0.1;
		if (self.weaponframe > 3)
			self.weaponframe = 0;
		break;
	default:
		// Solitude
		if (self.weaponframe > 4)		// assume that we're not firing and that animations should be handled in player.qc or elsewhere
			return;
		self.weaponframe = self.weaponframe + 1;
		self.weaponframe_time = time + 0.1;
		if (self.weaponframe > 6)
			self.weaponframe = 0;
	}
	
	self.wepanim = 0;	// turn hack off
};

/*
============
W_WeaponFrame

Called every frame so impulse events can be handled as well as possible
============
*/
void() W_WeaponFrame =
{
	local INTEGER scount;

	W_HandlePlayerFrame();

	if ((self.health < self.ohealth))
	{
		self.regen = (time + AS_MELEE);
	}
	self.ohealth = self.health;
	if (((time > self.regen) && (self.health < 100)))
	{
		Heal ();
	}
	
	if (time < self.attack_finished)
		return;

	if (self.impulse)
		ImpulseCommands ();
	
// check for attack
	if (self.button0)
	{
		scount = 0;
		// play catchup but don't allow more than 4 shots per frame
		while (self.attack_finished <= time)
		{
			if (scount >= 4)
			{
				self.attack_finished = time;
				break;
			}

			W_Attack();
			scount++;
		}
	}
	else
	{
		if (self.weaponheat > 0) {
			W_Attack();
		}
		if (self.needler_heat > 0)
			self.needler_heat = 0;
		if (self.prifle_heat > 0)
			self.prifle_heat = 0;
		self.attack_finished = time;
		self.weaponstate = WS_IDLE;
	}
};

/*
========
SuperDamageSound

Plays sound if needed
========
*/
void() SuperDamageSound =
{
	if (self.super_damage_finished > time)
	{
		if (self.super_sound < time)
		{
			self.super_sound = time + 1;
			sound (self, CHAN_BODY, "items/damage3.wav", 1, ATTN_NORM);
		}
	}
	return;
};

/*
void() testfunction =
{
	local vector v;
	local float a, b, c;

	a = 2;
	b = 4;
	c = 6;
	a *= 2;
	b *= 2;
	c *= 2;
	v = '2 4 6';
	v *= 2;
	if (!a && !b && !c)
		return;

	if (!v)
		return;

	v_x = 23;

	if (self.health && self.ammo_shells && self.ammo_cells)
		return;
};
*/
 
// GOLD: this is now a wrapper for W_UpdateAmmoCounts
void () W_SetCurrentAmmo =
{
	self.weaponframe = 0;
	W_UpdateAmmoCounts(self);
/*
	player_run ();
	self.items = (self.items - (self.items & (((IT_SHELLS | IT_NAILS) | IT_ROCKETS) | IT_CELLS)));
	if ((self.weapon == IT_AXE))
	{
		self.currentammo = MSG_BROADCAST;
		self.weaponmodel = "progs/v_axe.mdl";
		self.weaponframe = MSG_BROADCAST;
	}
	else
	{
		if ((self.weapon == IT_SHOTGUN))
		{
			self.currentammo = self.ammo_shells;
			self.weaponmodel = "progs/v_shot.mdl";
			self.weaponframe = MSG_BROADCAST;
			self.items = (self.items | IT_SHELLS);
		}
		else
		{
			if ((self.weapon == IT_SUPER_SHOTGUN))
			{
				self.currentammo = self.ammo_shells2;
				self.weaponmodel = "progs/v_shot2.mdl";
				self.weaponframe = MSG_BROADCAST;
			}
			else
			{
				if ((self.weapon == IT_NAILGUN))
				{
					self.currentammo = self.ammo_nails;
					self.weaponmodel = "progs/v_nail.mdl";
					self.weaponframe = MSG_BROADCAST;
				}
				else
				{
					if ((self.weapon == IT_SUPER_NAILGUN))
					{
						self.currentammo = self.ammo_hshells;
						self.weaponmodel = "progs/v_shotgun.mdl";
						self.weaponframe = MSG_BROADCAST;
					}
					else
					{
						if ((self.weapon == IT_GRENADE_LAUNCHER))
						{
							self.currentammo = self.ammo_rockets;
							self.weaponmodel = "progs/v_rock.mdl";
							self.weaponframe = MSG_BROADCAST;
							self.items = (self.items | IT_ROCKETS);
						}
						else
						{
							if ((self.weapon == IT_ROCKET_LAUNCHER))
							{
								self.currentammo = self.ammo_rockets;
								self.weaponmodel = "progs/v_rocket.mdl";
								self.weaponframe = MSG_BROADCAST;
								self.items = (self.items | IT_ROCKETS);
							}
							else
							{
								if ((self.weapon == IT_LIGHTNING))
								{
									self.currentammo = self.ammo_cells;
									self.weaponmodel = "progs/v_light.mdl";
									self.weaponframe = MSG_BROADCAST;
									self.items = (self.items | IT_CELLS);
								}
								else
								{
									self.currentammo = MSG_BROADCAST;
									self.weaponmodel = "";
									self.weaponframe = MSG_BROADCAST;
								}
							}
						}
					}
				}
			}
		}
	}
	*/
}
 