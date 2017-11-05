

void() normal_elite =
{
	local entity oldself;
	
	if (self.enemy != world)
	{
        if (self.enemy.health <= 0)
		{
            self.enemy = world;
		}
	}

	if (self.enemy == world)
	{ 
	oldself = self;
	self = spawn ();
	self.classname = "Needle-spikes";
      setorigin (self, oldself.origin);
      self.origin_z = self.origin_z + 2;
      self.solid = SOLID_SLIDEBOX;
      self.movetype = MOVETYPE_STEP;
	setmodel (self, "progs/elite.mdl");
	self.skin = 0;
	setsize (self, VEC_HULL_MIN, VEC_HULL_MAX);
      self.health = 200;
	self.elite = 0;
	self.th_stand = elite_stand1;
	self.th_walk = elite_walk1;
	self.th_run = elite_run1;
	self.th_die = elite_die;
	self.th_melee = elite_melee;
	self.th_missile = elite_nail1;
	self.th_pain = elite_pain;

        if (oldself.target != string_null)
        {
            self.target = oldself.target;
        }

        walkmonster_start();
	
	  oldself.enemy = self;
	  self = oldself;
		TOTAL_MONS += 1;		//Adds a monster to the world, so that waves can be set.
	}

};

void() red_elite =
{
	local entity oldself;
	
	if (self.enemy != world)
	{
        if (self.enemy.health <= 0)
		{
            self.enemy = world;
		}
	}

	if (self.enemy == world)
	{ 
	oldself = self;
	self = spawn ();
	self.classname = "Needle-spikes";
      setorigin (self, oldself.origin);
      self.origin_z = self.origin_z + 2;
      self.solid = SOLID_SLIDEBOX;
      self.movetype = MOVETYPE_STEP;
	setmodel (self, "progs/elite.mdl");
	self.skin = 1;
	setsize (self, VEC_HULL_MIN, VEC_HULL_MAX);
      self.health = 300;
	self.elite = 1;		//States what Elite type it is, so Different stats/weapons can be set.
	self.th_stand = elite_stand1;
	self.th_walk = elite_walk1;
	self.th_run = elite_run1;
	self.th_die = elite_die;
	self.th_melee = elite_melee;
	self.th_missile = elite_nail1;
	self.th_pain = elite_pain;

        if (oldself.target != string_null)
        {
            self.target = oldself.target;
        }

        walkmonster_start();
	
	  oldself.enemy = self;
	  self = oldself;
	TOTAL_MONS += 1;
	}

};
void() white_elite =
{
	local entity oldself;
	
	if (self.enemy != world)
	{
        if (self.enemy.health <= 0)
		{
            self.enemy = world;
		}
	}

	if (self.enemy == world)
	{ 
	oldself = self;
	self = spawn ();
	self.classname = "Needle-spikes";
      setorigin (self, oldself.origin);
      self.origin_z = self.origin_z + 2;
      self.solid = SOLID_SLIDEBOX;
      self.movetype = MOVETYPE_STEP;
	setmodel (self, "progs/elite.mdl");
	self.skin = 3;
	setsize (self, VEC_HULL_MIN, VEC_HULL_MAX);
      self.health = 400;
	self.elite = 2;
	self.th_stand = elite_stand1;
	self.th_walk = elite_walk1;
	self.th_run = elite_run1;
	self.th_die = elite_die;
	self.th_melee = elite_melee;
	self.th_missile = elite_nail1;
	self.th_pain = elite_pain;

        if (oldself.target != string_null)
        {
            self.target = oldself.target;
        }

        walkmonster_start();
	
	  oldself.enemy = self;
	  self = oldself;
	TOTAL_MONS += 1;
	}

};

void() normal_grunt =
{
	local entity oldself;
	
	if (self.enemy != world)
	{
        if (self.enemy.health <= 0)
		{
            self.enemy = world;
		}
	}

	if (self.enemy == world)
	{ 
	oldself = self;
	self = spawn ();
	self.classname = "Needle-spikes";
      setorigin (self, oldself.origin);
      self.origin_z = self.origin_z + 2;
      self.solid = SOLID_SLIDEBOX;
      self.movetype = MOVETYPE_STEP;
	setmodel (self, "progs/soldier.mdl");
	self.skin = 0;
	self.elite = 1;		//For Melee damage
	setsize (self, '-16 -16 -24', '16 16 40');
      self.health = 40 * round/1.5;
	self.th_stand = army_stand1;
	self.th_walk = army_walk1;
	self.th_run = army_run1;
	self.th_missile = army_atk1;
	self.th_pain = army_pain;
	self.th_die = army_die;
	self.th_melee = grunt_melee1;

        if (oldself.target != string_null)
        {
            self.target = oldself.target;
        }

        walkmonster_start();
	
	  oldself.enemy = self;
	  self = oldself;
	TOTAL_MONS += 1;
	}

};