/*
==============================================================================

WIZARD

==============================================================================
*/

$cd id1/models/a_wizard
$origin 0 0 24
$base wizbase	
$skin wizbase

$frame hover1 hover2 hover3 hover4 hover5 hover6 hover7 hover8
$frame hover9 hover10 hover11 hover12 hover13 hover14 hover15

$frame fly1 fly2 fly3 fly4 fly5 fly6 fly7 fly8 fly9 fly10
$frame fly11 fly12 fly13 fly14

$frame magatt1 magatt2 magatt3 magatt4 magatt5 magatt6 magatt7
$frame magatt8 magatt9 magatt10 magatt11 magatt12 magatt13

$frame pain1 pain2 pain3 pain4

$frame death1 death2 death3 death4 death5 death6 death7 death8

$frame idel1 idel2 idel3 idel4 idel5 idel6 idel7 idel8 idel9

/*
==============================================================================

WIZARD

If the player moves behind cover before the missile is launched, launch it
at the last visible spot with no velocity leading, in hopes that the player
will duck back out and catch it.
==============================================================================
*/



void() met_run1;
void() met_side1;

/*
=================
WizardCheckAttack
=================
*/
float()	WizardCheckAttack =
{
	local vector	spot1, spot2;	
	local entity	targ;
	local float		chance;

	if (time < self.attack_finished)
		return FALSE;
	if (!enemy_vis)
		return FALSE;

	if (enemy_range == RANGE_FAR)
	{
		if (self.attack_state != AS_STRAIGHT)
		{
			self.attack_state = AS_STRAIGHT;
			met_run1 ();
		}
		return FALSE;
	}
		
	targ = self.enemy;
	
// see if any entities are in the way of the shot
	spot1 = self.origin + self.view_ofs;
	spot2 = targ.origin + targ.view_ofs;

	traceline (spot1, spot2, FALSE, self);

	if (trace_ent != targ)
	{	// don't have a clear shot, so move to a side
		if (self.attack_state != AS_STRAIGHT)
		{
			self.attack_state = AS_STRAIGHT;
			met_run1 ();
		}
		return FALSE;
	}
			
	if (enemy_range == RANGE_MELEE)
		chance = 0.9;
	else if (enemy_range == RANGE_NEAR)
		chance = 0.6;
	else if (enemy_range == RANGE_MID)
		chance = 0.2;
	else
		chance = 0;


	if (enemy_range == RANGE_MID)
	{
		if (self.attack_state != AS_STRAIGHT)
		{
			self.attack_state = AS_STRAIGHT;
			met_run1 ();
		}
	}
	else
	{
		if (self.attack_state != AS_SLIDING)
		{
			self.attack_state = AS_SLIDING;
			met_side1 ();
		}
	}
	
	return FALSE;
};

/*
=================
WizardAttackFinished
=================
*/
float()	WizardAttackFinished =
{
	if (enemy_range >= RANGE_MID || !enemy_vis)
	{
		self.attack_state = AS_STRAIGHT;
		self.think = met_run1;
	}
	else
	{
		self.attack_state = AS_SLIDING;
		self.think = met_side1;
	}
};

/*
==============================================================================

FAST ATTACKS

==============================================================================
*/

void() Wiz_FastFire =
{
	local vector		vec;
	local vector		dst;

	if (self.owner.health > 0)
	{
		self.owner.effects = self.owner.effects | EF_MUZZLEFLASH;

		makevectors (self.enemy.angles);	
		dst = self.enemy.origin - 13*self.movedir;
	
		vec = normalize(dst - self.origin);
		sound (self, CHAN_WEAPON, "wizard/wattack.wav", 1, ATTN_NORM);
		launch_spike (self.origin, vec);
		newmis.velocity = vec*600;
		newmis.owner = self.owner;
		newmis.classname = "wizspike";
		setmodel (newmis, "progs/w_spike.mdl");
		setsize (newmis, VEC_ORIGIN, VEC_ORIGIN);		
	}

	remove (self);
};


void() metroid_idlesound =
{
local float wr;
	wr = random() * 5;

	if (self.waitmin < time)
	{
	 	self.waitmin = time + 2;
	 	if (wr > 4.5) 
	 		sound (self, CHAN_VOICE, "wizard/widle1.wav", 1,  ATTN_IDLE);
	 	if (wr < 1.5)
	 		sound (self, CHAN_VOICE, "wizard/widle2.wav", 1, ATTN_IDLE);
	}
	return;
};

