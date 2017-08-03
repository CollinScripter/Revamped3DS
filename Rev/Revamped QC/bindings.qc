void ()
player_bindings =
{
	stuffcmd (self, "r_novis 0\n");
	stuffcmd (self, "alias r_novis \n");
	stuffcmd (self, "r_wateralpha 1\n");
	stuffcmd (self, "alias r_wateralpha echo r_wateralpha has been disabled on this server.\n");
	stuffcmd (self, "chase_active 0\n");
	stuffcmd (self, "alias chase_active echo chase_active has been disabled on this server.\n");
	stuffcmd (self, "r_draworder 0\n");
	stuffcmd (self, "alias r_draworder echo r_draworder has been disabled on this server.\n");
	stuffcmd (self, "alias scr_ofsx echo screen offsets have been disabled on this server.\n");	
	stuffcmd (self, "alias scr_ofsy echo screen offsets have been disabled on this server.\n");	
	stuffcmd (self, "alias scr_ofsz echo screen offsets have been disabled on this server.\n");
	
	vote_aliases ();
	self.pflag = self.pflag | POQ_BINDINGS_SENT;
	
	bprint ("Player Bindings Sent\n");
};

void ()
player_bindings_think =
{
	local entity e;

	e = self;
	self = e.owner;
	remove (e);
	player_bindings ();
};

void ()
player_bindings_begin =
{
	local entity e;

	e = spawn ();
	e.owner = self;
	e.think = player_bindings_think;
	e.nextthink = time + 2;
};