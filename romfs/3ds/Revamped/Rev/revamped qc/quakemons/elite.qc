
//Credit to Frag.machine for partial code!
void () info_elite_think =
{
	local float r;
	r = floor(random()*4);

	if (TOTAL_MONS <= MAX_MONS)	//Prevents spawning, so Waves can be set.
		{
  	if (r == 0)
	{
	normal_elite();
	}
	else if (r == 1)
	{
	normal_grunt();
	}
	else if (r == 2)
	{
	if (round < 3)
	normal_elite() || normal_grunt();
	else
	red_elite();	//Sets a limitation, so Red Elites don't appear until Round 3
	}
	else if (r == 3)
	{
	if (round < 4)
	normal_elite() || normal_grunt() || red_elite();	//Randomly picks an enemy to spawn.
	else
	white_elite();
	}
		}
	
    // finally, let's schedule the execution of our "think" function
    self.think = info_elite_think;
    self.nextthink = (time + 5);
}; 

void () info_elite_start =
{

	kill_count();
	FIREFIGHT = 1;	//Sets Firefight to 1, so there are lives in play.
	localcmd ("teamplay 1\n");
	F_LIVES = 7;
	localcmd ("cl_life 8\n");

	precache_sound ("firefight.wav");
	
	precache_model ("progs/elite.mdl");
	precache_model ("progs/h_elite.mdl");
	precache_model ("progs/grenade.mdl");

	precache_sound ("elite/ogdrag.wav");
	precache_sound ("elite/ogdth.wav");
	precache_sound ("elite/ogpain1.wav");
	precache_sound ("elite/ogsawatk.wav");
	precache_sound ("elite/ogwake.wav");
	precache_sound ("elite/laugh1.wav");
	precache_sound ("elite/laugh2.wav");
	
	//Grunts
	precache_model ("progs/soldier.mdl");
	precache_model ("progs/h_guard.mdl");

	precache_sound ("soldier/death1.wav");
	precache_sound ("soldier/idle.wav");
	precache_sound ("soldier/pain1.wav");
	precache_sound ("soldier/pain2.wav");
	precache_sound ("soldier/sight1.wav");
	precache_sound ("soldier/laugh1.wav");
	precache_sound ("soldier/laugh2.wav");
	
	precache_sound ("soldier/unstoppable.wav");
	precache_sound ("soldier/kill_all.wav");
	

    self.enemy = world;
	
	
    self.think = info_elite_think;
    self.nextthink = time + 5;
}; 