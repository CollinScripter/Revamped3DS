void() info_elite_think;

void() kill_count = 
{
if (round_kills == 0)
{
localcmd ("cl_round 1\n");
TOTAL_MONS = 0;
MAX_MONS = 3;		//4 Max Monsters. 0-1-2-3
round = 1;
}

if (round_kills == 4)
{
localcmd ("cl_round 2\n");
TOTAL_MONS = 0;
MAX_MONS = 5;
round = 2;
}

if (round_kills == 10)
{
localcmd ("cl_round 3\n");
TOTAL_MONS = 0;
MAX_MONS = 9;
round = 3;
}

if (round_kills == 20)
{
localcmd ("skill 2\n");
localcmd ("cl_round 4\n");
TOTAL_MONS = 0;
MAX_MONS = 9;
round = 4;

}

if (round_kills == 30)
{
F_LIVES += 1;			//Increase the players life for making it this far.
localcmd ("cl_round 5\n");
TOTAL_MONS = 0;
MAX_MONS = 14;
round = 5;
}

if (round_kills == 45)
{
localcmd ("cl_round 6\n");
TOTAL_MONS = 0;
MAX_MONS = 19;
round = 6;
}

if (round_kills == 65)
{
localcmd ("skill 3\n");
localcmd ("cl_round 7\n");
TOTAL_MONS = 0;
MAX_MONS = 34;
round = 7;
}

if (round_kills == 100)
{
TOTAL_MONS = 0;
MAX_MONS = 34;
localcmd ("cl_round 8\n");
round = 8;
}
if (round_kills == 150)
{
TOTAL_MONS = 0;
MAX_MONS = 49;
localcmd ("cl_round 8\n");
round = 9;
centerprint (self, "Congrats! You have completed Firefight! Shoot to Retry.\n");
if (self.button0)
localcmd ("map spawn\n");
}

};

/*
===========================================================

WEAPON SHOOTING
This Enables Various Weapons to be used by Monster AI
============================================================
*/
//Shoot the Plasma Pistol
void() Enemy_Fire_PPist =
{
    local vector dir;
    local entity en;

    ai_face();

    //sound (self, CHAN_WEAPON, "soldier/.wav", 1,ATTN_NORM);
    en = self.enemy;
    dir = en.origin - en.velocity*0.2;
    dir = normalize (dir - self.origin);

   W_FirePPistol( self.weaponheat );
};

//Shoot the Needler
void() Enemy_Fire_Needler =
{
    local vector dir;
    local entity en;

    ai_face();

    //sound (self, CHAN_WEAPON, "soldier/.wav", 1,ATTN_NORM);
    en = self.enemy;
    dir = en.origin - en.velocity*0.2;
    dir = normalize (dir - self.origin);

   W_FireNeedler();
};
/*
==============================================================================

ELITE

==============================================================================
*/

$cd id1/models/elite_c
$origin 0 0 24
$base base		
$skin base

$frame	stand1 stand2 stand3 stand4 stand5 stand6 stand7 stand8 stand9

$frame walk1 walk2 walk3 walk4 walk5 walk6 walk7
$frame walk8 walk9 walk10 walk11 walk12 walk13 walk14 walk15 walk16

$frame run1 run2 run3 run4 run5 run6 run7 run8

$frame swing1 swing2 swing3 swing4 swing5 swing6 swing7
$frame swing8 swing9 swing10 swing11 swing12 swing13 swing14

$frame smash1 smash2 smash3 smash4 smash5 smash6 smash7
$frame smash8 smash9 smash10 smash11 smash12 smash13 smash14

$frame melee1 melee2 melee3 melee4 melee5 melee6 melee7 
$frame shoot1 shoot2 shoot3 shoot4 shoot5 shoot6 shoot7 shoot8 shoot9

$frame pain1 pain2 pain3 pain4 pain5

$frame painb1 painb2 painb3

