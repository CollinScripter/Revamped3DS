/*
==============================================================================

SOLITUDE PLAYER ANIMATIONS

==============================================================================
*/

void() bubble_bob;
$cd /raid/quake/id1/models/player_4
$origin 0 -6 24
$base base              
$skin skin

#define PLAYER_GUN_IDLE		0
#define PLAYER_RUN			1
#define PLAYER_ATTACK1		2
#define PLAYER_DIE1			3
#define PLAYER_AXE_IDLE		4
#define PLAYER_WALK			5
#define PLAYER_SWIM			6
#define PLAYER_JUMP			7
#define PLAYER_ATTACK_STAND	8
#define PLAYER_ATTACK_SIT	9
#define PLAYER_THROW_NADE	10
#define PLAYER_ATTACK_MELEE	11
#define PLAYER_ATTACK_RUN	12
#define PLAYER_DEATH1		13
#define PLAYER_DEATH2		14
#define PLAYER_RELOAD		15
#define PLAYER_PAIN			16			// HACK!! (uses death 1 anims)
#define PLAYER_PULL	17
float (float anim_type, float endframe) Player_GetFrame =
{
	switch (anim_type)
	{
		case PLAYER_GUN_IDLE:
			if (endframe)
				return 8;
			return 0;
			break;
		case PLAYER_AXE_IDLE:
			return 0;
			break;
		case PLAYER_RUN:
			if (endframe)
				return 14;
			return 9;
			break;
		case PLAYER_WALK:
			if (endframe)
				return 19;
			return 15;
			break;
		case PLAYER_SWIM:
			if (endframe)
				return 26;
			return 19;
			break;
		case PLAYER_JUMP:
			if (endframe)
				return 22;
			return 20;
			break;
		case PLAYER_ATTACK_STAND:
			if (endframe)
				return 25;
			return 23;
			break;
		case PLAYER_ATTACK_SIT:
			if (endframe)
				return 28;
			return 26;
			break;
		case PLAYER_THROW_NADE:
			if (endframe)
				return 35;
			return 29;
			break;
		case PLAYER_ATTACK_MELEE:
			if (endframe)
				return 41;
			return 36;
			break;
		case PLAYER_ATTACK_RUN:
			if (endframe)
				return 48;
			return 42;
			break;
		case PLAYER_DEATH1:
			if (endframe)
				return 60;
			return 49;
			break;
		case PLAYER_DEATH2:
			if (endframe)
				return 71;
			return 61;
			break;
		case PLAYER_RELOAD:
			if (endframe)
				return 79;
			return 70;
			break;
		case PLAYER_PAIN:
			if (endframe)
				return 51;
			return 49;
			break;
		case PLAYER_PULL:
			if (endframe)
				return 79;
			return 70;
			break;
		default:
			return 0;
			break;
	}
	
	return 0;
};

void (entity t_plyr, float t_frame) startwframe =
{
	if (t_plyr.weaponframe < t_frame)
		t_plyr.weaponframe = t_frame;
};

/*
==============================================================================
PLAYER
==============================================================================
*/

void() player_run;

void()  player_stand1 =[        0,       player_stand1   ]
{
	player_run ();		// player_run handles most animations.
};

void()  player_run =[   0,      player_run      ]
{
	local float ftype;
	
	if (vlen(self.velocity) < 150)
		ftype = PLAYER_WALK;
	else
		ftype = PLAYER_RUN;
		
//	if (self.waterlevel > 0)
//		ftype = PLAYER_SWIM;

	if (!self.velocity_x && !self.velocity_y)
	{
		ftype = PLAYER_GUN_IDLE;
	}
	
	if (self.jump_time > time)
		ftype = PLAYER_JUMP;

	if (self.pain_time > time)
		ftype = PLAYER_PAIN;
		
	if (self.weaponstate == WS_FIRING1 && self.weaponframe > 0) {
		if (vlen(self.velocity) < 20)
			ftype = PLAYER_ATTACK_STAND;
		else
			ftype = PLAYER_ATTACK_RUN;
	}
		
	self.frame = Player_GetFrame(ftype, 0);
		

	if ((self.frame + self.walkframe) > Player_GetFrame(ftype, 1)) 
		self.walkframe = 0;
		
	self.frame = self.frame + self.walkframe;

	self.walkframe = self.walkframe + 1;
	
	//_bprint(ftos(self.frame)," firing anim\n");
};

void () player_shot1 = [ 113, player_shot2 ]
{
	self.weaponframe = 1;
	self.effects = (self.effects | EF_MUZZLEFLASH);
};

void () player_shot2 = [ 114, player_shot3 ]
{
	self.weaponframe = 2;
};

void () player_shot3 = [ 115, player_shot4 ]
{
	self.weaponframe = 3;
};

void () player_shot4 = [ 116, player_run ]
{
	self.weaponframe = 0;
};

void () player_shot5 = [ 117, player_shot6 ]
{
	self.weaponframe = 5;
};

void () player_shot6 = [ 118, player_run ]
{
	self.weaponframe = 6;
};

