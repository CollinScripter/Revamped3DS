/*
*/

void (entity targ, entity inflictor, entity attacker, float damage) T_Damage;
void () player_run;
void(entity inflictor, entity attacker, float radius, entity ignore) T_RadiusDamage;
void() SuperDamageSound;

// called by worldspawn
void() W_Precache =
{
	precache_sound ("weapons/r_exp3.wav");	// new rocket explosion
	precache_sound ("weapons/rocket1i.wav");	// spike gun
	precache_sound ("weapons/sgun1.wav");
	precache_sound ("weapons/guncock.wav");	// player shotgun
	//precache_sound ("weapons/ric1.wav");	// ricochet (used in c code)
	//precache_sound ("weapons/ric2.wav");	// ricochet (used in c code)
	//precache_sound ("weapons/ric3.wav");	// ricochet (used in c code)
	//precache_sound ("weapons/spike2.wav");	// super spikes
	precache_sound ("weapons/tink1.wav");	// spikes tink (used in c code)
	//precache_sound ("weapons/grenade.wav");	// grenade launcher
	precache_sound ("weapons/bounce.wav");		// grenade bounce
	precache_sound ("weapons/shotgn2.wav");	// super shotgun
	precache_sound ("weapons/sniper.wav");	// sniper
	precache_model ("progs/blast.spr");		//blaster bullet sprite.
	precache_model ("progs/sniper.mdl");	//beam for the Sniper blaster
	precache_model ("progs/ric_beam.mdl");	//Beam for The richochet blaster
	precache_model ("progs/null.spr");
	precache_model ("progs/body.spr");
	
	//Morphball sounds
	precache_sound ("weapons/boost.wav");
	precache_sound ("weapons/mb_bomb.wav");	// Morphball lays a bomb
	precache_sound ("weapons/mb_explode.wav");
	precache_sound ("weapons/morphball.wav");
	precache_sound ("weapons/mb_bomb.wav");
	
	//Footsteps
	precache_sound ("steps/foot1.wav");
	precache_sound ("steps/foot2.wav");
	precache_sound ("steps/foot3.wav");
	precache_sound ("steps/foot4.wav");

	//Transform Sounds
	precache_sound ("weapons/blaster_transform.wav");
	precache_sound ("weapons/rocket_transform.wav");

	//Effects
		//Muzzleflashes
		precache_model ("progs/blaster_muzzle.spr");
		precache_model ("progs/ric_muzzle.spr");
		precache_model ("progs/sniper_muzzle.spr");
		precache_model ("progs/splaser_muzzle.spr");

};

float() crandom =
{
	return 2*(random() - 0.5);
};

/*
================
W_FireAxe
================
*/
void() W_FireAxe =
{
	local	vector	source;
	local	vector	org;

	makevectors (self.v_angle);
	source = self.origin + '0 0 16';
	traceline (source, source + v_forward*64, FALSE, self);
	if (trace_fraction == 1.0)
		return;
	
	org = trace_endpos - v_forward*4;

	if (trace_ent.takedamage)
	{
		trace_ent.axhitme = 1;
		SpawnBlood (org, '0 0 0', 20);
		T_Damage (trace_ent, self, self, 20);
	}
	else
	{	// hit wall
		sound (self, CHAN_WEAPON, "player/axhit2.wav", 1, ATTN_NORM);
		WriteByte (MSG_BROADCAST, SVC_TEMPENTITY);
		WriteByte (MSG_BROADCAST, TE_GUNSHOT);
		WriteCoord (MSG_BROADCAST, org_x);
		WriteCoord (MSG_BROADCAST, org_y);
		WriteCoord (MSG_BROADCAST, org_z);
	}
};


//============================================================================


vector() wall_velocity =
{
	local vector	vel;
	
	vel = normalize (self.velocity);
	vel = normalize(vel + v_up*(random()- 0.5) + v_right*(random()- 0.5));
	vel = vel + 2*trace_plane_normal;
	vel = vel * 200;
	
	return vel;
};


/*
==============================================================================

MULTI-DAMAGE

Collects multiple small damages into a single damage

==============================================================================
*/

entity	multi_ent;
vector  puff_org;
float	multi_damage;

void() ClearMultiDamage =
{
	multi_ent = world;
	multi_damage = 0;
};

void() ApplyMultiDamage =
{
	if (!multi_ent)
		return;
	T_Damage (multi_ent, self, self, multi_damage);
};

void(entity hit, float damage) AddMultiDamage =
{
	if (!hit)
		return;
	
	if (hit != multi_ent)
	{
		ApplyMultiDamage ();
		multi_damage = damage;
		multi_ent = hit;
	}
	else
		multi_damage = multi_damage + damage;
};

/* 
>>>>>>>>>>>>>>>>>>>>>>>>>
Touch Functions and Exlosions for Damage.
-I hate how all the Bullet damage functions are strewn around everywhere. This is where you Will find the Bullet-damage
For All the weapons. And I don't wanna create a new qc because I have do define Crap, and then Go there to edit.
it is Just fine right here.
<<<<<<<<<<<<<<<<<<<<<<<<<
*/
//For something.... Just Don't care to Go look. Find it yourself in combat.qc

vector(entity proj) bounce_off_wall =		// borrowing
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
	proj.velocity = v_forward * 2000;//proj.old_velocity;

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
	sound (self, CHAN_WEAPON, "weapons/bounce.wav", 1, ATTN_NORM);
	proj.angles = vectoangles (vec);
	// this is required to make downward slopes not stop the projectile
	proj.flags = proj.flags - ( proj.flags & FL_ONGROUND );
	return vec;
}
void () bounce_a =
{
	self.velocity = bounce_off_wall( self );
};

void () Bounce_Off_Walls =
{
	self.nextthink = time;
	self.think = bounce_a;

	if (self.velocity == '0 0 0')
		remove (self);
};

