// miscellaneous stuff

// Spawn some model.
void() func_model =
{
	precache_model( self.model );
	setmodel( self, self.model );
	setorigin( self, self.origin );
	
	self.movetype = MOVETYPE_NONE;
	self.solid = SOLID_BBOX;
	setsize(self, '-8 -8 -8', '8 8 8');
};