$frame painc1 painc2 painc3 painc4 painc5 painc6

$frame paind1 paind2 paind3 paind4 paind5 paind6 paind7 paind8 paind9 paind10
$frame paind11 paind12 paind13 paind14 paind15 paind16

$frame paine1 paine2 paine3 paine4 paine5 paine6 paine7 paine8 paine9 paine10
$frame paine11 paine12 paine13 paine14 paine15

$frame death1 death2 death3 death4 death5 death6
$frame death7 death8 death9 death10 death11 death12
$frame death13 death14

$frame bdeath1 bdeath2 bdeath3 bdeath4 bdeath5 bdeath6
$frame bdeath7 bdeath8 bdeath9 bdeath10

$frame pull1 pull2 pull3 pull4 pull5 pull6 pull7 pull8 pull9 pull10 pull11

//=============================================================================

//=============================================================================

void() laugh =
{
local float r;
r = random();
if (r <= 0.025)
sound (self, CHAN_AUTO, "elite/laugh1.wav", 1, ATTN_NORM);
else if ( r <= 0.05)
sound (self, CHAN_AUTO, "elite/laugh2.wav", 1, ATTN_NORM);
else
{}
};
/*
================
Elite Melee

FIXME
================
*/
void(float side) chainsaw =
{
local vector	delta;
local float 	ldmg;

	if (!self.enemy)
		return;
	if (!CanDamage (self.enemy, self))
		return;

	ai_charge(10);

	delta = self.enemy.origin - self.origin;

	if (vlen(delta) > 100)
		return;
		
	if (self.elite == 0)
	ldmg = (random() + random() + random()) * 10;
	else if (self.elite == 1)
	ldmg = (random() + random() + random()) * 15;
	else if (self.elite == 2)
	ldmg = (random() + random() + random()) * 20;
	T_Damage (self.enemy, self, self, ldmg, MOD_OGRE);
};


void() elite_stand1	=[	$stand1,	elite_stand2	] {ai_stand();};
void() elite_stand2	=[	$stand2,	elite_stand3	] {ai_stand();};
void() elite_stand3	=[	$stand3,	elite_stand4	] {ai_stand(); laugh();};
void() elite_stand4	=[	$stand4,	elite_stand5	] {ai_stand();};
void() elite_stand5	=[	$stand5,	elite_stand6	] {
ai_stand();
};
void() elite_stand6	=[	$stand6,	elite_stand7	] {ai_stand();};
void() elite_stand7	=[	$stand7,	elite_stand8	] {ai_stand();};
void() elite_stand8	=[	$stand8,	elite_stand9	] {ai_stand();};
void() elite_stand9	=[	$stand9,	elite_stand1	] {ai_stand();};

void() elite_walk1	=[	$walk1,		elite_walk2	] {ai_walk(3);};
void() elite_walk2	=[	$walk2,		elite_walk3	] {ai_walk(2);};
void() elite_walk3	=[	$walk3,		elite_walk4	] {
ai_walk(2);
};
void() elite_walk4	=[	$walk4,		elite_walk5	] {ai_walk(2);};
void() elite_walk5	=[	$walk5,		elite_walk6	] {ai_walk(2);};
void() elite_walk6	=[	$walk6,		elite_walk7	] {
ai_walk(5);
if (random() < 0.1)
	sound (self, CHAN_VOICE, "elite/ogdrag.wav", 1, ATTN_IDLE);
};
void() elite_walk7	=[	$walk7,		elite_walk8	] {ai_walk(6);};
void() elite_walk8	=[	$walk8,		elite_walk9	] {ai_walk(4);};
void() elite_walk9	=[	$walk9,		elite_walk10	] {ai_walk(6);};
void() elite_walk10	=[	$walk10,	elite_walk11	] {ai_walk(2);};
void() elite_walk11	=[	$walk11,	elite_walk12	] {ai_walk(4);};
void() elite_walk12	=[	$walk12,	elite_walk13	] {ai_walk(6);};
void() elite_walk13	=[	$walk13,	elite_walk14	] {ai_walk(6);};
void() elite_walk14	=[	$walk14,	elite_walk15	] {ai_walk(6);};
void() elite_walk15	=[	$walk15,	elite_walk16	] {ai_walk(6);};
void() elite_walk16	=[	$walk16,	elite_walk1	] {ai_walk(8);};

