

/*
================
Debris By Mexicouger (Bounce code from Needler. Not that advanced yet)
=================
*/
vector(entity proj) Debrisbounce =		// returns the velocity for bouncing off walls
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
	proj.velocity = v_forward * 50;//proj.old_velocity;

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
	
	if (other.classname == "gun_shells")
	sound (other, CHAN_AUTO, "weapons/shell.wav", 1, ATTN_NORM);
// set correct angles of our new velocity
	proj.angles = vectoangles (vec);

	// this is required to make downward slopes not stop the projectile
	proj.flags = proj.flags - ( proj.flags & FL_ONGROUND );

	return vec;
	
};

#define drandom() (2*(random()-0.5))



void(vector org) debris =
{
local entity rock;
local float rand;
rand = random();
rock = spawn ();  
rock.classname = "rock";
rock.movetype = MOVETYPE_BOUNCE;
rock.owner = self;


// This is all about how fast the debris goes. (My biggest problem)
makevectors (self.angles);
rock.velocity = v_forward * v_up * v_right * random();


rock.velocity_z = rock.velocity_z + 5 + 20*random();
rock.velocity_x = rock.velocity_x + 3 + 20*drandom();
rock.velocity_y = rock.velocity_y + 3 + 20*drandom();
rock.velocity = (rock.velocity * 12);
rock.avelocity = '300 300 300' * drandom();
rock.angles = vectoangles (rock.velocity);
rock.solid = SOLID_NOT;
rock.touch = Debrisbounce;

// Rock duration (How long the rocks are alive until they disapear/Explode
rock.nextthink = time + 2 * rand*4;
rock.think = SUB_Remove;
// The whole setting up the model thing. Sets up the sprite and location.
rock.origin = self.origin + v_forward*8*random() + '0 0 16';
setorigin (rock, org);
setsize (rock, '0 0 0', '3 3 3');
setmodel (rock, "maps/B_f1.bsp");
};