/*
=============================
RIC TOUCH 0
============================
*/
void () ric_touch =
{
	if (pointcontents(self.origin) == CONTENT_SKY)
	{
		remove(self);
		return;
	}
	else if (other.takedamage) {
		spawn_touchblood (18);
		T_Damage (other, self, self.owner, 10);	
	}
	else if (self.lives > 0) {
		particle (self.origin, '0 0 0', 179, 20);
		Bounce_Off_Walls ();
		self.lives -= 1;
		return;
	}
	
	remove(self);
};
/*
=============================
RIC TOUCH 1
============================
*/
void () ric_touch_1 =
{
	if (pointcontents(self.origin) == CONTENT_SKY)
	{
		remove(self);
		return;
	}
	else if (other.takedamage) {
		spawn_touchblood (20);
		T_Damage (other, self, self.owner, 15);	
	}
	else if (self.lives > 0) {
		particle (self.origin, '0 0 0', 179, 20);
		Bounce_Off_Walls ();
		self.lives -= 1;
		return;
	}
	
	remove(self);
};
/*
=============================
RIC TOUCH 2
============================
*/
void () ric_touch_2 =
{
	if (pointcontents(self.origin) == CONTENT_SKY)
	{
		remove(self);
		return;
	}
	else if (other.takedamage) {
		spawn_touchblood (25);
		T_Damage (other, self, self.owner, 20);	
	}
	else if (self.lives > 0) {
		particle (self.origin, '0 0 0', 179, 20);
		Bounce_Off_Walls ();
		self.lives -= 1;
		return;
	}
	
	remove(self);
};
/*
=============================
RIC TOUCH 3
============================
*/
void () ric_touch_3 =
{
	if (pointcontents(self.origin) == CONTENT_SKY)
	{
		remove(self);
		return;
	}
	else if (other.takedamage) {
		spawn_touchblood (25);
		T_Damage (other, self, self.owner, 25);	
	}
	else if (self.lives > 0) {
		particle (self.origin, '0 0 0', 179, 20);
		Bounce_Off_Walls ();
		self.lives -= 1;
		return;
	}
	
	remove(self);
};
/*
==========================================
ROCKET LAUNCHER 0
==========================================
*/
void() Rocket_Explode0 =
{

	if (other == self.owner)
		return;		// don't explode on owner

	if (pointcontents(self.origin) == CONTENT_SKY)
	{
		remove(self);
		return;
	}
	T_RadiusDamage (self, self.owner, 120, other);

	self.origin = self.origin - 8*normalize(self.velocity);


	CreateExplosion (self.origin);
	remove(self);
};
/*
==========================================
ROCKET LAUNCHER 1
==========================================
*/
void() Rocket_Explode1 =
{

	if (other == self.owner)
		return;		// don't explode on owner

	if (pointcontents(self.origin) == CONTENT_SKY)
	{
		remove(self);
		return;
	}
	T_RadiusDamage (self, self.owner, 140, other);

	self.origin = self.origin - 8*normalize(self.velocity);


	CreateExplosion (self.origin);
	remove(self);
};
/*
==========================================
ROCKET LAUNCHER 2
==========================================
*/
void() Rocket_Explode2 =
{

	if (other == self.owner)
		return;		// don't explode on owner

	if (pointcontents(self.origin) == CONTENT_SKY)
	{
		remove(self);
		return;
	}
	T_RadiusDamage (self, self.owner, 160, other);

	self.origin = self.origin - 8*normalize(self.velocity);


	CreateExplosion (self.origin);
	remove(self);
};
/*
==========================================
ROCKET LAUNCHER 3
==========================================
*/
void() Rocket_Explode3 =
{

	if (other == self.owner)
		return;		// don't explode on owner

	if (pointcontents(self.origin) == CONTENT_SKY)
	{
		remove(self);
		return;
	}
	T_RadiusDamage (self, self.owner, 190, other);

	self.origin = self.origin - 8*normalize(self.velocity);


	CreateExplosion (self.origin);
	remove(self);
};
void() T_MissileTouch =
{
	local float	damg;

	if (other == self.owner)
		return;		// don't explode on owner

	if (pointcontents(self.origin) == CONTENT_SKY)
	{
		remove(self);
		return;
	}

	damg = 40 + random()*10;
	
	if (other.health)
	{
		T_Damage (other, self, self.owner, damg );
	}

	// don't do radius damage to the other, because all the damage
	// was done in the impact
	T_RadiusDamage (self, self.owner, 120, other);

//	sound (self, CHAN_WEAPON, "weapons/r_exp3.wav", 1, ATTN_NORM);
	self.origin = self.origin - 8*normalize(self.velocity);


	CreateExplosion (self.origin);
	remove(self);
};

/*
=============================
Magma explode
============================
*/
void() magmaexplode =
{	
	T_RadiusDamage (self, self.owner, 120, other);

//	sound (self, CHAN_WEAPON, "weapons/r_exp3.wav", 1, ATTN_NORM);
	self.origin = self.origin - 8*normalize(self.velocity);


	CreateExplosion(self.origin);
	remove(self);
};
/*
=============================
Splaser Beam touch
============================
*/
void(vector org) SplaserTouch =
{
	if (pointcontents(self.origin) == CONTENT_SKY)
	{
		remove(self);
		return;
	}
	else if (other.takedamage) {
			spawn_touchblood (18);
			T_Damage (other, self, self.owner, 9);

			
			}
	else
	{
		particle (self.origin, '0 0 0', 149, 20);
		puff_org = self.origin;
		remove(self);
	}
};
/*
=============================
MAGMA TOUCH
============================
*/
void(vector org) magma_touch =
{
	if (pointcontents(self.origin) == CONTENT_SKY)
	{
		remove(self);
		return;
	}
	else if (other.takedamage) {
			spawn_touchblood (18);
			T_Damage (other, self, self.owner, 20);
			remove(self);
			}
	else
	{
		puff_org = self.origin;
		self.think = magmaexplode;
		self.nextthink = time + 5;
	}
};
/*
=============================
BLASTER TOUCH 0
============================
*/
void(vector org) BlasterTouch =
{
	self.velocity = '0 0 0';
		
	if (pointcontents(self.origin) == CONTENT_SKY)
	{
		remove(self);
		return;
	}
	else if (other.takedamage) {
			spawn_touchblood (18);
			T_Damage (other, self, self.owner, 7);

			
			}
	else
	{
		particle (self.origin, '0 0 0', 214, 20);
		puff_org = self.origin;
	}
	remove(self);
};
/*
=============================
BLASTER TOUCH 1
============================
*/
void(vector org) BlasterTouch1 =
{
	self.velocity = '0 0 0';
		
	if (pointcontents(self.origin) == CONTENT_SKY)
	{
		remove(self);
		return;
	}
	else if (other.takedamage) {
			spawn_touchblood (18);
			T_Damage (other, self, self.owner, 15);

			
			}
	else
	{
		particle (self.origin, '0 0 0', 214, 20);
		puff_org = self.origin;
	}
	remove(self);
};
/*
=============================
BLASTER TOUCH 2
============================
*/
void(vector org) BlasterTouch2 =
{
	self.velocity = '0 0 0';
		
	if (pointcontents(self.origin) == CONTENT_SKY)
	{
		remove(self);
		return;
	}
	else if (other.takedamage) {
			spawn_touchblood (18);
			T_Damage (other, self, self.owner, 36);
					}
	else
	{
		particle (self.origin, '0 0 0', 214, 20);
		puff_org = self.origin;
	}
	remove(self);
};
//The final Blast product for Blaster. I may fix up into 1 function, But for now, "self" is the projectile.
//And other doesn't work. Nor does other.owner

void(vector org) BlasterTouch3 =
{
	self.velocity = '0 0 0';
		
	if (pointcontents(self.origin) == CONTENT_SKY)
	{
		remove(self);
		return;
	}
	else if (other.takedamage) {
			spawn_touchblood (18);
			T_Damage (other, self, self.owner, 30);
			}
	else
	{
		particle (self.origin, '0 0 0', 214, 20);
		puff_org = self.origin;
	}
	remove(self);
};

/*
=============================
SNIPER TOUCH
============================
*/
void () SniperTouch =
{
	local vector p_a, p_b;
	local float zdif;
	
	self.velocity = '0 0 0';
		
	if (pointcontents(self.origin) == CONTENT_SKY)
	{
		remove(self);
		return;
	}
	else if (other.takedamage) {
		p_a_z = self.origin_z;
		p_b_z = other.origin_z;
		
		zdif = vlen(p_a - p_b);
		//_bprint(ftos(zdif),"\n");
		if (zdif > 20)
					{
			T_Damage (other, self, self.owner, 150);
			spawn_touchblood (18);
					}
		else
					{
			T_Damage (other, self, self.owner, 40);
			spawn_touchblood (18);
					}
	}
	else
	{
		particle (self.origin, '0 0 0', 251, 40);
		puff_org = self.origin;
	}
	remove(self);
};
/*
=============================
Morphball Exploding
============================
*/
void() BombExplode =
{
	local float	damg;
	
	damg = 16;
	
	if (other.health)
	{
		if (other.classname == "player")
			damg = damg = 0;
			T_Damage (other, self, self.owner, damg );
	}

	T_RadiusDamage (self, self.owner, 50, other);
	self.origin = self.origin - 8*normalize(self.velocity);
	CreateExplosion (self.origin);
	sound (self, CHAN_WEAPON, "weapons/mb_explode.wav", 1, ATTN_NORM);
	remove(self);
};