void () player_pistol_reload =
{
	local float amt;

	self.weaponframe = (self.weaponframe + WEAPON_SHOTGUN);
	if (self.weaponframe == 29)
	{
		player_run ();
		amt = (12 - self.ammo_shells);
		if ((self.exshells < amt))
		{
			amt = self.exshells;
		}
		self.exshells = (self.exshells - amt);
		self.ammo_shells = (self.ammo_shells + amt);
		self.armorvalue = self.exshells;
		W_SetCurrentAmmo ();
		return;
	}
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};
void () player_skull_reload =
{
	local float amt;

	self.weaponframe = (self.weaponframe + WEAPON_SKULL);
	if (self.weaponframe == 29)
	{
		player_run ();
		amt = (12 - self.ammo_shells);
		if ((self.exshells < amt))
		{
			amt = self.exshells;
		}
		self.exshells = (self.exshells - amt);
		self.ammo_shells = (self.ammo_shells + amt);
		self.armorvalue = self.exshells;
		W_SetCurrentAmmo ();
		return;
	}
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};
/*
void () player_shotgun_drop = [ 143, player_shotgun_drop ]
{
	self.weaponframe = (self.weaponframe + WEAPON_SHOTGUN);
	if ((self.weaponframe == SVC_KILLEDMONSTER))
	{
		self.weaponframe = 0;
		player_run ();
		return;
	}
	self.impulse = MSG_BROADCAST;
};

void () player_shotgun_reload =
{
	self.weaponframe = (self.weaponframe + WEAPON_SHOTGUN);

	if ((self.weaponframe == 17))
	{
		self.exshells2 = (self.exshells2 - 1);
		self.ammo_shells2 = (self.ammo_shells2 + 1);
		self.armorvalue = self.exshells2;
		W_SetCurrentAmmo ();
		if ( ((self.ammo_shells2 < W_GetMaxClip( self.weapon, 1 )) || (self.exshells2 == MSG_BROADCAST)) && self.exshells2 > 0)
		{
			self.weaponframe = 13;
			player_shotgun_reload ();
		}
		else
		{
			self.weaponframe = 17;
			player_shotgun_drop ();
			return;
		}
	}
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};
*/

void () player_shotgun_reload =
{
	if (self.button0 && self.currentammo > 0) {		// Interrupt reload
		player_run ();
		return;
	}
	
	self.weaponframe += 1;
	if (self.weaponframe == 17)
	{
		self.exshells2 = (self.exshells2 - 1);
		self.ammo_shells2 = (self.ammo_shells2 + 1);
		self.armorvalue = self.exshells2;
		W_UpdateAmmoCounts(self);
		if (self.currentammo == W_GetMaxClip( self.weapon, 1 ) || self.armorvalue == 0) {
			self.weaponframe = 18;
		}
		else {

			self.weaponframe = 13;
		}
	}
	else if (self.weaponframe > 17) {
		if (self.weaponframe > 20) {
			player_run ();
			W_SetCurrentAmmo ();
			return;
		}
	}
	
	self.attack_finished = (time + 0.2);
	self.impulse = 0;
};

void () player_uzi_reload =
{
	local float amt;

	self.weaponframe += 1;
	if ((self.weaponframe > 19))
	{
		player_run ();
		amt = (W_GetMaxClip(self.weapon, 1) - self.ammo_hshells);
		if ((self.exhshells < amt))
		{
			amt = self.exhshells;
		}
		self.exhshells = (self.exhshells - amt);
		self.ammo_hshells = (self.ammo_hshells + amt);
		self.armorvalue = self.exhshells;
		W_SetCurrentAmmo ();
		return;
	}
	self.attack_finished = (time + 0.2);
	self.impulse = 0;
};

void () player_rl_reload =
{
	local float amt;

	self.weaponframe += 1;
	if ((self.weaponframe > 50))
	{
		player_run ();
		amt = (W_GetMaxClip(self.weapon, 1) - self.ammo_rockets);
		if ((self.exrockets < amt))
		{
			amt = self.exrockets;
		}
		self.exrockets = (self.exrockets - amt);
		self.ammo_rockets = (self.ammo_rockets + amt);
		self.armorvalue = self.exrockets;
		W_SetCurrentAmmo ();
		return;
	}
	self.attack_finished = (time + 0.2);
	self.impulse = 0;
};

void () player_ar_reload =
{
	local float amt;
	
	self.weaponframe += 1;
	if ((self.weaponframe == 29))
	{
		player_run ();
		amt = (W_GetMaxClip(self.weapon, 1) - self.ammo_nails);
		if ((self.exnails < amt))
		{
			amt = self.exnails;
		}
		self.exnails = (self.exnails - amt);
		self.ammo_nails = (self.ammo_nails + amt);
		self.armorvalue = self.exnails;
		W_SetCurrentAmmo ();
		return;
	}
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};

void () player_sniper_reload =
{
	local float amt;

	self.weaponframe += 1;
	if (self.weaponframe > 27)
	{
		player_run ();
		amt = (W_GetMaxClip(self.weapon, 1) - self.ammo_sniper);
		if ((self.exsniper < amt))
		{
			amt = self.exsniper;
		}
		self.exsniper -= amt;
		self.ammo_sniper += amt;
		self.armorvalue = self.exsniper;
		W_SetCurrentAmmo ();
		return;
	}
	self.attack_finished = (time + 0.2);
	self.impulse = 0;
};

