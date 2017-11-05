// Solitude Items: weapons, ammo, misc.

// GetPlayerWeapons: 
// return how many weapons a player is holding.
// also used for finding out if the player is holding a certain weapon.
float (float pweapons) GetPlayerWeapons =
{
	local float i;
	
	if (pweapons & WEAPON_PISTOL)
		i++;
	if (pweapons & WEAPON_SKULL)
		i++;
	if (pweapons & WEAPON_SHOT)
		i++;
	if (pweapons & WEAPON_AR)
		i++;
	if (pweapons & WEAPON_UZI)
		i++;
	if (pweapons & WEAPON_RL)
		i++;
	if (pweapons & WEAPON_SNIPER)
		i++;
	if (pweapons & WEAPON_PPISTOL)
		i++;
	if (pweapons & WEAPON_SWORD)
		i++;
	if (pweapons & WEAPON_NEEDLER)
		i++;
	if (pweapons & WEAPON_PRIFLE)
		i++;
/*
	if (pweapons & WEAPON_PISTOL)
		i++;
	if (pweapons & WEAPON_PISTOL)
		i++;
*/
	return i;
};

// Returns the amount of ammo an entity or player has either in the primary or secondary clip
// PS. It's hackish, but it works :)
float (entity t_plyr, float t_wep, float cliptype) GetAmmoCount =
{
	local float oldweapon, rtval;
	
	oldweapon = t_plyr.weapon;
	t_plyr.weapon = t_wep;
	W_UpdateAmmoCounts( t_plyr );
	if (cliptype)
		rtval = t_plyr.currentammo;
	else
		rtval = t_plyr.armorvalue;
		
	t_plyr.weapon = oldweapon;
	W_UpdateAmmoCounts( t_plyr );
	
	return rtval;
};

// Sets the ammo of a new or dropped weapon, as opposed to the function below which...
void ( entity t_wep, float weptype ) SetWeaponAmmo =
{
	local float stammo;
	stammo = W_GetMaxClip( weptype, 1 );

	switch( weptype ) {
		case WEAPON_PISTOL:
			t_wep.exshells = 24;
			t_wep.ammo_shells = stammo;
			break;
		case WEAPON_SKULL:
			t_wep.exshells = 0;
			t_wep.ammo_shells = stammo;
			break;
		case WEAPON_SHOT:
			t_wep.exshells2 = 20;
			t_wep.ammo_shells2 = stammo;
			break;
		case WEAPON_AR:
			t_wep.exnails = 24;
			t_wep.ammo_nails = stammo;
			break;
		case WEAPON_UZI:
			t_wep.exhshells = 24;
			t_wep.ammo_hshells = stammo;
			break;
		case WEAPON_RL:
			t_wep.exrockets = 2;
			t_wep.ammo_rockets = stammo;
			break;
		case WEAPON_SNIPER:
			t_wep.exsniper = 10;
			t_wep.ammo_sniper = stammo;
			break;
		case WEAPON_PPISTOL:
			t_wep.exppistol = 0;
			t_wep.ammo_ppistol = stammo;
			break;
		case WEAPON_SWORD:
			t_wep.exppistol = 0;
			t_wep.ammo_ppistol = stammo;
			break;
		case WEAPON_NEEDLER:
			t_wep.exneedler = 90;
			t_wep.ammo_needler = stammo;
			break;
		case WEAPON_PRIFLE:
			t_wep.exprifle = 0;
			t_wep.ammo_prifle = stammo;
			break;			
		default:
			break;
	}
};

