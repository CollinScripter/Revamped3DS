void () DrawBeam = 
{
   local vector org;
   org = (self.origin) + '0 0 16';
   WriteByte(MSG_BROADCAST, SVC_TEMPENTITY);
   WriteByte(MSG_BROADCAST, TE_LIGHTNING1);
   WriteEntity(MSG_BROADCAST, world);
   WriteCoord(MSG_BROADCAST, org_x);
   WriteCoord(MSG_BROADCAST, org_y);
   WriteCoord(MSG_BROADCAST, org_z);
   WriteCoord(MSG_BROADCAST, self.hook.origin_x);
   WriteCoord(MSG_BROADCAST, self.hook.origin_y);
   WriteCoord(MSG_BROADCAST, self.hook.origin_z);	
};

void() pull =
{
		if (self.owner.hooking == 1)
		{
		self.owner.velocity = normalize(self.origin - self.owner.origin);
		self.owner.velocity = self.owner.velocity * 500;
		self.think = pull;
		self.nextthink = time + 0.1;
		}
		else
		{
		self.owner.hooking = 0;
		remove(self);
		sound (self.owner, CHAN_WEAPON, "grapple/grreset.wav", 1, ATTN_NORM);
		}	
};

void() hookdamage =
{
if (self.enemy.health)
{
	self.owner.velocity = normalize(self.origin - self.owner.origin);
	self.owner.velocity = self.owner.velocity * 500;
	
	T_Damage(self.enemy, self, self.owner, 2);

	self.origin = self.enemy.origin;
	self.think = hookdamage;
	self.nextthink = time + 0.1;
}
else
{
	self.owner.hooking = 0;
	remove(self);
	sound (self.owner, CHAN_WEAPON, "grapple/grreset.wav", 1, ATTN_NORM);	
}
};

void() PullHook =
{
	if (other == self.owner)
		return;

	if (other.classname == "grapple") // Pull
	{
			self.solid = SOLID_NOT;
			self.movetype = MOVETYPE_NONE;
			self.think = pull;
			self.nextthink = time;
      }
	if (other.takedamage && other.health)
	{
			self.think = hookdamage;
			self.enemy = other;
			self.solid = SOLID_NOT;
			self.nextthink = time;
	}
else
	remove(self);
	sound (self.owner, CHAN_WEAPON, "grapple/grhit.wav", 1, ATTN_NORM);	
	
};


void() BreakHook =
{
	if (self.hooking == 1)
	{
	remove(self.hook);
	self.hooking = 0;
	sound (self, CHAN_WEAPON, "grapple/grreset.wav", 1, ATTN_NORM);	
	}
};

void () FireHook =
{
	local entity hooky;
	hooky = spawn();
	setorigin(hooky, self.origin + self.view_ofs);
	setmodel(hooky, "progs/null.spr");
	setsize (hooky, '0 0 0', '0 0 0');
	hooky.solid = SOLID_BBOX;
	hooky.movetype = MOVETYPE_FLYMISSILE;
	makevectors(self.v_angle);
	self.aiment = hooky;
	hooky.velocity = v_forward * 1500;
	hooky.owner = self;
	self.hook = hooky;
	hooky.classname = "hookend";
	self.hooking = 1;
	hooky.touch = PullHook;
	//hooky.cansplash = 1; // If my splash tutorial is installed, uncomment this line
	sound (self, CHAN_WEAPON, "grapple/grfire.wav", 1, ATTN_NORM);	
};

void() CheckRope =
{
	if (self.hooking == 1 && self.hook.classname == "hookend")
	{
		DrawBeam ();
	}

};