void() elite_run1	=[	$run1,		elite_run2	] {ai_run(18);
};
void() elite_run2	=[	$run2,		elite_run3	] {ai_run(15);};
void() elite_run3	=[	$run3,		elite_run4	] {ai_run(15);};
void() elite_run4	=[	$run4,		elite_run5	] {ai_run(15);};
void() elite_run5	=[	$run5,		elite_run6	] {ai_run(15);};
void() elite_run6	=[	$run6,		elite_run7	] {ai_run(15);};
void() elite_run7	=[	$run7,		elite_run8	] {ai_run(15);};
void() elite_run8	=[	$run8,		elite_run1	] {ai_run(15);};

void() elite_swing1	=[	$swing1,		elite_swing2	] {ai_charge(11);
sound (self, CHAN_WEAPON, "elite/ogsawatk.wav", 1, ATTN_NORM);
};
void() elite_swing2	=[	$swing2,		elite_swing3	] {ai_charge(1);};
void() elite_swing3	=[	$swing3,		elite_swing4	] {ai_charge(4);};
void() elite_swing4	=[	$swing4,		elite_swing5	] {ai_charge(13);};
void() elite_swing5	=[	$swing5,		elite_swing6	] {ai_charge(9); };
void() elite_swing6	=[	$swing6,		elite_swing7	] {};
void() elite_swing7	=[	$swing7,		elite_swing8	] {};
void() elite_swing8	=[	$swing8,		elite_swing9	] {};
void() elite_swing9	=[	$swing9,		elite_swing10 ] {chainsaw(0);self.angles_y = self.angles_y + random()* 10;};
void() elite_swing10	=[	$swing10,		elite_swing11 ] {chainsaw(0);self.angles_y = self.angles_y + random()* 10;};
void() elite_swing11	=[	$swing11,		elite_swing12 ] {};
void() elite_swing12	=[	$swing12,		elite_swing13 ] {ai_charge(3);};
void() elite_swing13	=[	$swing13,		elite_swing14 ] {ai_charge(8);};
void() elite_swing14	=[	$swing14,		elite_run1	] {ai_charge(9);};

void() elite_smash1	=[	$smash1,		elite_smash2	] {ai_charge(6);
sound (self, CHAN_WEAPON, "elite/ogsawatk.wav", 1, ATTN_NORM);
};
void() elite_smash2	=[	$smash2,		elite_smash3	] {ai_charge(0);};
void() elite_smash3	=[	$smash3,		elite_smash4	] {ai_charge(0);};
void() elite_smash4	=[	$smash4,		elite_smash5	] {ai_charge(1);};
void() elite_smash5	=[	$smash5,		elite_smash6	] {ai_charge(4);};
void() elite_smash6	=[	$smash6,		elite_smash7	] {ai_charge(4); chainsaw(0);};
void() elite_smash7	=[	$smash7,		elite_smash8	] {ai_charge(4);};
void() elite_smash8	=[	$smash8,		elite_smash9	] {ai_charge(10);};
void() elite_smash9	=[	$smash9,		elite_smash10 ] {ai_charge(13);};
void() elite_smash10	=[	$smash10,		elite_smash11 ] {chainsaw(1);};
void() elite_smash11	=[	$smash11,		elite_smash12 ] {ai_charge(2);
self.nextthink = time + 0.1 + random()*0.1;};	// slight variation
//void() elite_smash12	=[	$smash12,		elite_smash13 ] {ai_charge();};
void() elite_smash12 =[$smash12, elite_smash13] {ai_charge(0);};
void() elite_smash13	=[	$smash13,		elite_smash14 ] {ai_charge(4);};
void() elite_smash14	=[	$smash14,		elite_run1	] {ai_charge(12);};