// sets ammo to a specific clip aspect of a weapon (current clip or extended clip)
void ( entity t_ent, float weptype, float cliptype, float newamt ) SetAmmoFor =
{
/*
_bprint(ftos(GetAmmoCount(t_ent, weptype, cliptype)), "\n");
_bprint(ftos(newamt), "\n");
_bprint(ftos(W_GetMaxClip(weptype, cliptype)), "\n");
*/
	if ( (GetAmmoCount(t_ent, weptype, cliptype)+newamt) > W_GetMaxClip(weptype, cliptype) ) {
		newamt = W_GetMaxClip(weptype, cliptype) - GetAmmoCount(t_ent, weptype, cliptype);
		if (newamt < 0)
			newamt = 0;
	}

	switch ( weptype ) {
		case WEAPON_PISTOL:
			if (!cliptype || cliptype > 1)
				t_ent.exshells += newamt;
			if (cliptype)
				t_ent.ammo_shells += newamt;
			break;
		case WEAPON_SKULL:
			if (!cliptype || cliptype > 1)
				t_ent.exshells += newamt;
			if (cliptype)
				t_ent.ammo_shells += newamt;
			break;
		case WEAPON_SHOT:
			if (!cliptype || cliptype > 1)
				t_ent.exshells2 += newamt;
			if (cliptype)
				t_ent.ammo_shells2 += newamt;
			break;
		case WEAPON_AR:
			if (!cliptype || cliptype > 1)
				t_ent.exnails += newamt;
			if (cliptype)
				t_ent.ammo_nails += newamt;
			break;
		case WEAPON_UZI:
			if (!cliptype || cliptype > 1)
				t_ent.exhshells += newamt;
			if (cliptype)
				t_ent.ammo_hshells += newamt;
			break;
		case WEAPON_RL:
			if (!cliptype || cliptype > 1)
				t_ent.exrockets += newamt;
			if (cliptype)
				t_ent.ammo_rockets += newamt;
			break;
		case WEAPON_SNIPER:
			if (!cliptype || cliptype > 1)
				t_ent.exsniper += newamt;
			if (cliptype)
				t_ent.ammo_sniper += newamt;
			break;
		case WEAPON_PPISTOL:
			if (!cliptype || cliptype > 1)
				t_ent.exppistol += newamt;
			if (cliptype)
				t_ent.ammo_ppistol += newamt;
			break;
		case WEAPON_SWORD:
			if (!cliptype || cliptype > 1)
				t_ent.exsword += newamt;
			if (cliptype)
				t_ent.ammo_sword += newamt;
			break;
		case WEAPON_NEEDLER:
			if (!cliptype || cliptype > 1)
				t_ent.exneedler += newamt;
			if (cliptype)
				t_ent.ammo_needler += newamt;
			break;
		case WEAPON_PRIFLE:
			if (!cliptype || cliptype > 1)
				t_ent.exprifle += newamt;
			if (cliptype)
				t_ent.ammo_prifle += newamt;
			break;			
		default:
			_bprint("SetAmmoFor: invalid weapon type specified\n");
			break;
	}
};

void ( entity t_from, entity t_to, float wtype, float aremove ) CopyAmmo =
{
	W_UpdateAmmoCounts( t_from );
	SetAmmoFor( t_to, wtype, 0, t_from.armorvalue );
	SetAmmoFor( t_to, wtype, 1, t_from.currentammo );

	if (aremove == 1) {
		SetAmmoFor( t_from, wtype, 0, (-1 * t_from.armorvalue) );
		SetAmmoFor( t_from, wtype, 1, (-1 * t_from.currentammo) );
	}
};

void () weapon_becometouch =
{
	self.think = SUB_Remove;
	self.nextthink = time + 30;
	self.touch = weapon_touch;
};

string ( float wtype ) weapon_getlaymodel =
{
	switch (wtype)
	{
		case WEAPON_SHOT:
			return ("progs/g_shot.mdl");
			break;
		case WEAPON_PISTOL:
			return ("progs/g_pistol.mdl");
			break;
		case WEAPON_SKULL:
			//return ("GameTypes/OddBall/g_skull.mdl");
			break;
		case WEAPON_AR:
			return ("progs/g_nail.mdl");
			break;
		case WEAPON_UZI:
			return ("progs/g_uzi.mdl");
			break;
		case WEAPON_RL:
			return ("progs/g_rocket.mdl");
			break;
		case WEAPON_SNIPER:
			return ("progs/g_sniper.mdl");
			break;
		case WEAPON_PPISTOL:
			return ("progs/g_plpist.mdl");
			break;
		case WEAPON_SWORD:
			return ("progs/g_axe.mdl");
			break;
		case WEAPON_NEEDLER:
			return ("progs/g_needler.mdl");
			break;
		case WEAPON_PRIFLE:
			return ("progs/g_plrifl.mdl");
			break;
		default:
			return ("progs/player.mdl");
			break;
	}
};
	
