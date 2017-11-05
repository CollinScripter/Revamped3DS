.vector flag_base;

.entity flag_ent;

.float update_print;

.float flag_state;
float FLAG_STATE_BASE	 = 0;
float FLAG_STATE_DROPPED = 1;
float FLAG_STATE_CARRIED = 2;

float TEAM_BLUE	= 14;
float TEAM_RED	= 5;

vector(entity e) realorg =
{
	return ((e.absmin + e.absmax) * 0.5);
};

string(float whichteam) CTF_TeamString =
{
	if (whichteam == TEAM_BLUE)
		return "\bBLUE";
	else
		return "\bRED";
};

void(float st) CTF_Flag_SetState =
{
	self.flag_state = st;

	if ( (st == FLAG_STATE_BASE) || (st == FLAG_STATE_DROPPED) )
	{
		self.owner = world;
		self.solid = SOLID_TRIGGER;
	}
	else if (st == FLAG_STATE_CARRIED)
		self.solid = SOLID_NOT;
};

// go back home
void() CTF_Flag_SendToBase =
{
	if (self.flag_state == FLAG_STATE_DROPPED)
	{
		bprint(CTF_TeamString(self.team));
		bprint(" flag was returned to base!\n");
	}
	
	setorigin(self, self.flag_base);
	CTF_Flag_SetState(FLAG_STATE_BASE);
	
};

// give the team points!
void() CTF_Flag_Capture =
{
	local entity e, oself;

	bprint(other.netname);
	bprint(" captured the ");
	bprint(CTF_TeamString(other.flag_ent.team));
	bprint(" flag!\n");
	
	centerprint(other, "\n");

	e = find(world, classname, "player");
	while (e)
	{
		if (e.team == other.team)
			e.frags = e.frags + 10;

		e = find(e, classname, "player");
	}
	
	// todo: play some noise and do happy dance

	oself = self;
	self = other.flag_ent;
	CTF_Flag_SendToBase();
	self = oself;

	other.flag_ent = world;
};

// braaaaains
void() CTF_Flag_Think =
{
	if (self.flag_state == FLAG_STATE_CARRIED)
	{
		// stay tracking with them, behind a little bit
		makevectors(self.owner.v_angle);
		setorigin (self, realorg(self.owner) + (v_forward * -14));
		
		if (self.owner.update_print < time)
		{
			centerprint(self.owner, " \n \n \n \n \n \n \n \n \nYou have the flag!\nReturn to your base.");
			self.owner.update_print = time + 1.5;
		}

		self.think = CTF_Flag_Think;
		self.nextthink = time;
	}
	else if (self.flag_state == FLAG_STATE_DROPPED)
	{
		self.nextthink = time + 30;
		self.think = CTF_Flag_SendToBase;
	}
};

void() CTF_Flag_Drop =
{
	local vector deviance;
	local entity oself;
	
	if (!self.flag_ent)
		return;

	bprint(self.netname);
	bprint(" has dropped the ");
	bprint(CTF_TeamString(self.flag_ent.team));
	bprint(" flag!\n");

	// throw it out in the direction of the owners velocity, plus a bit random
	deviance_x = random() * 20;
	deviance_y = random() * 20;
	deviance_z = 200;

	self.flag_ent.velocity = (self.flag_ent.velocity * 0.5) + deviance;
	
	oself = self;
	self = self.flag_ent;
	CTF_Flag_SetState(FLAG_STATE_DROPPED);
	self = oself;
	
	self.flag_ent.think = CTF_Flag_Think;
	self.flag_ent.nextthink = time;
	
	self.flag_ent = world;
};

// flag has been touched!
void() CTF_Flag_Touch =
{
	if (other.classname != "player")
		return;
	if (other.health <= 0)
		return;

	// not on my team
	if (other.team != self.team)
	{
		bprint(other.netname);
		bprint(" has picked up the ");
		bprint(CTF_TeamString(self.team));
		bprint(" flag!\n");
	
		self.owner = other;
		other.flag_ent = self;
	
		CTF_Flag_SetState(FLAG_STATE_CARRIED);

		self.think = CTF_Flag_Think;
		self.nextthink = time;
	}
	else
	{
		// on my team
		// dropped, return to base
		if (self.flag_state == FLAG_STATE_DROPPED)
		{
			bprint(other.netname);
			bprint(" returned the ");
			bprint(CTF_TeamString(other.team));
			bprint(" flag\n");

			CTF_Flag_SendToBase();
		}
		else if (self.flag_state == FLAG_STATE_BASE)
		{
			if (other.flag_ent)
				CTF_Flag_Capture(); // OH YEAH!
		}
	}
};

void() CTF_Flag_Finalise =
{
	self.movetype = MOVETYPE_TOSS;
	
	CTF_Flag_SetState(FLAG_STATE_BASE);
};

void(float whichteam) CTF_Flag_Init =
{
	local string m, s;
	local vector v;
	local entity flag;
	
	flag = spawn();
	
	flag.touch = CTF_Flag_Touch;
	flag.flags = FL_ITEM;
	flag.team = whichteam;
	
	if (whichteam == TEAM_BLUE)
	{
		m = "progs/b_s_key.mdl";
		s = "misc/basekey.wav";
		flag.items = IT_KEY1;
	}
	else
	{
		m = "progs/b_g_key.mdl";
		s = "misc/basekey.wav";
		flag.items = IT_KEY2;
	}
	
	precache_model (m);
	setmodel (flag, m);
	
	precache_sound (s);
	flag.noise = s;
	
	v = self.origin + '0 0 4';

	flag.flag_base = v;
	flag.owner = world;
	flag.team = whichteam;
	
	setsize (flag, VEC_HULL_MIN, VEC_HULL_MAX);
	setorigin(flag, v);
	
	flag.nextthink = time + 0.2;
	flag.think = CTF_Flag_Finalise;	
};

void() info_flag_blue =
{
	CTF_Flag_Init(TEAM_BLUE);
};

void() info_flag_red =
{
	CTF_Flag_Init(TEAM_RED);
};