/*
=====================
End of Touch Functions
=====================
*/

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
void(float damage, vector dir) TraceAttack =
{
	local	vector	vel, org;
	
	vel = normalize(dir + v_up*crandom() + v_right*crandom());
	vel = vel + 2*trace_plane_normal;
	vel = vel * 200;

	org = trace_endpos - dir*4;

	if (trace_ent.takedamage)
	{
		SpawnBlood (org, vel*0.2, damage);
		AddMultiDamage (trace_ent, damage);
	}
	else
	{
		WriteByte (MSG_BROADCAST, SVC_TEMPENTITY);
		WriteByte (MSG_BROADCAST, TE_GUNSHOT);
		WriteCoord (MSG_BROADCAST, org_x);
		WriteCoord (MSG_BROADCAST, org_y);
		WriteCoord (MSG_BROADCAST, org_z);
	}
};

/*
================
FireBullets

Used by shotgun, super shotgun, and enemy soldier firing
Go to the trouble of combining multiple pellets into a single damage call.
================
*/
void(float shotcount, vector dir, vector spread) FireBullets =
{
	local	vector direction;
	local	vector	src;
	
	makevectors(self.v_angle);

	src = self.origin + v_forward*10;
	src_z = self.absmin_z + self.size_z * 0.7;

	ClearMultiDamage ();
	while (shotcount > 0)
	{
		direction = dir + crandom()*spread_x*v_right + crandom()*spread_y*v_up;

		traceline (src, src + direction*2048, FALSE, self);
		if (trace_fraction != 1.0)
			TraceAttack (4, direction);

		shotcount = shotcount - 1;
	}
	ApplyMultiDamage ();
};


/*
========================
MAGMA
========================
*/
void() W_FireMagma =
{
	local	entity sniper;
	blaster_flash();
	self.currentammo = self.ammo_lava = self.ammo_lava -= 1;
	sound (self, CHAN_WEAPON, "weapons/sniper.wav", 1, ATTN_NORM);
	self.punchangle_x = -3;

	sniper = spawn ();
	sniper.owner = self;
	sniper.movetype = MOVETYPE_BOUNCE;
	sniper.solid = SOLID_BBOX;
	sniper.classname = "Magma";
		
// Set The Sniper bullets speed

	makevectors (self.v_angle);
	sniper.velocity = aim(self, 1000);
	sniper.velocity = sniper.velocity * 1000;	
	sniper.angles = vectoangles(sniper.velocity);
	
	sniper.touch = magma_touch;
	
	setmodel (sniper, "progs/lavaball.mdl");
	setsize (sniper, '0 0 0', '0 0 0');		
	setorigin (sniper, self.origin + v_forward*10 + '0 0 16');
};
/*
========================
SPLASER
========================
*/
void() W_FireSplaser =
{
	local	entity sniper;
	blaster_flash();
	self.currentammo = self.ammo_nails = self.ammo_nails -= 1;
	sound (self, CHAN_WEAPON, "weapons/sniper.wav", 1, ATTN_NORM);
	self.punchangle_x = -3;

	sniper = spawn ();
	sniper.owner = self;
	sniper.movetype = MOVETYPE_FLYMISSILE;
	sniper.solid = SOLID_BBOX;
	sniper.classname = "splaser";
		
// Set The Sniper bullets speed

	makevectors (self.v_angle);
	sniper.velocity = aim(self, 1000);
	sniper.velocity = sniper.velocity * 2000;	//This is so It is fast Like a sniper Projectile
	sniper.angles = vectoangles(sniper.velocity);
	
	sniper.touch = SplaserTouch;
	
// set missile duration
	sniper.nextthink = time + 5;
	sniper.think = SUB_Remove;
	sniper.frame += 1;
	
	setmodel (sniper, "progs/splaser_muzzle.spr");
	sniper.effects = EF_DIMLIGHT;
	setsize (sniper, '0 0 0', '0 0 0');		
	setorigin (sniper, self.origin + v_forward*10 + '0 0 16');
};
/*
========================
SNIPER
========================
*/
void() W_FireSniper =
{
	local	entity sniper;
	blaster_flash();
	self.currentammo = self.ammo_sniper = self.ammo_sniper - 1;
	sound (self, CHAN_WEAPON, "weapons/sniper.wav", 1, ATTN_NORM);
	self.punchangle_x = -3;

	sniper = spawn ();
	sniper.owner = self;
	sniper.movetype = MOVETYPE_FLYMISSILE;
	sniper.solid = SOLID_BBOX;
	sniper.classname = "Sniper";
		
// Set The Sniper bullets speed

	makevectors (self.v_angle);
	sniper.velocity = aim(self, 1000);
	sniper.velocity = sniper.velocity * 10000;	//This is so It is fast Like a sniper Projectile
	sniper.angles = vectoangles(sniper.velocity);
	
	sniper.touch = SniperTouch;
	
// set missile duration
	sniper.nextthink = time + 5;
	sniper.think = SUB_Remove;
	sniper.frame += 1;
	
	setmodel (sniper, "progs/sniper.mdl");
	sniper.effects = EF_DIMLIGHT;
	setsize (sniper, '0 0 0', '0 0 0');		
	setorigin (sniper, self.origin + v_forward*30 + '0 0 16');
};
/*
================
BLASTER
================
*/
void() W_FireBlaster =
{

	local	entity plasma;
	blaster_flash();
	self.currentammo = self.ammo_blaster = self.ammo_blaster - 0;
	sound (self, CHAN_AUTO, "weapons/guncock.wav", 1, ATTN_NORM);
	self.punchangle_x = -2;

	plasma = spawn ();
	plasma.owner = self;
	plasma.movetype = MOVETYPE_FLYMISSILE;
	plasma.solid = SOLID_BBOX;
	plasma.classname = "Plasma";
		
// Set the speed of the Plasma

	makevectors (self.v_angle);
	plasma.velocity = aim(self, 1000);
	if (self.charge >= 10 && self.charge <= 39)	// Sets the Velocity for When charging the Blaster
     	plasma.velocity = plasma.velocity * 4200;
	if (self.charge >= 40 && self.charge <= 69)
     	plasma.velocity = plasma.velocity * 3100;
	if (self.charge >= 70)
     	plasma.velocity = plasma.velocity * 2000;
	else
	plasma.velocity = plasma.velocity * 4500;

	plasma.angles = vectoangles(plasma.velocity);
	
	if (self.charge >= 10 && self.charge <= 39)	// Sets the Different Damages
     	plasma.touch = BlasterTouch1;
	if (self.charge >= 40 && self.charge <= 69)
    	plasma.touch = BlasterTouch2;
	if (self.charge >= 70)
     	plasma.touch = BlasterTouch3;
	else
	plasma.touch = BlasterTouch;
	setmodel (plasma, "progs/blast.spr");
	if (self.charge >= 10 && self.charge <= 49)
	plasma.frame = 1;
	else if (self.charge >= 50)
	plasma.frame = 0;
	else
	plasma.frame = 2;

	setsize (plasma, '0 0 0', '0 0 0');		
	setorigin (plasma, self.origin + v_forward*10 + '0 0 16');
	
// set missile duration
	plasma.nextthink = time + 5;
	plasma.think = SUB_Remove;
	self.charge = 0;
};