void () player_ppistol_reload =
{
	if (self.weaponframe < 15)		// fixme: shouldn't be necessary :\
		self.weaponframe = 15;
	self.weaponframe += 1;
	if (self.weaponframe > 35)
	{
		player_run ();
		self.exppistol = 0;
		self.weaponheat = 0;
		W_SetCurrentAmmo ();
		return;
	}
	//self.weaponframe_time = time + 0.1;
	self.attack_finished = (time + 0.2);
	self.impulse = 0;
};

void () player_needler_reload =
{
	local float amt;

	self.weaponframe += 1;
	if (self.weaponframe > 29)
	{
		player_run ();
		amt = (W_GetMaxClip(self.weapon, 1) - self.ammo_needler);
		if ((self.exneedler < amt))
		{
			amt = self.exneedler;
		}
		self.exneedler -= amt;
		self.ammo_needler += amt;
		self.armorvalue = self.exneedler;
		W_SetCurrentAmmo ();
		return;
	}
	self.attack_finished = (time + 0.2);
	self.impulse = 0;
};

void () player_generic_reload =
{
	local float rld_amt;
	rld_amt = self.armorvalue;

	if ((Player_GetFrame(PLAYER_RELOAD, 0) + self.fireframe) > Player_GetFrame(PLAYER_RELOAD, 1)) {
	
		rld_amt = (W_GetMaxClip(self.weapon, 1) - self.currentammo);
		if ((self.armorvalue < rld_amt))
		{
			rld_amt = self.armorvalue;
		}
		player_run ();
		SetAmmoFor( self, self.weapon, 1, rld_amt );
		SetAmmoFor( self, self.weapon, 0, (-1 * rld_amt) );
		W_SetCurrentAmmo ();
		return;
	}
	self.attack_finished = (time + 0.2);
	self.impulse = 0;
};

// Primary player reload function (handles all reloading)
void () player_reload1 = [ 0, player_reload1 ]
{
	// allow players to interrupt reload for melee/nade throw
	if (self.impulse == 29) {
		pre_player_melee ();
		return;
	}
	else if (self.impulse == 28) {
		pre_player_throw_grenade ();
		return;
	}
	else if (self.reload_time == -1) {
		self.reload_time = 1;
		player_run();
		return;
	}
	
	switch (self.weapon) {
		case WEAPON_PISTOL:
			player_pistol_reload ();
			break;
		case WEAPON_SKULL:
			player_skull_reload ();
			break;
		case WEAPON_SHOT:
			player_shotgun_reload ();
			break;
		case WEAPON_AR:
			player_ar_reload ();
			break;
		case WEAPON_UZI:
			player_uzi_reload ();
			break;
		case WEAPON_RL:
			player_rl_reload ();
			break;
		case WEAPON_SNIPER:
			player_sniper_reload ();
			break;
		case WEAPON_PPISTOL:
			player_ppistol_reload ();
			break;
		case WEAPON_NEEDLER:
			player_needler_reload ();
			break;
		default:
			player_generic_reload ();
			break;
	}
	self.reload_time = time + .1;
	
	self.frame = Player_GetFrame(PLAYER_RELOAD, 0);
	if ((self.frame + self.fireframe) > Player_GetFrame(PLAYER_RELOAD, 1)) {
		if (self.weaponframe == 0) {
			self.melee_time = 0;
			self.donefire = 0;
			self.fireframe = 0;
			player_run();
			return;
		}
		else {
			self.fireframe = 5;
			//self.frame = Player_GetFrame(PLAYER_RELOAD, 0) + 3;
		}
		
	}
		
	self.frame = self.frame + self.fireframe;
	
	self.fireframe = self.fireframe + 1;
};

void () player_hshot = [ 103, player_hshot ]
{
	if (!W_CheckNoAmmo ())
	{
		return;
	}
	self.effects = (self.effects | EF_MUZZLEFLASH);
	self.weaponframe = (self.weaponframe + WEAPON_SHOTGUN);
	if ((self.weaponframe == TE_LAVASPLASH))
	{
		self.weaponframe = WEAPON_SHOTGUN;
		player_run ();
		return;
	}
	self.attack_finished = (time + 0.5);
};

void () Melee_Finished =
{
	self.donefire = 1;
	self.weaponframe = 0;
	player_run ();
};

void () player_shot_melee =
{
	self.weaponframe = (self.weaponframe + WEAPON_SHOTGUN);
	if ((self.weaponframe >= 41))
	{
		Melee_Finished ();
		return;
	}
	if ((self.weaponframe == 33))
	{
		W_Melee ();
	}
	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};

void () player_skull_melee =
{
	self.weaponframe = (self.weaponframe + WEAPON_SKULL);
	if ((self.weaponframe >= 16))
	{
		Melee_Finished ();
		return;
	}
	if ((self.weaponframe == 1))
	{
		W_Melee ();
	}
	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};