void (float wtype, float ttype) ThrowWeapon =
{
	local entity newthrow;
	newthrow = spawn();
	newthrow.owner = self;
	newthrow.movetype = MOVETYPE_BOUNCE;
	newthrow.solid = SOLID_BBOX;
	newthrow.classname = "weapon_pickup";
	newthrow.flags = FL_ITEM;
	newthrow.think = weapon_becometouch;
	newthrow.nextthink = time + 1;
	
	newthrow.weapon = wtype;
	
	if (ttype == 1)	{	// throwing an existing weapon
		CopyAmmo(self, newthrow, wtype, 1);
		newthrow.lives = 1;
	}
	else
		SetWeaponAmmo(newthrow, wtype);
	
	makevectors (self.v_angle);
	if (self.v_angle_x)
	{
		newthrow.velocity = ((((v_forward * 45) + (v_up * 200)) + ((crandom () * v_right) * TE_LAVASPLASH)) + ((crandom () * v_up) * TE_LAVASPLASH));
	}
	else
	{
		newthrow.velocity = aim (self, 10000);
		newthrow.velocity = (newthrow.velocity * 45);
		newthrow.velocity_z = 200;
	}
	
	newthrow.gravity = 3;
	newthrow.solid = SOLID_TRIGGER;
	
	setsize (newthrow, '-16 -16 0', '16 16 56');
	
	setmodel( newthrow, weapon_getlaymodel( wtype ) );
	
	setorigin (newthrow, ((self.origin + '0 0 16') + (v_right * CONTENT_SKY)));
};

// respawn the weapon
void () weapon_activate =
{
	if (self.lives == 1) {
		remove( self );
		return;
	}
	if (self.mdl)
		setmodel(self, self.mdl);
	self.touch = weapon_touch;
}