/*
================
W_FireRic

Has 3 Functions Because It needs 3 different origins. There are 3 slots in the Richochet beam.
================
*/
void() W_FireRic =
{

	local	entity plasma;
	blaster_flash();
	if (self.charge >= 10 && self.charge <= 39)	//Sets the amount of ammo lost when CHarging
	{
	if (self.ammo_ric <= 6)
	self.currentammo = self.ammo_ric = self.ammo_ric - 1;
	else
	self.currentammo = self.ammo_ric = self.ammo_ric - 4;
	}
	else if (self.charge >= 40)
	{
	if (self.ammo_ric <= 6)
	self.currentammo = self.ammo_ric = self.ammo_ric - 1;
	else
	self.currentammo = self.ammo_ric = self.ammo_ric - 5;
	}
	else
	{
	if (self.ammo_ric <= 6)
	self.currentammo = self.ammo_ric = self.ammo_ric - 1;
	else
	self.currentammo = self.ammo_ric = self.ammo_ric - 3;
	}
	sound (self, CHAN_AUTO, "weapons/guncock.wav", 1, ATTN_NORM);
	if (self.charge >= 10 && self.charge <= 39)
	self.punchangle_x = -4;
	else if (self.charge >= 40)
	self.punchangle_x = -6;
	else
	self.punchangle_x = -2;

	plasma = spawn ();
	plasma.owner = self;
	plasma.movetype = MOVETYPE_FLYMISSILE;
	plasma.solid = SOLID_BBOX;
	plasma.classname = "ric";
		
// Set the speed of the Plasma

	makevectors (self.v_angle);
	plasma.velocity = aim(self, 1000);
	if (self.charge >= 10 && self.charge <= 39)
	plasma.velocity = plasma.velocity * 2300;
	else if (self.charge >= 40 && self.charge <= 69)
	plasma.velocity = plasma.velocity * 2500;
	else if (self.charge >= 70)
	plasma.velocity = plasma.velocity * 2700;
	else
	plasma.velocity = plasma.velocity * 2100;
	plasma.angles = vectoangles(plasma.velocity);
	
	if (self.charge >= 10 && self.charge <= 39)
	plasma.touch = ric_touch_1;
	else if (self.charge >= 40 && self.charge <= 69)
	plasma.touch = ric_touch_2;
	else if (self.charge >= 70)
	plasma.touch = ric_touch_3;
	else
	plasma.touch = ric_touch;

	if (self.charge >= 40)
	plasma.lives = 2 + 4 * random();
	else
	plasma.lives = 2 + 2 * random();
	
// set missile duration
	plasma.nextthink = time + 5;
	plasma.think = SUB_Remove;

	setmodel (plasma, "progs/ric_beam.mdl");
	setsize (plasma, '0 0 0', '0 0 0');		
	setorigin (plasma, self.origin + v_forward * 22 + v_right * 10.5 + '0 0 7');
};

void() W_FireRic2 =
{

	local	entity plasma;

	plasma = spawn ();
	plasma.owner = self;
	plasma.movetype = MOVETYPE_FLYMISSILE;
	plasma.solid = SOLID_BBOX;
	plasma.classname = "ric";
		
// Set the speed of the Plasma

	makevectors (self.v_angle);
	plasma.velocity = aim(self, 1000);
	if (self.charge >= 10 && self.charge <= 39)
	plasma.velocity = plasma.velocity * 2300;
	else if (self.charge >= 40 && self.charge <= 69)
	plasma.velocity = plasma.velocity * 2500;
	else if (self.charge >= 70)
	plasma.velocity = plasma.velocity * 2700;
	else
	plasma.velocity = plasma.velocity * 2100;
	plasma.angles = vectoangles(plasma.velocity);
	
	if (self.charge >= 10 && self.charge <= 39)
	plasma.touch = ric_touch_1;
	else if (self.charge >= 40 && self.charge <= 69)
	plasma.touch = ric_touch_2;
	else if (self.charge >= 70)
	plasma.touch = ric_touch_3;
	else
	plasma.touch = ric_touch;

	if (self.charge >= 40)
	plasma.lives = 2 + 4 * random();
	else
	plasma.lives = 2 + 2 * random();
	
// set missile duration
	plasma.nextthink = time + 5;
	plasma.think = SUB_Remove;

	setmodel (plasma, "progs/ric_beam.mdl");
	setsize (plasma, '0 0 0', '0 0 0');		
	setorigin (plasma, self.origin + v_forward * 22 + v_right * 3.5 + '0 0 7');
};

void() W_FireRic3 =
{

	local	entity plasma;

	plasma = spawn ();
	plasma.owner = self;
	plasma.movetype = MOVETYPE_FLYMISSILE;
	plasma.solid = SOLID_BBOX;
	plasma.classname = "ric";
		
// Set the speed of the Plasma

	makevectors (self.v_angle);
	plasma.velocity = aim(self, 1000);
	if (self.charge >= 10 && self.charge <= 39)
	plasma.velocity = plasma.velocity * 2300;
	else if (self.charge >= 40 && self.charge <= 69)
	plasma.velocity = plasma.velocity * 2500;
	else if (self.charge >= 70)
	plasma.velocity = plasma.velocity * 2700;
	else
	plasma.velocity = plasma.velocity * 2100;
	plasma.angles = vectoangles(plasma.velocity);
	
	if (self.charge >= 10 && self.charge <= 39)
	plasma.touch = ric_touch_1;
	else if (self.charge >= 40 && self.charge <= 69)
	plasma.touch = ric_touch_2;
	else if (self.charge >= 70)
	plasma.touch = ric_touch_3;
	else
	plasma.touch = ric_touch;

	if (self.charge >= 40)
	plasma.lives = 2 + 4 * random();
	else
	plasma.lives = 2 + 2 * random();
	
// set missile duration
	plasma.nextthink = time + 5;
	plasma.think = SUB_Remove;

	setmodel (plasma, "progs/ric_beam.mdl");	
	setsize (plasma, '0 0 0', '0 0 0');		
	setorigin (plasma, self.origin + v_forward * 18 + v_right * 17.5 + '0 0 7');
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
	local	entity missile;
	if (self.charge >= 10 && self.charge < 40)
	self.currentammo = self.ammo_rockets = self.ammo_rockets - 2;
	else if (self.charge >= 40 && self.charge < 70)
	self.currentammo = self.ammo_rockets = self.ammo_rockets - 3;
	else if (self.charge >= 70)
	self.currentammo = self.ammo_rockets = self.ammo_rockets - 5;
	else
	self.currentammo = self.ammo_rockets = self.ammo_rockets - 1;
	if (self.ammo_rockets == 0)
		self.weapon = IT_BLASTER;
	
	sound (self, CHAN_WEAPON, "weapons/sgun1.wav", 1, ATTN_NORM);
	if (self.charge >= 40 && self.charge < 70)
	self.punchangle_x = -4;
	else if (self.charge >= 70)
	self.punchangle_x = -7;
	else
	self.punchangle_x = -2;

	missile = spawn ();
	missile.owner = self;
	missile.movetype = MOVETYPE_FLYMISSILE;
	missile.solid = SOLID_BBOX;
	missile.classname = "missile";
		
// set missile speed	

	if (self.charge >= 10 && self.charge < 40)	//Dang, I messed up with making some 39 and 69 :p
	{
	makevectors (self.v_angle);
	missile.velocity = aim(self, 1000);
	missile.velocity = missile.velocity * 1100;
	missile.angles = vectoangles(missile.velocity);
	}
	else if (self.charge >= 40 && self.charge < 70)		
	{
	makevectors (self.v_angle);
	missile.velocity = aim(self, 1000);
	missile.velocity = missile.velocity * 1200;
	missile.angles = vectoangles(missile.velocity);
	}
	else if (self.charge >= 70)		
	{
	makevectors (self.v_angle);
	missile.velocity = aim(self, 1000);
	missile.velocity = missile.velocity * 1500;
	missile.angles = vectoangles(missile.velocity);
	}
	else
	{
	makevectors (self.v_angle);
	missile.velocity = aim(self, 1000);
	missile.velocity = missile.velocity * 1000;
	missile.angles = vectoangles(missile.velocity);
	}
	
		if (self.charge >= 10 && self.charge < 40)
	missile.touch = Rocket_Explode1;
		else if (self.charge >= 40 && self.charge < 70)
	missile.touch = Rocket_Explode2;
		else if (self.charge >= 70)
	missile.touch = Rocket_Explode3;
		else
	missile.touch = Rocket_Explode0;
	
// set missile duration
	missile.nextthink = time + 5;
	missile.think = SUB_Remove;

	setmodel (missile, "progs/missile.mdl");
	setsize (missile, '0 0 0', '0 0 0');		
	setorigin (missile, self.origin + v_forward*8 + '0 0 16');	
};

