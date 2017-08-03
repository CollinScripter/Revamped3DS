

void() MarioHome =
{
	local vector dir, vtemp, wantdir;
	local entity te;
	local float maxmove;
	maxmove = 85;		// maximum xyz value we're allowed to change in mid-air

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

void () Mario_Touch =
{
	if (other.takedamage != FALSE && other.health > 0) {
		T_Damage (other, self, self.owner, 50, MOD_SOLITUDE);	
		Add_Needle(self.owner, other, self.origin_x);
	}
	else if (self.lives > 0) {
		Bounce_Off_Walls ();
		self.lives -= 1;
		return;
	}
	
	remove(self);
};
void() dust =
{
	self.enemy.kill_amount += 1;
	self.enemy.frags += 1;
	self.enemy.needles -= 1;
	T_Damage (self.enemy, self, self.owner, 4, MOD_SOLITUDE);
	sound (self, CHAN_WEAPON, "weapons/crystal.wav", 1, ATTN_NORM);	
	createpinkdust(self.origin);
	remove(self);
};
void() misc_marion;
void() W_FireMario =
{
	local entity fshell;
	local vector spread;
	muzzleflash6();
	sound (self, CHAN_WEAPON, "weapons/bigneedler.wav", 1, ATTN_NORM); 

	spread = '3.60 3.60 0.10';
	
	
	fshell = spawn ();
	fshell.owner = self;
	fshell.health = 15;
	fshell.classname = "Needle-spikes";
	fshell.movetype = 9;
	fshell.solid = SOLID_BBOX;
	fshell.takedamage = DAMAGE_AIM;
	fshell.th_die = dust;
	makevectors (self.v_angle);
	fshell.velocity = v_forward + crandom()*spread_x*v_right + crandom()*spread_y*v_up;
	fshell.velocity = (fshell.velocity * 6550);
	fshell.angles = vectoangles (fshell.velocity);
	fshell.touch = Mario_Touch;
	fshell.armorvalue = time + 100000000;		// amount of time the needler projectile should stay alive
	fshell.nextthink = (time + 0.2);
	fshell.think = MarioHome;
	fshell.lives = 100000000;
	self.think = W_FireMario;
	self.nextthink = (time + 1.5);				// number of times the needle will bounce off walls
	setmodel (fshell, "progs/Bigneedproy.mdl");
	setsize (fshell, '-12 -12 -12', '12 12 12');
	setorigin (fshell, ((self.origin + (v_forward * 8)) + '0 0 16'));  //setorigin (fshell, ((self.origin + (v_forward * 8)) + '0 0 16'));

	
};

void() misc_marion =
{
local entity mario;

mario = spawn();

mario.solid = SOLID_SLIDEBOX;
mario.movetype = MOVETYPE_NONE;
mario.classname = "Mario";

setsize (mario, '-25 -25 -10', '25 25 50');
setorigin (mario, self.origin);

mario.think = W_FireMario && SUB_Remove;
mario.nextthink = (time + 1);
};