void () weapon_touch =
{
	local entity oself;
	local float addweapon, newweapon;
	
	oself = self;
	//
	if (!(other.flags & FL_CLIENT))
		return;

	if (other.ishuman != #TRUE)
		if (other.attack_finished < time)
			other.canpickup_time = time + .1;
		
	self.mdl = self.model;
		
	if ( (other.items & self.weapon) ) {
		if (self.weapon & WEAPON_PPISTOL || self.weapon & WEAPON_PRIFLE)				// weapons that don't have an extended clip
			if ( W_GetMaxClip(self.weapon, 1) <= GetAmmoCount(other, self.weapon, 1) )
				return;
	
		if ( W_GetMaxClip(self.weapon, 0) <= GetAmmoCount(other, self.weapon, 0) )
			return;

		if (self.weapon & WEAPON_PPISTOL || self.weapon & WEAPON_PRIFLE)
			SetAmmoFor( other, self.weapon, 1, self.currentammo );
		else
			SetAmmoFor( other, self.weapon, 0, self.armorvalue );
		//SetAmmoFor( other, self.weapon, 1, self.currentammo );
		
		W_UpdateAmmoCounts( other );
		self.touch = SUB_Null;
		setmodel( self, string_null );
		self.nextthink = time + 30;
		self.think = weapon_activate;
		return;
	}
	
	if (other.canpickup_time > time) {
		if (other.weapon == self.weapon || GetPlayerWeapons(other.items) == 2 )
			addweapon = 2;		// drop current weapon and replace it
		else
		{
			addweapon = 1;		// add other weapon and switch to it
		}
			
		other.canpickup_time = 0;
	}
	else {
		if (time > other.pickup_time) {
			other.pickup_time = time + .5;
			return;
		}
	}

	if (self.weapon == IT_NAILGUN)	//Assault rifle
	{
	other.groundwep = 1;
	stuffcmd (other, "cl_ww 1\n");
	}
	
	else if (self.weapon == IT_LIGHTNING)//Plasma Pistol
	{
	other.groundwep = 1;
	stuffcmd (other, "cl_ww 2\n");
	}
	
	else if (self.weapon == IT_SUPER_SHOTGUN)	//Shootie
	{
	other.groundwep = 1;
	stuffcmd (other, "cl_ww 3\n");
	}
	
	else if (self.weapon == IT_EXTRA_WEAPON)	
	{
	other.groundwep = 1;
	stuffcmd (other, "cl_ww 4\n");
	}
	
	else if (self.weapon == IT_ROCKET_LAUNCHER)	
	{
	other.groundwep = 1;
	stuffcmd (other, "cl_ww 5\n");
	}
	
	else if (self.weapon == IT_SHOTGUN)	
	{
	other.groundwep = 1;
	stuffcmd (other, "cl_ww 6\n");
	}
	
	else if (self.weapon == IT_SUPER_NAILGUN)	
	{
	other.groundwep = 1;
	stuffcmd (other, "cl_ww 7\n");
	}
	
	else if (self.weapon == IT_GRENADE_LAUNCHER)	
	{
	other.groundwep = 1;
	stuffcmd (other, "cl_ww 8\n");
	}
	
	else
	stuffcmd (other, "cl_ww 0\n");	
	
	if (addweapon)
	{
		other.attack_finished = time + .1;	// so the player doesnt reload when picking up a new weapon
		if (addweapon == 1) {
			other.items = other.items | self.weapon;
			sprint(other,"New weapon added to your inv\n");
		}
		else if (addweapon == 2) {			// replace current weapon
			newweapon = self.weapon;
			other.items = other.items - other.weapon;
			other.items = other.items | self.weapon;
			self = other;
			ThrowWeapon(self.weapon, 1);
			W_WeaponSwitch(newweapon);
			W_SetCurrentAmmo();
			self = oself;
		}
		CopyAmmo( self, other, self.weapon, 0 );
		W_UpdateAmmoCounts(other);
		self.touch = SUB_Null;
		setmodel( self, string_null );
		self.nextthink = time + 30;
		self.think = weapon_activate;
		return;
	}
};

void () weapon_start =
{
	if (!self.weapon) {
		_bprint("weapon_start: weapon with no .weapon set!\n");
		remove(self);
	}
	
	self.classname = "weapon_pickup";			// so bots can recognize it
	self.flags = FL_ITEM;
	
	precache_model( weapon_getlaymodel( self.weapon ) );
	setmodel( self, weapon_getlaymodel( self.weapon ) );
	
	self.gravity = 3;
	self.solid = SOLID_TRIGGER;
	
	setsize (self, '-16 -16 0', '16 16 56');
	
	SetWeaponAmmo( self, self.weapon );
	self.touch = weapon_touch;
};

// WEAPONS
void () weapon_shotgun =
{
	self.weapon = WEAPON_PISTOL;
	weapon_start ();
};
void () weapon_pistol =
{
	weapon_shotgun();
};
void() weapon_skull =
{
	self.weapon = WEAPON_SKULL;
	weapon_start ();
};
void() weapon_supershotgun =
{
	self.weapon = WEAPON_SHOT;
	weapon_start ();
};

void() weapon_nailgun =
{
	self.weapon = WEAPON_AR;
	weapon_start ();
};
void() weapon_ar =
{
	weapon_nailgun();
};

void() weapon_supernailgun =
{
	self.weapon = WEAPON_UZI;
	weapon_start ();
};
void() weapon_uzi =
{
	weapon_supernailgun ();
};

void() weapon_grenadelauncher =
{
	self.weapon = WEAPON_PPISTOL;
	weapon_start ();
};
void() weapon_ppistol =
{
	weapon_grenadelauncher ();
};

void() weapon_rocketlauncher =
{
	self.weapon = WEAPON_RL;
	weapon_start ();
};

void() weapon_lightning =
{
	self.weapon = WEAPON_SNIPER;
	weapon_start ();
};
void() weapon_sniperrifle =
{
	weapon_lightning ();
};

void() weapon_sword =
{
	self.weapon = WEAPON_SWORD;
	weapon_start ();
};

void() weapon_plasmapistol =
{
	self.weapon = WEAPON_PPISTOL;
	weapon_start ();
};

void() weapon_plasmarifle =
{
	self.weapon = WEAPON_PRIFLE;
	weapon_start ();
};

void() weapon_needler =
{
	self.weapon = WEAPON_NEEDLER;
	weapon_start ();
};