/*
===============================================================================

LIGHTNING

===============================================================================
*/

/*
=================
LightningDamage
=================
*/
void(vector p1, vector p2, entity from, float damage) LightningDamage =
{
	local entity		e1, e2;
	local vector		f;
	
	f = p2 - p1;
	normalize (f);
	f_x = 0 - f_y;
	f_y = f_x;
	f_z = 0;
	f = f*16;

	e1 = e2 = world;

	traceline (p1, p2, FALSE, self);
	if (trace_ent.takedamage)
	{
		particle (trace_endpos, '0 0 100', 225, damage*4);
		T_Damage (trace_ent, from, from, damage);
		if (self.classname == "player")
		{
			if (other.classname == "player")
				trace_ent.velocity_z = trace_ent.velocity_z + 400;
		}
	}
	e1 = trace_ent;

	traceline (p1 + f, p2 + f, FALSE, self);
	if (trace_ent != e1 && trace_ent.takedamage)
	{
		particle (trace_endpos, '0 0 100', 225, damage*4);
		T_Damage (trace_ent, from, from, damage);
	}
	e2 = trace_ent;

	traceline (p1 - f, p2 - f, FALSE, self);
	if (trace_ent != e1 && trace_ent != e2 && trace_ent.takedamage)
	{
		particle (trace_endpos, '0 0 100', 225, damage*4);
		T_Damage (trace_ent, from, from, damage);
	}
};


void() W_FireLightning =
{
	local	vector		org;
	local	float		cells;

	if (self.ammo_cells < 1)
	{
		//self.weapon = W_BestWeapon ();
		W_SetCurrentAmmo ();
		return;
	}

// explode if under water
	if (self.waterlevel > 1)
	{
		cells = self.ammo_cells;
		self.ammo_cells = 0;
		W_SetCurrentAmmo ();
		T_RadiusDamage (self, self, 35*cells, world);
		return;
	}

	if (self.t_width < time)
	{
		sound (self, CHAN_WEAPON, "weapons/lhit.wav", 1, ATTN_NORM);
		self.t_width = time + 0.6;
	}
	self.punchangle_x = -2;

	self.currentammo = self.ammo_cells = self.ammo_cells - 1;

	org = self.origin + '0 0 16';
	
	traceline (org, org + v_forward*600, TRUE, self);

	WriteByte (MSG_BROADCAST, SVC_TEMPENTITY);
	WriteByte (MSG_BROADCAST, TE_LIGHTNING2);
	WriteEntity (MSG_BROADCAST, self);
	WriteCoord (MSG_BROADCAST, org_x);
	WriteCoord (MSG_BROADCAST, org_y);
	WriteCoord (MSG_BROADCAST, org_z);
	WriteCoord (MSG_BROADCAST, trace_endpos_x);
	WriteCoord (MSG_BROADCAST, trace_endpos_y);
	WriteCoord (MSG_BROADCAST, trace_endpos_z);

	LightningDamage (self.origin, trace_endpos + v_forward*4, self, 30);
};


//=============================================================================


void() GrenadeExplode =
{
	T_RadiusDamage (self, self.owner, 120, world);

	WriteByte (MSG_BROADCAST, SVC_TEMPENTITY);
	WriteCoord (MSG_BROADCAST, self.origin_x);
	WriteCoord (MSG_BROADCAST, self.origin_y);
	WriteCoord (MSG_BROADCAST, self.origin_z);

	CreateExplosion (self.origin);
};

void() GrenadeTouch =
{
	if (other == self.owner)
		return;		// don't explode on owner
	if (other.takedamage == DAMAGE_AIM)
	{
		GrenadeExplode();
		return;
	}
	sound (self, CHAN_WEAPON, "weapons/bounce.wav", 1, ATTN_NORM);	// bounce sound
	if (self.velocity == '0 0 0')
		self.avelocity = '0 0 0';
};

/*
================
W_FireGrenade
================
*/
void() W_FireGrenade =
{
	local	entity missile;
	
	self.currentammo = self.ammo_rockets = self.ammo_rockets - 1;
	
	sound (self, CHAN_WEAPON, "weapons/grenade.wav", 1, ATTN_NORM);

	self.punchangle_x = -2;

	missile = spawn ();
	missile.owner = self;
	missile.movetype = MOVETYPE_BOUNCE;
	missile.solid = SOLID_BBOX;
	missile.classname = "grenade";
		
// set missile speed	

	makevectors (self.v_angle);

	if (self.v_angle_x)
		missile.velocity = v_forward*600 + v_up * 200 + crandom()*v_right*10 + crandom()*v_up*10;
	else
	{
		missile.velocity = aim(self, 10000);
		missile.velocity = missile.velocity * 600;
		missile.velocity_z = 200;
	}

	missile.avelocity = '300 300 300';

	missile.angles = vectoangles(missile.velocity);
	
	missile.touch = GrenadeTouch;
	
// set missile duration
	missile.nextthink = time + 2.5;
	missile.think = GrenadeExplode;

	setmodel (missile, "progs/grenade.mdl");
	setsize (missile, '0 0 0', '0 0 0');		
	setorigin (missile, self.origin);
};
//For regenerating Your Bombs
void() mbomb1 =
{
if (self.morphbombs == 3)
 self.morphbombs += 1;
if (self.morphbombs == 2)
 self.morphbombs += 2;
if (self.morphbombs == 1)
 self.morphbombs += 3;
};

void() fire_morphbomb =
{
	local	entity missile;
	self.currentammo = self.morphbombs = self.morphbombs - 1;
	sound (self, CHAN_WEAPON, "weapons/mb_bomb.wav", 1, ATTN_NORM);

	missile = spawn ();
	missile.owner = self;
	missile.movetype = MOVETYPE_BOUNCE;
	missile.solid = SOLID_BBOX;
	missile.classname = "Mbomb";
		
// set missile speed	

	makevectors (self.v_angle);

	missile.avelocity = '0 0 0';

	missile.angles = vectoangles(missile.velocity);
	
	
// set missile duration
	missile.nextthink = time + 2.5;
	missile.think = BombExplode;
	
	self.think = mbomb1;
	self.nextthink = time + 2.5;
	missile.effects = EF_DIMLIGHT;
	setmodel (missile, "progs/mbomb.mdl");
	setsize (missile, '0 0 0', '0 0 0');		
	setorigin (missile, self.origin + v_up * 8);
};


//=============================================================================

void() spike_touch;
void() superspike_touch;


/*
===============
launch_spike

Used for both the player and the ogre
===============
*/
void(vector org, vector dir) launch_spike =
{
	newmis = spawn ();
	newmis.owner = self;
	newmis.movetype = MOVETYPE_FLYMISSILE;
	newmis.solid = SOLID_BBOX;

	newmis.angles = vectoangles(dir);
	
	newmis.touch = spike_touch;
	newmis.classname = "spike";
	newmis.think = SUB_Remove;
	newmis.nextthink = time + 6;
	setmodel (newmis, "progs/spike.mdl");
	setsize (newmis, VEC_ORIGIN, VEC_ORIGIN);		
	setorigin (newmis, org);

	newmis.velocity = dir * 1000;
};