void() elite_nail1	=[	$run1,		elite_nail2	] {ai_face();};
void() elite_nail2	=[	$run2,		elite_nail3	] {ai_face();};
void() elite_nail3	=[	$run2,		elite_nail4	] {ai_face();};
void() elite_nail4	=[	$run3,		elite_nail5	] {ai_face();
if (self.elite == 0 || self.elite == 2)
Enemy_Fire_PPist();
if (self.elite == 1)
Enemy_Fire_Needler();
};
void() elite_nail5	=[	$run4,		elite_nail6	] {ai_face();};
void() elite_nail6	=[	$run5,		elite_nail7	] {ai_face();};
void() elite_nail7	=[	$run6,		elite_run1	] {ai_face();};

void()	elite_pain1	=[	$pain1,		elite_pain2	] {};
void()	elite_pain2	=[	$pain2,		elite_pain3	] {};
void()	elite_pain3	=[	$pain3,		elite_pain4	] {};
void()	elite_pain4	=[	$pain4,		elite_pain5	] {};
void()	elite_pain5	=[	$pain5,		elite_run1	] {};


void()	elite_painb1	=[	$painb1,	elite_painb2	] {};
void()	elite_painb2	=[	$painb2,	elite_painb3	] {};
void()	elite_painb3	=[	$painb3,	elite_run1	] {};


void()	elite_painc1	=[	$painc1,	elite_painc2	] {};
void()	elite_painc2	=[	$painc2,	elite_painc3	] {};
void()	elite_painc3	=[	$painc3,	elite_painc4	] {};
void()	elite_painc4	=[	$painc4,	elite_painc5	] {};
void()	elite_painc5	=[	$painc5,	elite_painc6	] {};
void()	elite_painc6	=[	$painc6,	elite_run1	] {};


void()	elite_paind1	=[	$paind1,	elite_paind2	] {};
void()	elite_paind2	=[	$paind2,	elite_paind3	] {ai_pain(10);};
void()	elite_paind3	=[	$paind3,	elite_paind4	] {ai_pain(9);};
void()	elite_paind4	=[	$paind4,	elite_paind5	] {ai_pain(4);};
void()	elite_paind5	=[	$paind5,	elite_paind6	] {};
void()	elite_paind6	=[	$paind6,	elite_paind7	] {};
void()	elite_paind7	=[	$paind7,	elite_paind8	] {};
void()	elite_paind8	=[	$paind8,	elite_paind9	] {};
void()	elite_paind9	=[	$paind9,	elite_paind10	] {};
void()	elite_paind10=[	$paind10,	elite_paind11	] {};
void()	elite_paind11=[	$paind11,	elite_paind12	] {};
void()	elite_paind12=[	$paind12,	elite_paind13	] {};
void()	elite_paind13=[	$paind13,	elite_paind14	] {};
void()	elite_paind14=[	$paind14,	elite_paind15	] {};
void()	elite_paind15=[	$paind15,	elite_paind16	] {};
void()	elite_paind16=[	$paind16,	elite_run1	] {};