void()	met_stand1	=[	$hover1,		met_stand2	] {ai_stand();};
void()	met_stand2	=[	$hover2,		met_stand3	] {ai_stand();};
void()	met_stand3	=[	$hover3,		met_stand4	] {ai_stand();};
void()	met_stand4	=[	$hover4,		met_stand5	] {ai_stand();};
void()	met_stand5	=[	$hover5,		met_stand6	] {ai_stand();};
void()	met_stand6	=[	$hover6,		met_stand7	] {ai_stand();};
void()	met_stand7	=[	$hover7,		met_stand8	] {ai_stand();};
void()	met_stand8	=[	$hover8,		met_stand1	] {ai_stand();};

void()	met_walk1	=[	$hover1,		met_walk2	] {ai_walk(8);
metroid_idlesound();};
void()	met_walk2	=[	$hover2,		met_walk3	] {ai_walk(8);};
void()	met_walk3	=[	$hover3,		met_walk4	] {ai_walk(8);};
void()	met_walk4	=[	$hover4,		met_walk5	] {ai_walk(8);};
void()	met_walk5	=[	$hover5,		met_walk6	] {ai_walk(8);};
void()	met_walk6	=[	$hover6,		met_walk7	] {ai_walk(8);};
void()	met_walk7	=[	$hover7,		met_walk8	] {ai_walk(8);};
void()	met_walk8	=[	$hover8,		met_walk1	] {ai_walk(8);};

void()	met_side1	=[	$hover1,		met_side2	] {ai_run(8);
metroid_idlesound();};
void()	met_side2	=[	$hover2,		met_side3	] {ai_run(8);};
void()	met_side3	=[	$hover3,		met_side4	] {ai_run(8);};
void()	met_side4	=[	$hover4,		met_side5	] {ai_run(8);};
void()	met_side5	=[	$hover5,		met_side6	] {ai_run(8);};
void()	met_side6	=[	$hover6,		met_side7	] {ai_run(8);};
void()	met_side7	=[	$hover7,		met_side8	] {ai_run(8);};
void()	met_side8	=[	$hover8,		met_side1	] {ai_run(8);};

void()	met_run1	=[	$fly1,		met_run2	] {ai_run(16);
metroid_idlesound();
};
void()	met_run2	=[	$fly2,		met_run3	] {ai_run(16);};
void()	met_run3	=[	$fly3,		met_run4	] {ai_run(16);};
void()	met_run4	=[	$fly4,		met_run5	] {ai_run(16);};
void()	met_run5	=[	$fly5,		met_run6	] {ai_run(16);};
void()	met_run6	=[	$fly6,		met_run7	] {ai_run(16);};
void()	met_run7	=[	$fly7,		met_run8	] {ai_run(16);};
void()	met_run8	=[	$fly8,		met_run9	] {ai_run(16);};
void()	met_run9	=[	$fly9,		met_run10	] {ai_run(16);};
void()	met_run10	=[	$fly10,		met_run11	] {ai_run(16);};
void()	met_run11	=[	$fly11,		met_run12	] {ai_run(16);};
void()	met_run12	=[	$fly12,		met_run13	] {ai_run(16);};
void()	met_run13	=[	$fly13,		met_run14	] {ai_run(16);};
void()	met_run14	=[	$fly14,		met_run1	] {ai_run(16);};

void()	met_fast1	=[	$magatt1,		met_fast2	] {ai_face();Wiz_StartFast();};
void()	met_fast2	=[	$magatt2,		met_fast3	] {ai_face();};
void()	met_fast3	=[	$magatt3,		met_fast4	] {ai_face();};
void()	met_fast4	=[	$magatt4,		met_fast5	] {ai_face();};
void()	met_fast5	=[	$magatt5,		met_fast6	] {ai_face();};
void()	met_fast6	=[	$magatt6,		met_fast7	] {ai_face();};
void()	met_fast7	=[	$magatt5,		met_fast8	] {ai_face();};
void()	met_fast8	=[	$magatt4,		met_fast9	] {ai_face();};
void()	met_fast9	=[	$magatt3,		met_fast10	] {ai_face();};
void()	met_fast10	=[	$magatt2,		met_run1	] {ai_face();SUB_AttackFinished(2);WizardAttackFinished ();};