void() W_FireSuperSpikes =
{
	local vector	dir;
	
	sound (self, CHAN_WEAPON, "weapons/spike2.wav", 1, ATTN_NORM);
	self.attack_finished = time + 0.2;
	self.currentammo = self.ammo_nails = self.ammo_nails - 2;
	dir = aim (self, 1000);
	launch_spike (self.origin + '0 0 16', dir);
	newmis.touch = superspike_touch;
	setmodel (newmis, "progs/s_spike.mdl");
	setsize (newmis, VEC_ORIGIN, VEC_ORIGIN);		
	self.punchangle_x = -2;
};

void(float ox) W_FireSpikes =
{
	local vector	dir;
	
	makevectors (self.v_angle);
	
	if (self.ammo_nails >= 2 && self.weapon == IT_SNIPER)
	{
		W_FireSuperSpikes ();
		return;
	}

	if (self.ammo_nails < 1)
	{
		//self.weapon = W_BestWeapon ();
		W_SetCurrentAmmo ();
		return;
	}

	sound (self, CHAN_WEAPON, "weapons/rocket1i.wav", 1, ATTN_NORM);
	self.attack_finished = time + 0.2;
	self.currentammo = self.ammo_nails = self.ammo_nails - 1;
	dir = aim (self, 1000);
	launch_spike (self.origin + '0 0 16' + v_right*ox, dir);

	self.punchangle_x = -2;
};



void() spike_touch =
{
	if (other == self.owner)
		return;

	if (other.solid == SOLID_TRIGGER)
		return;	// trigger field, do nothing

	if (pointcontents(self.origin) == CONTENT_SKY)
	{
		remove(self);
		return;
	}
	
// hit something that bleeds
	if (other.takedamage)
	{
		spawn_touchblood (18);
		T_Damage (other, self, self.owner, 18);
	}
	else
	{
		WriteByte (MSG_BROADCAST, SVC_TEMPENTITY);
		WriteByte (MSG_BROADCAST, TE_SUPERSPIKE);
		WriteCoord (MSG_BROADCAST, self.origin_x);
		WriteCoord (MSG_BROADCAST, self.origin_y);
		WriteCoord (MSG_BROADCAST, self.origin_z);
	}

	remove(self);

};


void() superspike_touch =
{
	if (other == self.owner)
		return;

	if (other.solid == SOLID_TRIGGER)
		return;	// trigger field, do nothing

	if (pointcontents(self.origin) == CONTENT_SKY)
	{
		remove(self);
		return;
	}
	
// hit something that bleeds
	if (other.takedamage)
	{
		spawn_touchblood (18);
		T_Damage (other, self, self.owner, 18);
	}
	else
	{
		WriteByte (MSG_BROADCAST, SVC_TEMPENTITY);
		WriteByte (MSG_BROADCAST, TE_SUPERSPIKE);
		WriteCoord (MSG_BROADCAST, self.origin_x);
		WriteCoord (MSG_BROADCAST, self.origin_y);
		WriteCoord (MSG_BROADCAST, self.origin_z);
	}

	remove(self);

};


/*
===============================================================================

PLAYER WEAPON USE

===============================================================================
*/

void() W_SetCurrentAmmo =
{
	if (self.weapon == IT_MORPHBALL)
	return;

{
	player_run ();		// get out of any weapon firing states

	self.items = self.items - ( self.items & (IT_SHELLS | IT_NAILS | IT_ROCKETS | IT_CELLS) );
	
	if (self.weapon == IT_BLASTER)
	{
	if (self.weapon == IT_MORPHBALL)
		{
		return;
		}
		if(!self.semi)
		{
		self.currentammo = self.ammo_blaster;
		self.weaponmodel = "progs/v_shot.mdl";
		self.weaponframe = 0;		
		sound (self, CHAN_WEAPON, "weapons/blaster_transform.wav", 1, ATTN_NORM);
		player_missle27();
		}
	}	
	else if (self.weapon == IT_RIC)
	{
		if (self.weapon == IT_MORPHBALL)
		{
		return;
		}
		self.currentammo = self.ammo_ric;
		self.weaponmodel = "progs/v_shot.mdl";
		player_missle37();
		self.attack_finished = time + 1.5;
	}
	else if (self.weapon == IT_ROCKET)
	{
		if (self.weapon == IT_MORPHBALL)
		{
		return;
		}
		self.currentammo = self.ammo_rockets;
		self.weaponmodel = "progs/v_shot.mdl";
		sound (self, CHAN_WEAPON, "weapons/rocket_transform.wav", 1, ATTN_NORM);
		player_missle1();
		self.attack_finished = time + 1.5;
	}
	else if (self.weapon == IT_SPLASER)
	{
		if (self.weapon == IT_MORPHBALL)
		{
		return;
		}
		self.currentammo = self.ammo_nails;
		self.weaponmodel = "progs/v_shot.mdl";
		self.weaponframe = 0;
	}
	else if (self.weapon == IT_SNIPER)
	{
		if (self.weapon == IT_MORPHBALL)
		{
		return;
		}
		self.currentammo = self.ammo_sniper;
		self.weaponmodel = "progs/v_shot.mdl";
		self.weaponframe = 0;
		self.items = self.items | IT_NAILS;
	}
	else if (self.weapon == IT_GRENADE_LAUNCHER)
	{
		//self.currentammo = self.ammo_rockets;
		//self.weaponmodel = "progs/v_rock.mdl";
		self.currentammo = self.morphbombs;
		self.weaponframe = 0;
		//self.items = self.items | IT_ROCKETS;
	}
	else if (self.weapon == IT_MAGMA)
	{
		if (self.weapon == IT_MORPHBALL)
		{
		return;
		}
		self.currentammo = self.ammo_lava;
		self.weaponmodel = "progs/v_shot.mdl";
		self.weaponframe = 0;
		self.items = self.items | IT_ROCKETS;
	}
	else if (self.weapon == IT_LIGHTNING)
	{
		self.currentammo = self.ammo_cells;
		self.weaponmodel = "progs/v_light.mdl";
		self.weaponframe = 0;
		self.items = self.items | IT_CELLS;
	}
	else
	{
		self.currentammo = 0;
		self.weaponframe = 0;
	}
 }
};
float() W_CheckNoAmmo =
{
	if (self.currentammo > 0)
		return TRUE;

	if (self.weapon == IT_MORPHBALL)
		return TRUE;
	
	W_SetCurrentAmmo ();
	
// drop the weapon down
	return FALSE;
};