void()	elite_paine1	=[	$paine1,	elite_paine2	] {};
void()	elite_paine2	=[	$paine2,	elite_paine3	] {ai_pain(10);};
void()	elite_paine3	=[	$paine3,	elite_paine4	] {ai_pain(9);};
void()	elite_paine4	=[	$paine4,	elite_paine5	] {ai_pain(4);};
void()	elite_paine5	=[	$paine5,	elite_paine6	] {};
void()	elite_paine6	=[	$paine6,	elite_paine7	] {};
void()	elite_paine7	=[	$paine7,	elite_paine8	] {};
void()	elite_paine8	=[	$paine8,	elite_paine9	] {};
void()	elite_paine9	=[	$paine9,	elite_paine10	] {};
void()	elite_paine10=[	$paine10,	elite_paine11	] {};
void()	elite_paine11=[	$paine11,	elite_paine12	] {};
void()	elite_paine12=[	$paine12,	elite_paine13	] {};
void()	elite_paine13=[	$paine13,	elite_paine14	] {};
void()	elite_paine14=[	$paine14,	elite_paine15	] {};
void()	elite_paine15=[	$paine15,	elite_run1	] {};


void(entity attacker, float damage)	elite_pain =
{
	local float	r;

// don't make multiple pain sounds right after each other
	if (self.pain_finished > time)
		return;

	sound (self, CHAN_VOICE, "elite/ogpain1.wav", 1, ATTN_NORM);		

	r = random();
	
	if (r < 0.25)
	{
		elite_pain1 ();
		self.pain_finished = time + 1;
	}
	else if (r < 0.5)
	{
		elite_painb1 ();
		self.pain_finished = time + 1;
	}
	else if (r < 0.75)
	{
		elite_painc1 ();
		self.pain_finished = time + 1;
	}
	else if (r < 0.88)
	{
		elite_paind1 ();
		self.pain_finished = time + 2;
	}
	else
	{
		elite_paine1 ();
		self.pain_finished = time + 2;
	}
};

void()	elite_die1	=[	$death1,	elite_die2	] {};
void()	elite_die2	=[	$death2,	elite_die3	] {};
void()	elite_die3	=[	$death3,	elite_die4	]
{self.solid = SOLID_NOT;DropBackpack();};
void()	elite_die4	=[	$death4,	elite_die5	] {};
void()	elite_die5	=[	$death5,	elite_die6	] {};
void()	elite_die6	=[	$death6,	elite_die7	] {};
void()	elite_die7	=[	$death7,	elite_die8	] {};
void()	elite_die8	=[	$death8,	elite_die9	] {};
void()	elite_die9	=[	$death9,	elite_die10	] {};
void()	elite_die10	=[	$death10,	elite_die11	] {};
void()	elite_die11	=[	$death11,	elite_die12	] {};
void()	elite_die12	=[	$death12,	elite_die13	] {};
void()	elite_die13	=[	$death13,	elite_die14	] {};
void()	elite_die14	=[	$death14,	elite_die14	] {remove(self); round_kills += 1; kill_count();};

void()	elite_bdie1	=[	$bdeath1,	elite_bdie2	] {};
void()	elite_bdie2	=[	$bdeath2,	elite_bdie3	] {ai_forward(5);};
void()	elite_bdie3	=[	$bdeath3,	elite_bdie4	]
{self.solid = SOLID_NOT;DropBackpack();};
void()	elite_bdie4	=[	$bdeath4,	elite_bdie5	] {ai_forward(1);};
void()	elite_bdie5	=[	$bdeath5,	elite_bdie6	] {ai_forward(3);};
void()	elite_bdie6	=[	$bdeath6,	elite_bdie7	] {ai_forward(7);};
void()	elite_bdie7	=[	$bdeath7,	elite_bdie8	] {ai_forward(25);};
void()	elite_bdie8	=[	$bdeath8,	elite_bdie9	] {};
void()	elite_bdie9	=[	$bdeath9,	elite_bdie10	] {};
void()	elite_bdie10	=[	$bdeath10,	elite_bdie10	] {remove(self); round_kills += 1; kill_count();};

void() elite_die =
{

	sound (self, CHAN_VOICE, "elite/ogdth.wav", 1, ATTN_NORM);
	
	if (random() < 0.5)
		elite_die1 ();
	else
		elite_bdie1 ();
};

void() elite_melee =
{
	if (random() > 0.5)
		elite_smash1 ();
	else
		elite_swing1 ();
};