void () player_rl_melee =
{
	self.weaponframe += 1;
	if ( self.weaponframe > 65 )
	{
		Melee_Finished ();
		return;
	}
	if ( self.weaponframe == 62 )
	{
		W_Melee ();
	}
	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};

void () player_hshot_melee =
{
	self.weaponframe = (self.weaponframe + WEAPON_SHOTGUN);
	if ((self.weaponframe >= 26))
	{
		Melee_Finished ();
		return;
	}
	if ((self.weaponframe == 23))
	{
		W_Melee ();
	}
	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};

void () player_shot2_melee =
{
	self.weaponframe = (self.weaponframe + WEAPON_SHOTGUN);
	if ((self.weaponframe >= 33))
	{
		Melee_Finished ();
		return;
	}
	if ((self.weaponframe == 30))
	{
		W_Melee ();
	}
	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};

void () player_nail_melee =
{
	self.weaponframe = (self.weaponframe + WEAPON_SHOTGUN);
	if ((self.weaponframe >= 34))
	{
		Melee_Finished ();
		return;
	}
	if ((self.weaponframe == SVC_FINALE))
	{
		W_Melee ();
	}
	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};

void () player_sniper_melee = 
{
	self.weaponframe = (self.weaponframe + WEAPON_SHOTGUN);
	if ((self.weaponframe >= 34))
	{
		Melee_Finished ();
		return;
	}
	if ((self.weaponframe == 32))
	{
		W_Melee ();
	}
	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};

void () player_ppistol_melee = 
{
	self.weaponframe += 1;
	if ((self.weaponframe >= 43))
	{
		Melee_Finished ();
		return;
	}
	if ((self.weaponframe == 38))
	{
		W_Melee ();
	}
	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = 0;
};

void () player_needler_melee = 
{
	self.weaponframe += 1;
	if ((self.weaponframe >= 47))
	{
		Melee_Finished ();
		return;
	}
	if ((self.weaponframe == 34))
	{
		W_Melee ();
	}
	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = 0;
};

void () player_melee = [ 0, player_melee ]
{
	local float ftype;
	ftype = PLAYER_ATTACK_MELEE;
	
	self.melee_time = time + .6;
	switch (self.weapon) {
		case WEAPON_SHOT:
			startwframe(self, 28);
			player_shot2_melee ();
			break;
		case WEAPON_PISTOL:
			startwframe(self, 30);
			player_shot_melee ();
			break;
		case WEAPON_SKULL:
			startwframe(self, 1);
			player_skull_melee ();
			break;
		case WEAPON_AR:
			startwframe(self, 29);
			player_nail_melee ();
			break;
		case WEAPON_UZI:
			startwframe(self, 21);
			player_hshot_melee ();
			break;
		case WEAPON_RL:
			startwframe(self, 58);
			player_rl_melee ();
			break;
		case WEAPON_SNIPER:
			startwframe(self, 29);
			player_sniper_melee ();
			break;
		case WEAPON_PPISTOL:
			startwframe(self, 36);
			player_ppistol_melee ();
			break;
		case WEAPON_NEEDLER:
			startwframe(self, 30);
			player_needler_melee ();
			break;
		default:
			self.melee_time = 0;
			return;
	}

	self.frame = Player_GetFrame(ftype, 0);

	if ((self.frame + self.fireframe) > Player_GetFrame(ftype, 1)) {
		if (self.weaponframe == 0) {
			self.melee_time = 0;
			self.donefire = 0;
			self.fireframe = 0;
			player_run();
		}
		else {
			self.frame = Player_GetFrame(ftype, 1);
		}
		return;
	}
		
	self.frame = self.frame + self.fireframe;
	
	self.fireframe = self.fireframe + 1;
};

void () pre_player_melee =
{
	player_melee ();
	self.weaponframe = 0;
	self.fireframe = 1;
	self.frame = Player_GetFrame(PLAYER_ATTACK_MELEE, 0);
};

void () Throw_Finished =
{
	self.donefire = 1;
	self.weaponframe = 0;
	player_run ();
};

void () player_shot_throw =
{
	self.weaponframe = (self.weaponframe + WEAPON_SHOTGUN);
	if ((self.weaponframe >= 51))
	{
		Throw_Finished ();
		return;
	}
	if ((self.weaponframe == 47))
	{
		W_ThrowGrenade ();
	}
	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};

void () player_skull_throw =
{
	self.weaponframe = (self.weaponframe + WEAPON_SKULL);
	if ((self.weaponframe >= 16))
	{
		Throw_Finished ();
		return;
	}
	//if ((self.weaponframe == 47))
	//{
	//	W_ThrowGrenade ();
	//}
	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};

void () player_shot2_throw =
{
	self.weaponframe += 1;
	if (self.weaponframe >= 41)
	{
		Throw_Finished ();
		return;
	}
	if (self.weaponframe == 39)
	{
		W_ThrowGrenade ();
	}
	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};

void () player_nail_throw = 
{
	self.weaponframe = (self.weaponframe + WEAPON_SHOTGUN);
	if ((self.weaponframe >= 42))
	{
		Throw_Finished ();
		return;
	}
	if ((self.weaponframe == 39))
	{
		W_ThrowGrenade ();
	}
	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};