/*
============
W_Attack

An attack impulse can be triggered now
============
*/
void()	player_axe1;
void()	player_axeb1;
void()	player_axec1;
void()	player_axed1;
void()	player_shot1;
void()	player_nail1;
void()	player_light1;
void()	player_rocket1;
void()	FireAnimations;	//A function that Is becoming less useable as the game goes on...Sigh
void() 	player_missle14;	//Shooting Animations for Rocket Launcher
void() 	player_missle45;	//Shooting Animations for Richochet beam
void()	player_missle56;	//Shooting Animations for Blaster
void() W_Attack =
{
	if (!W_CheckNoAmmo ())
		return;

	makevectors	(self.v_angle);			// calculate forward angle for velocity
	self.show_hostile = time + 1;	// wake monsters up
	

	if (self.weapon == IT_MORPHBALL)
	{
	if (self.morphbombs <= 1)
	return;
	fire_morphbomb();
	self.attack_finished = time + 0.6;
	}
	else if (self.weapon == IT_BLASTER)
	{
		if (self.weapon == IT_MORPHBALL)
		{
		return;
		}
		else
		{
		if (!self.semi)
		{
		W_FireBlaster();
		player_missle56();
		self.semi = 1;
		self.attack_finished = time + 0.12;
		}
	}
}
	else if (self.weapon == IT_RIC)
	{
		if (self.weapon == IT_MORPHBALL)
		{
		return;
		}
		else
		{
		
         if(!self.semi)
		 {
	if (self.ammo_ric <= 6)
		W_FireRic();
		else
		{
		W_FireRic();
		W_FireRic2();
		W_FireRic3();
		}
         player_missle45();
          self.semi = 1; // Semiauto
          self.attack_finished = time + 0.6; // Faster
          }
		}
	}
	

	else if (self.weapon == IT_ROCKET)
	{
		if (self.weapon == IT_MORPHBALL)
		{
		return;
		}

		else
		{
		 if(!self.semi)
			{
		player_missle14();
		W_FireRocket();
		self.semi = 1;
		self.attack_finished = time + 0.7;
			}
		}
	}
	else if (self.weapon == IT_SPLASER)
	{
	if (self.weapon == IT_MORPHBALL)
		{
		return;
		}

		else
		{
		 if(!self.semi)
			{
		FireAnimations();
		self.semi = 1;
		self.attack_finished = time + 0.8;
			}
		}
	}
	else if (self.weapon == IT_SNIPER)
	{
		if (self.weapon == IT_MORPHBALL)
		{
		return;
		}
		FireAnimations();
		self.attack_finished = time + 1;
	}
	else if (self.weapon == IT_GRENADE_LAUNCHER)
	{
	fire_morphbomb();
	self.attack_finished = time + 0.6;
	}
	else if (self.weapon == IT_MAGMA)
	{	
		if (self.weapon == IT_MORPHBALL)
		{
		return;
		}
		FireAnimations();
		W_FireMagma();
		self.attack_finished = time + 0.7;
	}
	else if (self.weapon == IT_LIGHTNING)
	{
		player_light1();
		self.attack_finished = time + 0.1;
		sound (self, CHAN_AUTO, "weapons/lstart.wav", 1, ATTN_NORM);
	}
};

/*
============
W_ChangeWeapon

============
*/
void() W_ChangeWeapon =
{
	local	float	it, am, fl;
	
	it = self.items;
	am = 0;
	
	if (self.impulse == 1)
	{
		fl = IT_MORPHBALL;
	}
	else if (self.impulse == 2)
	{
		//if (self.weapon == IT_RIC | IT_ROCKET | IT_SNIPER | IT_SPLASER | IT_MAGMA);
		//player_missle27();
		fl = IT_BLASTER;
		if (self.ammo_shells < 1)
			am = 1;
	}
	else if (self.impulse == 3)
	{
		fl = IT_ROCKET;
		if (self.ammo_shells < 2)
			am = 1;
	}		
	//else if (self.impulse == 4)
	//{
		//fl = IT_SPLASER;
		//if (self.ammo_nails < 1)
			//am = 1;
	//}
	else if (self.impulse == 5)
	{
		fl = IT_SNIPER;
		if (self.ammo_sniper < 2)
			am = 1;
	}
	//else if (self.impulse == 6)
	//{
	//	fl = IT_GRENADE_LAUNCHER;
	//	if (self.ammo_rockets < 1)
	//		am = 1;
	//}
	else if (self.impulse == 7)
	{
		fl = IT_MAGMA;
		if (self.ammo_lava < 1)
			am = 1;
	}
	else if (self.impulse == 8)
	{
		fl = IT_LIGHTNING;
		if (self.ammo_cells < 1)
			am = 1;
	}
	self.impulse = 0;
	
	if (!(self.items & fl))
	{	// don't have the weapon or the ammo
		sprint (self, "no weapon.\n");
		return;
	}
	
	if (am)
	{	// don't have the ammo
		sprint (self, "not enough ammo.\n");
		return;
	}

//
// set weapon, set ammo
//
	self.weapon = fl;		
	W_SetCurrentAmmo ();

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

	self.ammo_rockets = 100;
	self.ammo_nails = 200;
	self.ammo_shells = 100;
	self.items = self.items | 
		IT_MORPHBALL |
		IT_BLASTER |
		IT_ROCKET |
		IT_SPLASER |
		IT_SNIPER |
		IT_GRENADE_LAUNCHER |
		IT_MAGMA |
		IT_RIC |
		IT_KEY1 | IT_KEY2;
		

	self.ammo_cells = 200;
	self.items = self.items | IT_LIGHTNING;

	self.weapon = IT_MAGMA;
	self.impulse = 0;
	W_SetCurrentAmmo ();
};