/*
==============================================================================

SOLDIER / PLAYER

==============================================================================
*/

$cd id1/models/soldier3
$origin 0 -6 24
$base base		
$skin skin

$frame prowl_1 prowl_2 prowl_3 prowl_4 prowl_5 prowl_6 prowl_7 prowl_8
$frame prowl_9 prowl_10 prowl_11 prowl_12 prowl_13 prowl_14 prowl_15 prowl_16
$frame prowl_17 prowl_18 prowl_19 prowl_20 prowl_21 prowl_22 prowl_23 prowl_24

/*
==============================================================================
SOLDIER CODE
==============================================================================
*/

void() laughs =
{
local float r;
r = random();
if (r <= 0.025)
{
self.attack_finished = time + 0.6;
sound (self, CHAN_AUTO, "soldier/laugh1.wav", 0.8, ATTN_NORM);
}
else if ( r <= 0.05)
{
self.attack_finished = time + 0.6;
sound (self, CHAN_AUTO, "soldier/laugh2.wav", 0.8, ATTN_NORM);
}
else
{}
};
//For randomy playing a grunt sound
void() g_attack =
{
local float r;
r = random();
if (r <= 0.005)
{
self.attack_finished = time + 0.6;
sound (self, CHAN_AUTO, "soldier/unstoppable.wav", 0.9, ATTN_NORM);
}
else if ( r <= 0.01)
{
self.attack_finished = time + 0.6;
sound (self, CHAN_AUTO, "soldier/kill_it.wav", 0.9, ATTN_NORM);
}
else {}
};
void() army_fire;

void()	army_stand1	=[	$stand1,	army_stand2	] {ai_stand();};
void()	army_stand2	=[	$stand2,	army_stand3	] {ai_stand();};
void()	army_stand3	=[	$stand3,	army_stand4	] {ai_stand();};
void()	army_stand4	=[	$stand4,	army_stand5	] {ai_stand();};
void()	army_stand5	=[	$stand5,	army_stand6	] {ai_stand();};
void()	army_stand6	=[	$stand6,	army_stand7	] {ai_stand();laughs();};
void()	army_stand7	=[	$stand7,	army_stand8	] {ai_stand();};
void()	army_stand8	=[	$stand8,	army_stand1	] {ai_stand();};

void()	army_walk1	=[	$prowl_1,	army_walk2	] {
ai_walk(1);};
void()	army_walk2	=[	$prowl_2,	army_walk3	] {ai_walk(1);};
void()	army_walk3	=[	$prowl_3,	army_walk4	] {ai_walk(1);};
void()	army_walk4	=[	$prowl_4,	army_walk5	] {ai_walk(1);};
void()	army_walk5	=[	$prowl_5,	army_walk6	] {ai_walk(2);};
void()	army_walk6	=[	$prowl_6,	army_walk7	] {ai_walk(3);};
void()	army_walk7	=[	$prowl_7,	army_walk8	] {ai_walk(4);};
void()	army_walk8	=[	$prowl_8,	army_walk9	] {ai_walk(4);};
void()	army_walk9	=[	$prowl_9,	army_walk10	] {ai_walk(2);};
void()	army_walk10	=[	$prowl_10,	army_walk11	] {ai_walk(2);};
void()	army_walk11	=[	$prowl_11,	army_walk12	] {ai_walk(2);};
void()	army_walk12	=[	$prowl_12,	army_walk13	] {ai_walk(1);};
void()	army_walk13	=[	$prowl_13,	army_walk14	] {ai_walk(0);};
void()	army_walk14	=[	$prowl_14,	army_walk15	] {ai_walk(1);};
void()	army_walk15	=[	$prowl_15,	army_walk16	] {ai_walk(1);};
void()	army_walk16	=[	$prowl_16,	army_walk17	] {ai_walk(1);};
void()	army_walk17	=[	$prowl_17,	army_walk18	] {ai_walk(3);};
void()	army_walk18	=[	$prowl_18,	army_walk19	] {ai_walk(3);};
void()	army_walk19	=[	$prowl_19,	army_walk20	] {ai_walk(3);};
void()	army_walk20	=[	$prowl_20,	army_walk21	] {ai_walk(3);};
void()	army_walk21	=[	$prowl_21,	army_walk22	] {ai_walk(2);};
void()	army_walk22	=[	$prowl_22,	army_walk23	] {ai_walk(1);};
void()	army_walk23	=[	$prowl_23,	army_walk24	] {ai_walk(1);};
void()	army_walk24	=[	$prowl_24,	army_walk1	] {ai_walk(1);};