void () player_uzi_throw =
{
	self.weaponframe += 1;

	if (self.weaponframe >= 33)
	{
		Throw_Finished ();
		return;
	}
	if (self.weaponframe == 30)
	{
		W_ThrowGrenade ();
	}
	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};

void () player_sniper_throw =
{
	self.weaponframe += 1;

	if (self.weaponframe >= 42)
	{
		Throw_Finished ();
		return;
	}
	if (self.weaponframe == 39)
	{
		W_ThrowGrenade ();
	}
	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};

void () player_rl_throw =
{
	self.weaponframe += 1;

	if (self.weaponframe >= 58)
	{
		Throw_Finished ();
		return;
	}
	if (self.weaponframe == 55)
	{
		W_ThrowGrenade ();
	}
	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};

void () player_ppistol_throw =
{
	self.weaponframe += 1;

	if (self.weaponframe >= 50)
	{
		Throw_Finished ();
		return;
	}
	if (self.weaponframe == 46)
	{
		W_ThrowGrenade ();
	}
	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};

void () player_needler_throw =
{
	self.weaponframe += 1;

	if (self.weaponframe >= 56)
	{
		Throw_Finished ();
		return;
	}
	if (self.weaponframe == 52)
	{
		W_ThrowGrenade ();
	}
	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};

void () player_throw_grenade = [ 0, player_throw_grenade ]
{
	local float ftype;
	ftype = PLAYER_THROW_NADE;
	
	self.nade_time = time + .8;
	switch (self.weapon) {
		case WEAPON_PISTOL:
			startwframe(self, 44);
			player_shot_throw ();
			break;
		case WEAPON_SHOT:
			startwframe(self, 34);
			player_shot2_throw ();
			break;
		case WEAPON_AR:
			startwframe(self, 34);
			player_nail_throw ();
			break;
		case WEAPON_UZI:
			startwframe(self, 26);
			player_uzi_throw ();
			break;
		case WEAPON_RL:
			startwframe(self, 51);
			player_rl_throw ();
			break;
		case WEAPON_SNIPER:
			startwframe(self, 35);
			player_sniper_throw ();
			break;
		case WEAPON_PPISTOL:
			startwframe(self, 43);
			player_ppistol_throw ();
			break;
		case WEAPON_NEEDLER:
			startwframe(self, 48);
			player_needler_throw ();
			break;
		default:
			self.nade_time = 0;
			return;
	}
	
	self.frame = Player_GetFrame(ftype, 0);

	if ((self.frame + self.fireframe) > Player_GetFrame(ftype, 1)) {
		if (self.weaponframe == 0) {
			self.donefire = 0;
			self.fireframe = 0;
			player_run();
		}
		else {
			self.frame = Player_GetFrame(ftype, 1);
		}
		return;
	}
		
	self.frame = self.frame + self.fireframe;

	self.fireframe = self.fireframe + 1;
};

void () pre_player_throw_grenade =
{
	player_throw_grenade ();
	self.weaponframe = 0;
	self.fireframe = 0;
	self.frame = Player_GetFrame(PLAYER_THROW_NADE, 0);
};

//============================================================================

void () player_nail2 = [ 103, player_nail2 ]
{
	if (!W_CheckNoAmmo ())
	{
		return;
	}
	self.effects = (self.effects | EF_MUZZLEFLASH);
	if (!self.button0)
	{
		player_run ();
		return;
	}
	/*
	self.weaponframe += 1;
	if (self.weaponframe > 3)
	{
		self.weaponframe = 1;
	}
	*/
	SuperDamageSound ();
	W_FireNail2 ();
	//self.attack_finished = (time + 0.1);
};

void () player_ar1 = [ 103, player_ar1 ]
{
	if (!W_CheckNoAmmo ())
	{
		return;
	}
	self.effects = (self.effects | EF_MUZZLEFLASH);
	if (!self.button0)
	{
		player_run ();
		return;
	}

	self.weaponframe += 1;
	if (self.weaponframe > 3)
	{
		self.weaponframe = 1;
	}
	
	SuperDamageSound ();
	//W_FireNail2 ();
	//self.attack_finished = (time + 0.1);
};

void(float num_bubbles) DeathBubbles;

void() PainSound =
{
	

	if (self.health < 0)
		return;

	if (self.pain_finished > time)
		return;

	// change pain sound depending on means of death
	switch (damage_mod)
	{
	case MOD_TELEFRAG:
	case MOD_TELEFRAGDEFLECT:
		sound (self, CHAN_VOICE, "player/teledth1.wav", 1, ATTN_NONE);
		return;
	case MOD_DROWN:
		DeathBubbles(1);
		if (random() > 0.5)
			sound (self, CHAN_VOICE, "player/drown1.wav", 1, ATTN_NORM);
		else
			sound (self, CHAN_VOICE, "player/drown2.wav", 1, ATTN_NORM);
		return;
	case MOD_SLIME:
		// FIX ME: put in some steam here
		if (self.waterlevel == 3)
			DeathBubbles(1);
	case MOD_LAVA:
		if (random() > 0.5)
			sound (self, CHAN_VOICE, "player/lburn1.wav", 1, ATTN_NORM);
		else
			sound (self, CHAN_VOICE, "player/lburn2.wav", 1, ATTN_NORM);
		return;
	default:
	 	if (self.health >= 40)
		stuffcmd(self,"play player/hit1.wav\n"); 
		//else
		//stuffcmd(self,"play player/pain1.wav\n"); 
		
	}
};
void()  Player_PainAnimation =
{
	self.pain_time = time + .4;
	PainSound();
};

