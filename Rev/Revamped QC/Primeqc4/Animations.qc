
//The Rocket Is gay and messed up. I have to use it In the Fire Function I guess >:(
void()	player_missle14 =	[$missle14, player_missle15] {self.weaponframe=22;};
void()	player_missle15 =	[$missle15, player_missle16] {self.weaponframe=23;};
void()	player_missle16 =	[$missle16, player_missle17] {self.weaponframe=24;};
void()	player_missle17 =	[$missle17, player_missle18] {self.weaponframe=25;};
void()	player_missle18 =	[$missle18, player_missle19] {self.weaponframe=26;};
void()	player_missle19 =	[$missle19, player_missle20] {self.weaponframe=27;};
void()	player_missle20 =	[$missle20, player_missle21] {self.weaponframe=28;};
void()	player_missle21 =	[$missle21, player_missle22] {self.weaponframe=39;};
void()	player_missle22 =	[$missle22, player_missle23] {self.weaponframe=30;};
void()	player_missle23 =	[$missle23, player_missle24] {self.weaponframe=31;};
void()	player_missle24 =	[$missle24, player_missle25] {self.weaponframe=32;};
void()	player_missle25 =	[$missle25, player_missle26] {self.weaponframe=33;};
void()	player_missle26 = {self.weaponframe=34;};

//Shooting Animations For Richochet beam. Any Weapon that Has transforming anims, needs These kinda frames
void()	player_missle45 =	[$missle1, player_missle46] {self.weaponframe=49;};
void()	player_missle46 =	[$missle2, player_missle47] {self.weaponframe=50;};
void()	player_missle47 =	[$missle3, player_missle48] {self.weaponframe=51;};
void()	player_missle48 =	[$missle4, player_missle49] {self.weaponframe=52;};
void()	player_missle49 =	[$missle5, player_missle50] {self.weaponframe=53;};
void()	player_missle50 =	[$missle6, player_missle51] {self.weaponframe=54;};
void()	player_missle51 =	[$missle7, player_missle52] {self.weaponframe=55;};
void()	player_missle52 =	[$missle8, player_missle53] {self.weaponframe=56;};
void()	player_missle53 =	[$missle9, player_missle54] {self.weaponframe=57;};
void()	player_missle54 =	[$missle10, player_missle55] {self.weaponframe=58;};
void()	player_missle55 = {self.weaponframe=59;};

// Shooting Animations for The blaster.
void()	player_missle56 =	[$missle1, player_missle57] {self.weaponframe=1;};
void()	player_missle57 =	[$missle2, player_missle58] {self.weaponframe=2;};
void()	player_missle58 =	[$missle3, player_missle59] {self.weaponframe=3;};
void()	player_missle59 =	[$missle4, player_missle60] {self.weaponframe=4;};
void()	player_missle60 =	[$missle5, player_missle61] {self.weaponframe=5;};
void()	player_missle61 =	[$missle6, player_missle62] {self.weaponframe=6;};
void()	player_missle62 =	[$missle7, player_missle63] {self.weaponframe=7;};
void()	player_missle63 =	[$missle8, player_missle64] {self.weaponframe=8;};
void()	player_missle64 =	[$missle9, player_missle65] {self.weaponframe=9;};
void()	player_missle65 =	[$missle10, player_missle66] {self.weaponframe=10;};
void()	player_missle66 = {self.weaponframe=11;};


void (entity t_plyr, float t_frame) startwframe =
{
	if (t_plyr.weaponframe < t_frame)
		t_plyr.weaponframe = t_frame;
};

void () Fire_finished =
{
	self.donefire = 1;
	self.weaponframe = 0;
	player_run ();
};
void() Fire_nail =
{
	self.weaponframe += 1;
	if (self.weaponframe > 11)
	{
	Fire_finished();
	}
 	if (self.weaponframe == 2)
	{
	W_FireSplaser();
	}
};
void() Fire_Sniper =
{
	self.weaponframe += 1;
	if (self.weaponframe > 11)
	{
	Fire_finished();
	}
 	if (self.weaponframe == 2)
	{
	W_FireSniper();
	}
};
void() Fire_Magma =
{
	self.weaponframe += 1;
	if (self.weaponframe > 11)
	{
	Fire_finished();
	}
 	if (self.weaponframe == 2)
	{
	W_FireMagma();
	}
};
void() FireAnimations =
{
	switch(self.weapon)
		{
		case IT_SPLASER:
			{
			startwframe(self, 1);
			Fire_nail();
			}
			break;
		case IT_SNIPER:
			{
			startwframe(self, 1);
			Fire_Sniper();
			}
			break;
		case IT_MAGMA:
			{
			startwframe(self, 1);
			Fire_Magma();
			}
			break;
		}
};