void()	army_run1	=[	$run1,		army_run2	] {
if (random() < 0.2)
	sound (self, CHAN_VOICE, "soldier/idle.wav", 1, ATTN_IDLE);
ai_run(11);};
void()	army_run2	=[	$run2,		army_run3	] {ai_run(15);};
void()	army_run3	=[	$run3,		army_run4	] {ai_run(10);};
void()	army_run4	=[	$run4,		army_run5	] {ai_run(10);};
void()	army_run5	=[	$run5,		army_run6	] {ai_run(8);};
void()	army_run6	=[	$run6,		army_run7	] {ai_run(15);};
void()	army_run7	=[	$run7,		army_run8	] {ai_run(10);};
void()	army_run8	=[	$run8,		army_run1	] {ai_run(8);};

void()	army_atk1	=[	$shoot1,	army_atk2	] {ai_face();};
void()	army_atk2	=[	$shoot2,	army_atk3	] {ai_face();};
void()	army_atk3	=[	$shoot3,	army_atk4	] {ai_face();};
void()	army_atk4	=[	$shoot4,	army_atk5	] {ai_face();};
void()	army_atk5	=[	$shoot5,	army_atk6	] {ai_face(); Enemy_Fire_PPist();};
void()	army_atk6	=[	$shoot6,	army_atk7	] {ai_face();};
void()	army_atk7	=[	$shoot7,	army_atk8	] {ai_face();SUB_CheckRefire (army_atk1);};
void()	army_atk8	=[	$shoot8,	army_atk9	] {ai_face();};
void()	army_atk9	=[	$shoot9,	army_run1	] {ai_face();};

void() grunt_melee1	=[	$melee1,		grunt_melee2	] {ai_charge(1); };
void() grunt_melee2	=[	$melee2,		grunt_melee3	] {ai_charge(1);};
void() grunt_melee3	=[	$melee3,		grunt_melee4	] {ai_charge(4); chainsaw(0);self.angles_y = self.angles_y + random()* 10;};
void() grunt_melee4	=[	$melee4,		grunt_melee5	] {ai_charge(13);};
void() grunt_melee5	=[	$melee5,		grunt_melee6	] {ai_charge(9); };
void() grunt_melee6	=[	$melee6,		grunt_melee7	] {};
void() grunt_melee7	=[	$melee7,		army_run1	] {};

void()	army_pain1	=[	$pain1,		army_pain2	] {};
void()	army_pain2	=[	$pain2,		army_pain3	] {};
void()	army_pain3	=[	$pain3,		army_pain4	] {};
void()	army_pain4	=[	$pain4,		army_pain5	] {g_attack();};
void()	army_pain5	=[	$pain5,		army_pain6	] {};
void()	army_pain6	=[	$pain6,		army_run1	] {ai_pain(1);};