void() player_pain =
{
	if (self.weaponstate != WS_IDLE)
		return;

	if (self.invisible_finished > time)
		return;         // eyes don't have pain frames

	Player_PainAnimation ();
};

void() DeathBubblesSpawn =
{
local entity    bubble;
	if (self.owner.waterlevel != 3)
	{
		remove(self);
		return;
	}
	bubble = spawn();
	setmodel (bubble, "progs/s_bubble.spr");
	setorigin (bubble, self.owner.origin + '0 0 24');
	bubble.movetype = MOVETYPE_NOCLIP;
	bubble.solid = SOLID_NOT;
	bubble.velocity = '0 0 15';
	bubble.nextthink = time + 0.5;
	bubble.think = bubble_bob;
	bubble.classname = "bubble";
	bubble.frame = 0;
	bubble.bubble_state = 0;
	setsize (bubble, '-8 -8 -8', '8 8 8');
	self.nextthink = time + 0.1;
	self.think = DeathBubblesSpawn;
	self.bubble_count = self.bubble_count - 1;
	if (self.bubble_count <= 0)
		remove(self);
};

void(float num_bubbles) DeathBubbles =
{
local entity    bubble_spawner;
	
	bubble_spawner = spawn();
	setorigin (bubble_spawner, self.origin);
	bubble_spawner.movetype = MOVETYPE_NONE;
	bubble_spawner.solid = SOLID_NOT;
	bubble_spawner.nextthink = time + 0.1;
	bubble_spawner.think = DeathBubblesSpawn;
	bubble_spawner.owner = self;
	bubble_spawner.bubble_count = num_bubbles;
};


void() DeathSound =
{
local float             rs;

	// water death sounds
	if (self.waterlevel == 3)
	{
		DeathBubbles(5);
		sound (self, CHAN_VOICE, "player/h2odeath.wav", 1, ATTN_NONE);
		return;
	}
	
	rs = rint ((random() * 1) + 1);
	if (rs == 1)
		stuffcmd (self, "play player/death1.wav\n");
	if (rs == 2)
		stuffcmd (self, "play player/death1.wav\n");
	
};

void() PlayerDead =
{
	self.nextthink = -1;
// allow respawn after a certain time
	self.deadflag = DEAD_DEAD;
};

vector(float dm) VelocityForDamage =
{
	local vector v;

	if (vlen(damage_inflictor.velocity)>0)
	{
		v = 0.5 * damage_inflictor.velocity;
		v = v + (25 * normalize(self.origin-damage_inflictor.origin));
		v_z = 100 + 240 * random();
		v_x = v_x + (200 * crandom());
		v_y = v_y + (200 * crandom());
		//dprint ("Velocity gib\n");                
	}
	else
	{
		v_x = 100 * crandom();
		v_y = 100 * crandom();
		v_z = 200 + 100 * random();
	}

	//v_x = 100 * crandom();
	//v_y = 100 * crandom();
	//v_z = 200 + 100 * random();

	if (dm > -50)
	{
	//      dprint ("level 1\n");
		v = v * 0.7;
	}
	else if (dm > -200)
	{
	//      dprint ("level 3\n");
		v = v * 2;
	}
	else
		v = v * 10;

	return v;
};

void(string gibname, float dm) ThrowGib =
{
	local   entity new;

	new = spawn();
	new.origin = self.origin;
	setmodel (new, gibname);
	setsize (new, '0 0 0', '0 0 0');
	new.velocity = VelocityForDamage (dm);
	new.movetype = MOVETYPE_BOUNCE;
	new.solid = SOLID_NOT;
	new.avelocity_x = random()*600;
	new.avelocity_y = random()*600;
	new.avelocity_z = random()*600;
	new.think = SUB_Remove;
	new.nextthink = time + 10 + random()*10;
	new.frame = 0;
	new.flags = 0;
};

void(string gibname, float dm) ThrowHead =
{
	setmodel (self, gibname);
	self.frame = 0;
	self.nextthink = -1;
	self.movetype = MOVETYPE_BOUNCE;
	self.takedamage = DAMAGE_NO;
	self.solid = SOLID_NOT;
	self.view_ofs = '0 0 8';
	setsize (self, '-16 -16 0', '16 16 56');
	self.velocity = VelocityForDamage (dm);
	self.origin_z = self.origin_z - 24;
	self.flags = self.flags - (self.flags & FL_ONGROUND);
	self.avelocity = crandom() * '0 600 0';
};