/*
============
CycleWeaponCommand

Go to the next weapon with ammo
============
*/
void() CycleWeaponCommand =
{
	local	float	it, am;
	
	it = self.items;
	self.impulse = 0;
	
	while (1)
	{
		am = 0;

		if (self.weapon == IT_LIGHTNING)
		{  
			player_missle27();
			self.weapon = IT_BLASTER;
			if (self.ammo_blaster < 1)
				am = 1;
		}
		else if (self.weapon == IT_BLASTER)
		{
			self.weapon = IT_RIC;
			if (self.ammo_ric < 2)
				am = 1;
		}		
		else if (self.weapon == IT_RIC)
		{
			self.weapon = IT_ROCKET;
			if (self.ammo_rockets < 1)
				am = 1;
		}
		else if (self.weapon == IT_ROCKET)
		{
			self.weapon = IT_SPLASER;
			if (self.ammo_nails < 1)
				am = 1;
		}
		else if (self.weapon == IT_SPLASER)
		{
			self.weapon = IT_SNIPER;
			if (self.ammo_sniper < 1)
				am = 1;
		}
		else if (self.weapon == IT_SNIPER)
		{
			self.weapon = IT_MAGMA;
			if (self.ammo_lava < 1)
				am = 1;
		}
		//else if (self.weapon == IT_GRENADE_LAUNCHER)
		//{
		//	self.weapon = IT_MAGMA;
		//	if (self.ammo_lava < 1)
		//		am = 1;
		//}
		else if (self.weapon == IT_MAGMA)
		{
			self.weapon = IT_LIGHTNING;
			if (self.ammo_cells < 1)
				am = 1;
		}
	
		if ( (it & self.weapon) && am == 0)
		{
			W_SetCurrentAmmo ();
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
	local	float	it, am;
	
	it = self.items;
	self.impulse = 0;

	while (1)
	{
		am = 0;

		if (self.weapon == IT_LIGHTNING)
		{
			self.weapon = IT_MAGMA;
			if (self.ammo_lava < 1)
				am = 1;
		}
		else if (self.weapon == IT_MAGMA)
		{
			self.weapon = IT_SNIPER;
			if (self.ammo_sniper < 1)
				am = 1;
		}
		//else if (self.weapon == IT_GRENADE_LAUNCHER)
		//{
		//	self.weapon = IT_SNIPER;
		//	if (self.ammo_sniper < 1)
		//		am = 1;
		//}
		else if (self.weapon == IT_SNIPER)
		{
			self.weapon = IT_SPLASER;
			if (self.ammo_nails < 1)
				am = 1;
		}
		else if (self.weapon == IT_SPLASER)
		{
			self.weapon = IT_ROCKET;
			if (self.ammo_shells < 2)
				am = 1;
		}
				
		else if (self.weapon == IT_ROCKET)
		{
			self.weapon = IT_BLASTER;
			if (self.ammo_blaster < 1)
				am = 1;
		}
		else if (self.weapon == IT_BLASTER)
		{
			self.weapon = IT_MORPHBALL;
		}
		else if (self.weapon == IT_MORPHBALL)
		{
			self.weapon = IT_LIGHTNING;
			if (self.ammo_cells < 1)
				am = 1;
		}
	
		if ( (it & self.weapon) && am == 0)
		{
			W_SetCurrentAmmo ();
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
	serverflags = serverflags * 2 + 1;
};

void() QuadCheat =
{
	if (deathmatch || coop)
		return;
	self.super_time = 1;
	self.super_damage_finished = time + 30;
	self.items = self.items | IT_QUAD;
	dprint ("quad cheat\n");
};
void() PlayerJump;
/*
============
ImpulseCommands

============
*/
void() ImpulseCommands =
{
	if (self.impulse >= 1 && self.impulse <= 8)
		W_ChangeWeapon ();		
	if (self.impulse == 9)
		CheatCommand ();
	if (self.impulse == 10)
			{
		CycleWeaponCommand ();
		Set_FOV ( FOV_DEFAULT );
		self.pfov = FOV_DEFAULT;
			}
	if (self.impulse == 11)
		ServerflagsCommand ();
	if (self.impulse == 12)
			{
		CycleWeaponReverseCommand ();
		Set_FOV ( FOV_DEFAULT );
		self.pfov = FOV_DEFAULT;
			}
    if (self.impulse == 15)
			{ 
		if (self.health < BROKENITEMS || self.button0 || !self.flags & FL_ONGROUND)
		return;
		if (self.weapon != IT_MORPHBALL)
		{
		self.charge = 0;
		self.pfov = FOV_DEFAULT;
		setsize (self, '-10 -10 -24', '10 10 10');
		self.weapon = IT_MORPHBALL;
		self.morphbombs = 4;
		self.mballset = 1;
		self.currentammo = self.morphbombs;
		self.boostlives = 1;
		self.morphbombs = 4;
		sound (self, CHAN_WEAPON, "weapons/morphball.wav", 1, ATTN_NORM);
		stuffcmd (self, "chase_active 1");
		self.attack_finished = time + 1;
		}
		else if (self.weapon == IT_MORPHBALL)
		{
		self.charge = 0;
		self.pfov = FOV_DEFAULT;
		setorigin (self, self.origin + v_up * 20);
		setsize (self, '-16 -16 -24', '16 16 32');
		self.mballset = 0;
		self.weapon = IT_BLASTER;
		stuffcmd (self, "chase_active 0");
		 W_SetCurrentAmmo ();	
		self.attack_finished = time + 1;
		}
			}
	if (self.impulse == 17)
		{
			if (self.weapon == IT_SNIPER)
					{
					if (self.weapon == IT_MORPHBALL)
					return;
				WeaponZoom();
					}
			if (self.weapon == IT_MORPHBALL)
				boost();
		}
	if (self.impulse == 255)
		QuadCheat ();

	self.impulse = 0;
};
/*
============
W_WeaponFrame

Called every frame so impulse events can be handled as well as possible
============
*/
void() W_WeaponFrame =
{
   if (!self.button0)
           self.semi = 0; 
         
   if (time < self.attack_finished)
      return;

      ImpulseCommands ();  // check for attack
   
   //if (self.button0) // Whats funny Is That You don't even need to Press the Button!
  // {
	/*
===============================================
	BLASTER
==================================	
	*/
     if (self.weapon == IT_BLASTER)
     {	
      if (self.charge < 10)
         {
        self.charge = self.charge + 1;
         }
	
      if (self.charge >= 10)
      if (self.charge < 20)
         {
      self.charge = self.charge + 1;
         }

      if (self.charge >= 20)
      if (self.charge < 30)
         {
         self.charge = self.charge + 1;
         }
      if (self.charge >= 30)
      if (self.charge < 40)
         {
         self.charge = self.charge + 1;
         }
	if (self.charge >= 40)
      if (self.charge < 50)
         {
         self.charge = self.charge + 1;
         }
	if (self.charge >= 50)
      if (self.charge < 60)
         {
         self.charge = self.charge + 1;
         }	
	if (self.charge >= 60)
      if (self.charge < 70)
         {
         self.charge = self.charge + 1;
         }
	if (self.charge >= 70)
         {
	if (self.weapon == IT_MORPHBALL)	//If you turn into Morphball, Then Have no Charge
	{self.charge = 0;}
		else
		{
         self.charge = self.charge + 1;
        sprint(self, "Fully charged\n");	
		}
         }
     
      if (self.charge < 10 && !self.button0)
      if (self.charge >= 1 && !self.button0)           // no rapid fire
         {
         self.charge = 0;
         }

        if (!self.button0 && self.charge >= 10)         // you released the button
         {
	if (self.weapon == IT_MORPHBALL)
		return;
	if (!self.semi)
			{
	W_FireBlaster();   
	self.charge = 0;
      player_missle56();
	self.semi = 0;
      self.attack_finished = time + 0.12;
			}
         }
	}
/*
===============================================
	RICHOCHET
==================================	
*/
     if (self.weapon == IT_RIC)
     {	
      if (self.charge < 10)
         {
        self.charge = self.charge + 1;
         }
	
      if (self.charge >= 10)
      if (self.charge < 20)
         {
      self.charge = self.charge + 1;
         }

      if (self.charge >= 20)
      if (self.charge < 30)
         {
         self.charge = self.charge + 1;
         }
      if (self.charge >= 30)
      if (self.charge < 40)
         {
         self.charge = self.charge + 1;
         }
	if (self.charge >= 40)
      if (self.charge < 50)
         {
         self.charge = self.charge + 1;
         }
	if (self.charge >= 50)
      if (self.charge < 60)
         {
         self.charge = self.charge + 1;
         }	
	if (self.charge >= 60)
      if (self.charge < 70)
         {
         self.charge = self.charge + 1;
         }
	if (self.charge >= 70)
         {
	if (self.weapon == IT_MORPHBALL)	//If you turn into Morphball, Then Have no Charge
	{self.charge = 0;}
		else
		{
         self.charge = self.charge + 1;
        sprint(self, "Fully charged\n");	
		}
         }
     
      if (self.charge < 10 && !self.button0)
      if (self.charge >= 1 && !self.button0)           // no rapid fire
         {
         self.charge = 0;
         }

        if (!self.button0 && self.charge >= 10)         // you released the button
         {
	if (self.weapon == IT_MORPHBALL)
		return;
	if (!self.semi)
			{
	W_FireRic();   
	self.charge = 0;
      player_missle45();
	self.semi = 0;
      self.attack_finished = time + 0.7;
			}
         }
	}

/*
===============================================
ROCKET LAUNCHER
==================================	
*/
     if (self.weapon == IT_ROCKET)
     {	
      if (self.charge < 10)
         {
        self.charge = self.charge + 1;
         }
	
      if (self.charge >= 10)
      if (self.charge < 20)
         {
      self.charge = self.charge + 1;
         }

      if (self.charge >= 20)
      if (self.charge < 30)
         {
         self.charge = self.charge + 1;
         }
      if (self.charge >= 30)
      if (self.charge < 40)
         {
         self.charge = self.charge + 1;
         }
	if (self.charge >= 40)
      if (self.charge < 50)
         {
         self.charge = self.charge + 1;
         }
	if (self.charge >= 50)
      if (self.charge < 60)
         {
         self.charge = self.charge + 1;
         }	
	if (self.charge >= 60)
      if (self.charge < 70)
         {
         self.charge = self.charge + 1;
         }
	if (self.charge >= 70)
         {
	if (self.weapon == IT_MORPHBALL)	//If you turn into Morphball, Then Have no Charge
	{self.charge = 0;}
		else
		{
         self.charge = self.charge + 1;
        sprint(self, "Fully charged\n");	
		}
         }
     
      if (self.charge < 10 && !self.button0)
      if (self.charge >= 1 && !self.button0)           // no rapid fire
         {
         self.charge = 0;
         }

        if (!self.button0 && self.charge >= 10)         // you released the button
         {
	if (self.weapon == IT_MORPHBALL)
		return;
	if (!self.semi)
			{
	W_FireRocket();   
	self.charge = 0;
     player_missle14();
	self.semi = 0;
      self.attack_finished = time + 0.7;
			}
         }
	}


	if (self.button0)
	{
      SuperDamageSound ();
      W_Attack ();
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
 