void()	army_painb1	=[	$painb1,	army_painb2	] {};
void()	army_painb2	=[	$painb2,	army_painb3	] {ai_painforward(13);};
void()	army_painb3	=[	$painb3,	army_painb4	] {ai_painforward(9);};
void()	army_painb4	=[	$painb4,	army_painb5	] {};
void()	army_painb5	=[	$painb5,	army_painb6	] {};
void()	army_painb6	=[	$painb6,	army_painb7	] {};
void()	army_painb7	=[	$painb7,	army_painb8	] {};
void()	army_painb8	=[	$painb8,	army_painb9	] {};
void()	army_painb9	=[	$painb9,	army_painb10] {};
void()	army_painb10=[	$painb10,	army_painb11] {};
void()	army_painb11=[	$painb11,	army_painb12] {};
void()	army_painb12=[	$painb12,	army_painb13] {ai_pain(2);};
void()	army_painb13=[	$painb13,	army_painb14] {};
void()	army_painb14=[	$painb14,	army_run1	] {};

void()	army_painc1	=[	$painc1,	army_painc2	] {};
void()	army_painc2	=[	$painc2,	army_painc3	] {ai_pain(1);};
void()	army_painc3	=[	$painc3,	army_painc4	] {};
void()	army_painc4	=[	$painc4,	army_painc5	] {};
void()	army_painc5	=[	$painc5,	army_painc6	] {ai_painforward(1);};
void()	army_painc6	=[	$painc6,	army_painc7	] {ai_painforward(1);};
void()	army_painc7	=[	$painc7,	army_painc8	] {};
void()	army_painc8	=[	$painc8,	army_painc9	] {ai_pain(1);};
void()	army_painc9	=[	$painc9,	army_painc10] {ai_painforward(4);};
void()	army_painc10=[	$painc10,	army_painc11] {ai_painforward(3);};
void()	army_painc11=[	$painc11,	army_painc12] {ai_painforward(6);};
void()	army_painc12=[	$painc12,	army_painc13] {ai_painforward(8);};
void()	army_painc13=[	$painc13,	army_run1] {};

void(entity attacker, float damage)	army_pain =
{
	local float r;
	
	if (self.pain_finished > time)
		return;

	r = random();

	if (r < 0.2)
	{
		self.pain_finished = time + 0.6;
		army_pain1 ();
		sound (self, CHAN_VOICE, "soldier/pain1.wav", 1, ATTN_NORM);
	}
	else if (r < 0.6)
	{
		self.pain_finished = time + 1.1;
		army_painb1 ();
		sound (self, CHAN_VOICE, "soldier/pain2.wav", 1, ATTN_NORM);
	}
	else
	{
		self.pain_finished = time + 1.1;
		army_painc1 ();
		sound (self, CHAN_VOICE, "soldier/pain2.wav", 1, ATTN_NORM);
	}
};


void() army_fire =
{
	local	vector	dir;
	local	entity	en;
	
	ai_face();
	
	sound (self, CHAN_WEAPON, "weapons/ppist.wav", 1, ATTN_NORM);	

// fire somewhat behind the player, so a dodging player is harder to hit
	en = self.enemy;
	
	dir = en.origin - en.velocity*0.2;
	dir = normalize (dir - self.origin);
	
	FireBullets (1, dir, '0.1 0.1 0', MOD_SOLDIER);
};



void()	army_die1	=[	$death1,	army_die2	] {remove(self); round_kills += 1; kill_count();};
void()	army_die2	=[	$death2,	army_die3	] {};
void()	army_die3	=[	$death3,	army_die4	] {self.solid = SOLID_NOT;DropBackpack();};
void()	army_die4	=[	$death4,	army_die5	] {};
void()	army_die5	=[	$death5,	army_die6	] {};
void()	army_die6	=[	$death6,	army_die7	] {};
void()	army_die7	=[	$death7,	army_die8	] {};
void()	army_die8	=[	$death8,	army_die9	] {};
void()	army_die9	=[	$death9,	army_die10	] {};
void()	army_die10	=[	$death10,	army_die10	] {};


void() army_die =
{

// regular death
	sound (self, CHAN_VOICE, "soldier/death1.wav", 1, ATTN_NORM);
		army_die1 ();
};