void() GibPlayer =
{
	ThrowHead ("progs/h_player.mdl", self.health);
	ThrowGib ("progs/gib1.mdl", self.health);
	ThrowGib ("progs/gib2.mdl", self.health);
	ThrowGib ("progs/gib3.mdl", self.health);

	self.deadflag = DEAD_DEAD;

	if (damage_attacker.classname == "teledeath")
	{
		sound (self, CHAN_VOICE, "player/teledth1.wav", 1, ATTN_NONE);
		return;
	}
		
	if (random() < 0.5)
		sound (self, CHAN_VOICE, "player/gib.wav", 1, ATTN_NONE);
	else
		sound (self, CHAN_VOICE, "player/udeath.wav", 1, ATTN_NONE);
		
	stuffcmd(self,"chase_active 1\n");
	self.setup_death = #TRUE;
};

void() PlayerDropStuff =
{
	local	string	s, t;	

	if (numberserverinfokey("dq") != 0)
	{
		if (self.super_damage_finished > time)
		{
			DropQuad (self.super_damage_finished - time);
			s = ftos(rint(self.super_damage_finished - time));
			t = " lost a quad with ";
			if (deathmatch == 4)
				t = " lost an OctaPower with ";
			bprint4 (PRINT_LOW, self.netname, t, s, " seconds remaining\n");
		}
	}

	if (numberserverinfokey("dr") != 0)
	{
		if (self.invisible_finished > time)
		{
			s = ftos(rint(self.invisible_finished - time));
			bprint4 (PRINT_LOW, self.netname, " lost a ring with ", s, " seconds remaining\n");
			DropRing (self.invisible_finished - time);
		}
	}

	//DropBackpack();
	ThrowWeapon(self.weapon, 1);
}

void () Player_RunDeath = [ 0, Player_RunDeath ]
{
	self.walkframe++;
	self.frame = (Player_GetFrame(self.death_type, 0) - 1) + self.walkframe;
	if (self.frame >= (Player_GetFrame(self.death_type, 1) - 1))
	{
		PlayerDead();
		return;
	}
};

void () Player_AnimateDeath =
{
	local   float   i, dtype;
	
	i = random();

	if (i < 0.5)
		dtype = PLAYER_DEATH1;
	else
		dtype = PLAYER_DEATH2;
		
	self.death_type = dtype;
	self.walkframe = 0;
	self.frame = Player_GetFrame(self.death_type, 0) - 1;
	Player_RunDeath ();
};


void() PlayerDie =
{
	self.items = self.items - (self.items & IT_INVISIBILITY);

CTF_Flag_Drop();

	PlayerDropStuff();

	self.invisible_finished = 0;    // don't die as eyes
	self.invincible_finished = 0;
	self.super_damage_finished = 0;
	self.radsuit_finished = 0;
	self.modelindex = modelindex_player;    // don't use eyes

	self.weaponmodel="";
	self.view_ofs = '0 0 -8';
	self.deadflag = DEAD_DYING;
	self.solid = SOLID_NOT;
	self.flags = self.flags - (self.flags & FL_ONGROUND);
	self.movetype = MOVETYPE_TOSS;
	if (self.velocity_z < 10)
		self.velocity_z = self.velocity_z + random()*300;
	/*
	if (self.nade_lives == 4)
	{
	DeathNade(self.origin)
	DeathNade(self.origin)
	DeathNade(self.origin)
	DeathNade(self.origin)
	}
	if (self.nade_lives == 3)
	{
	DeathNade(self.origin)
	DeathNade(self.origin)
	DeathNade(self.origin)
	}
	if (self.nade_lives == 2)
	{
	DeathNade(self.origin)
	DeathNade(self.origin)
	}
	if (self.nade_lives == 1)
	{
	DeathNade(self.origin)
	}
	*/
	DeathSound();
	
	self.angles_x = 0;
	self.angles_z = 0;
	
	Set_FOV( FOV_DEFAULT );
	self.pfov = FOV_DEFAULT;
	
	stuffcmd(self,"chase_active 1\n");
	self.setup_death = #TRUE;
	
	Player_AnimateDeath ();
};

void() set_suicide_frame =
{       // used by klill command and diconnect command
	PlayerDie();
	
	/*
	if (self.model != "progs/player.mdl")
		return; // allready gibbed
	self.frame = 0;//$deatha11; // XAVIOR: FIXME
	self.solid = SOLID_NOT;
	self.movetype = MOVETYPE_TOSS;
	self.deadflag = DEAD_DEAD;
	self.nextthink = -1;
	*/
}

void () pull_finished =
{
	self.donefire = 1;
	self.weaponframe = 0;
	player_run ();
};

void() player_generic_pull = 
{
self.weaponframe += 1;
if (self.weaponframe >= 1) 
	{
	pull_finished();
	return;
	}
if (self.weaponframe == 2)
	{
	sound (self, CHAN_WEAPON, "weapons/equip/ppist.wav", 1, ATTN_NORM);
	}
	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};	

void() player_needler_pull = 
{
self.weaponframe += 1;
if (self.weaponframe >= 68) 
	{
	pull_finished();
	return;
	}
if (self.weaponframe == 59)
	{
	sound (self, CHAN_WEAPON, "weapons/equip/needler.wav", 1, ATTN_NORM);
	}

	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};	
