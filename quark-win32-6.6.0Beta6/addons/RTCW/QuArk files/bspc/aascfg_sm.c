//===========================================================================
// BSPC configuration file
// Wolfenstein
//===========================================================================

#define PRESENCE_NONE				1
#define PRESENCE_NORMAL				2
#define PRESENCE_CROUCH				4

bbox	//30x30x72
{
	presencetype	PRESENCE_NORMAL
	flags				0x0000
	mins				{-18, -18, -24}
	maxs				{18, 18, 48}
} //end bbox

bbox	//30x30x48
{
	presencetype	PRESENCE_CROUCH
	flags				0x0001
	mins				{-18, -18, -24}
	maxs				{18, 18,  24}
} //end bbox

settings
{
	phys_gravitydirection		{0, 0, -1}
	phys_friction				6
	phys_stopspeed				100
	phys_gravity				800
	phys_waterfriction			1
	phys_watergravity			400
	phys_maxvelocity			320
	phys_maxwalkvelocity		220
	phys_maxcrouchvelocity		100
	phys_maxswimvelocity		150
	phys_walkaccelerate			100
	phys_airaccelerate			0
	phys_swimaccelerate			0
	phys_maxstep				18
	phys_maxsteepness			0.7
	phys_maxwaterjump			17
	phys_maxbarrier				33
	phys_jumpvel				270
	phys_falldelta5				40
	phys_falldelta10			60
	rs_waterjump				400
	rs_teleport					50
	rs_barrierjump				100
	rs_startcrouch				300
	rs_startgrapple				500
	rs_startwalkoffledge		70
	rs_startjump				300
	rs_rocketjump				500
	rs_bfgjump					500
	rs_jumppad					250
	rs_aircontrolledjumppad		300
	rs_funcbob					300
	rs_startelevator			50
	rs_falldamage5				300
	rs_falldamage10				500
	//rs_maxfallheight			0
	rs_maxjumpfallheight		450
	rs_allowladders				1
} //end settings