void()	met_pain1	=[	$pain1,		met_pain2	] {};
void()	met_pain2	=[	$pain2,		met_pain3	] {};
void()	met_pain3	=[	$pain3,		met_pain4	] {};
void()	met_pain4	=[	$pain4,		met_run1	] {};

void()	met_death1	=[	$death1,		met_death2	] {

self.velocity_x = -200 + 400*random();
self.velocity_y = -200 + 400*random();
self.velocity_z = 100 + 100*random();
self.flags = self.flags - (self.flags & FL_ONGROUND);
sound (self, CHAN_VOICE, "wizard/wdeath.wav", 1, ATTN_NORM);
};
void()	met_death2	=[	$death2,		met_death3	] {};
void()	met_death3	=[	$death3,		met_death4	]{self.solid = SOLID_NOT;};
void()	met_death4	=[	$death4,		met_death5	] {};
void()	met_death5	=[	$death5,		met_death6	] {};
void()	met_death6	=[	$death6,		met_death7	] {};
void()	met_death7	=[	$death7,		met_death8	] {};
void()	met_death8	=[	$death8,		met_death8	] {};

void() metroid_die =
{
// check for gib
	if (self.health < -40)
	{
		sound (self, CHAN_VOICE, "player/udeath.wav", 1, ATTN_NORM);
		ThrowHead ("progs/h_wizard.mdl", self.health);
		ThrowGib ("progs/gib2.mdl", self.health);
		ThrowGib ("progs/gib2.mdl", self.health);
		ThrowGib ("progs/gib2.mdl", self.health);
		return;
	}

	met_death1 ();
};


void(entity attacker, float damage) metroid_Pain =
{
	sound (self, CHAN_VOICE, "wizard/wpain.wav", 1, ATTN_NORM);
	if (random()*70 > damage)
		return;		// didn't flinch

	met_pain1 ();
};
void()	met_atk1	=[	$attackb1,		knight_atk2	]
{
sound (self, CHAN_WEAPON, "knight/sword1.wav", 1, ATTN_NORM);
ai_charge(0);};
void()	met_atk2	=[	$idel1,		met_atk3	] {ai_charge(7);};
void()	met_atk3	=[	$idel2,		met_atk4	] {ai_charge(4);};
void()	met_atk4	=[	$idel3,		met_atk5	] {ai_charge(0);};
void()	met_atk5	=[	$idel4,		met_atk6	] {ai_charge(3);};
void()	met_atk6	=[	$idel5,		met_atk7	] {ai_charge(4); ai_melee();};
void()	met_atk7	=[	$idel6,		met_atk8	] {ai_charge(1); ai_melee();};
void()	met_atk8	=[	$idel7,		met_atk9	] {ai_charge(3);
ai_melee();};
void()	met_atk9	=[	$idel8,		met_atk10] {ai_charge(1);};
void()	met_atk10=[	$idel9,		met_run1	] {ai_charge(5);};

//void()	knight_atk9	=[	$attack9,		knight_atk10	] {};
//void()	knight_atk10	=[	$attack10,		knight_atk11	] {};
//void()	knight_atk11	=[	$attack11,		knight_run1	] {};
/*QUAKED monster_wizard (1 0 0) (-16 -16 -24) (16 16 40) Ambush
*/
void() monster_wizard =
{
	if (deathmatch)
	{
		remove(self);
		return;
	}
	precache_model ("progs/metroid.mdl");
	precache_model ("progs/h_wizard.mdl");
	precache_model ("progs/w_spike.mdl");

	precache_sound ("wizard/hit.wav");		// used by c code
	precache_sound ("wizard/wattack.wav");
	precache_sound ("wizard/wdeath.wav");
	precache_sound ("wizard/widle1.wav");
	precache_sound ("wizard/widle2.wav");
	precache_sound ("wizard/wpain.wav");
	precache_sound ("wizard/wsight.wav");

	self.solid = SOLID_SLIDEBOX;
	self.movetype = MOVETYPE_STEP;

	setmodel (self, "progs/metroid.mdl");

	setsize (self, '-16 -16 -24', '16 16 32');
	self.health = 120;

	self.th_stand = met_stand1;
	self.th_walk = met_walk1;
	self.th_run = met_run1;
	self.th_pain = metroid_Pain;
	self.th_melee = met_atk1;
	self.th_die = metroid_die;
		
	flymonster_start ();
};