void() player_ppist_pull = 
{
self.weaponframe += 1;
if (self.weaponframe >= 56) 
	{
	pull_finished();
	return;
	}
if (self.weaponframe == 51)
	{
	sound (self, CHAN_WEAPON, "weapons/equip/ppist.wav", 1, ATTN_NORM);
	}

	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};	
void() player_sniper_pull = 
{
self.weaponframe += 1;
if (self.weaponframe >= 53) 
	{
	pull_finished();
	return;
	}
if (self.weaponframe == 46)
	{
	sound (self, CHAN_WEAPON, "weapons/equip/sniper.wav", 1, ATTN_NORM);
	}

	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};	
void() player_rl_pull = 
{
self.weaponframe += 1;
if (self.weaponframe >= 79) 
	{
	pull_finished();
	return;
	}
if (self.weaponframe == 70)
	{
	sound (self, CHAN_WEAPON, "weapons/equip/rocket.wav", 1, ATTN_NORM);
	}
	
	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};	
void() player_uzi_pull = 
{
self.weaponframe += 1;
if (self.weaponframe >= 40)
	{
	pull_finished();
	return;
	}
if (self.weaponframe == 36)
	{
	sound (self, CHAN_WEAPON, "weapons/equip/smg.wav", 1, ATTN_NORM);
	}
	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};	
void() player_shotgun_pull = 
{
self.weaponframe += 1;
if (self.weaponframe >= 48)
	{
	pull_finished();
	return;
	}
if (self.weaponframe == 46)
	{
	sound (self, CHAN_WEAPON, "weapons/equip/shotgun.wav", 1, ATTN_NORM);
	}

	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};	

void() player_ar_pull = 
{
self.weaponframe += 1;
if (self.weaponframe >= 55)
	{
	pull_finished();
	return;
	}
if (self.weaponframe == 46)
	{
	sound (self, CHAN_WEAPON, "weapons/equip/ar.wav", 1, ATTN_NORM);
	}

	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};
void() player_shot_pull = 
{

self.weaponframe += 1;

if (self.weaponframe >= 62)
	{
	pull_finished();
	return;
	}
if (self.weaponframe == 53)
	{
	sound (self, CHAN_WEAPON, "weapons/equip/pistol.wav", 1, ATTN_NORM);
	}

	SuperDamageSound ();
	self.attack_finished = (time + 0.2);
	self.impulse = MSG_BROADCAST;
};

void() player_pull = [ 0, player_pull ]
{
	local float ftype;
	ftype = PLAYER_PULL;
	
	// allow players to interrupt reload for melee/nade throw
	if (self.impulse == 29) {
		pre_player_melee ();
		return;
	}
	else if (self.impulse == 28) {
		
		{
		Set_FOV ( FOV_DEFAULT );
		self.pfov = FOV_DEFAULT;
	if (self.selnade == GRENADE_REGULAR)
	{
		if (self.nade_lives > 0) {
		pre_player_throw_grenade ();
		self.nade_lives -= 1;
		sprint (self, ftos(self.nade_lives));
		sprint (self, " grenades\n");
		return; }
		else
		centerprint (self, "No Grenades\n");
	}
	else
	{	
	if (self.plasma_lives > 0) {
		pre_player_throw_grenade ();
		self.plasma_lives -= 1;
		sprint (self, ftos(self.plasma_lives));
		sprint (self, " Plasma grenades\n");
		return; }
		else
		centerprint (self, "No Plasma Grenades\n");
	}
		}
}
	else if (self.pull_time == -1) {
		self.pull_time = time + .6;
		player_run();
		return;
	}
	
	switch (self.weapon) {
		case WEAPON_PISTOL:
			startwframe(self, 52);
			player_shot_pull ();
			break;
		case WEAPON_SHOT:
			startwframe(self, 41);
			player_shotgun_pull ();
			break;
		case WEAPON_AR:
			startwframe(self, 45);
			player_ar_pull ();
			break;
		case WEAPON_UZI:
			startwframe (self, 34);
			player_uzi_pull ();
			break;
		case WEAPON_RL:
			startwframe (self, 69);
			player_rl_pull ();
			break;
		case WEAPON_SNIPER:
			startwframe (self, 43);
			player_sniper_pull ();
			break;
		case WEAPON_PPISTOL:
			startwframe (self, 50);
			player_ppist_pull ();
			break;
		case WEAPON_NEEDLER:
			startwframe (self, 58);
			player_needler_pull ();
			break;
		default:
			startwframe (self, 1);
			player_generic_pull ();
			break;
	}
	
	self.frame = Player_GetFrame(ftype, 0);
	if ((self.frame + self.fireframe) > Player_GetFrame(ftype, 1)) {
		if (self.weaponframe == 0) {
			self.melee_time = 0;
			self.donefire = 0;
			self.fireframe = 0;
			player_run();
			return;
		}
		else {
			self.fireframe = 5;
			//self.frame = Player_GetFrame(ftype, 0) + 3;
		}
		
	}
		
	self.frame = self.frame + self.fireframe;
	
	self.fireframe = self.fireframe + 1;
};

void () pre_player_pull =
{
	player_pull ();
	self.weaponframe = 0;
	self.fireframe = 0;
	self.frame = Player_GetFrame(PLAYER_PULL, 0);
};
