//For Blaster.
void(vector org) BlasterTouch =
{
	self.velocity = '0 0 0';
		
	if (other.takedamage) {
			spawn_touchblood (18);
			T_Damage (other, self, self.owner, 15);
			}
	else
	{
		puff_org = self.origin;
	}
	remove(self);
};
//Sniper
void(vector org) SniperTouch =
{
	self.velocity = '0 0 0';
		
	if (other.takedamage) {
			spawn_touchblood (18);
			T_Damage (other, self, self.owner, 15);
			}
	else
	{
		puff_org = self.origin;
	}
	remove(self);
};
