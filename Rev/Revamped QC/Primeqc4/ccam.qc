void () CCam;

  void () CCamChasePlayer = 
  {
     makevectors (self.v_angle);
     traceline ((self.origin + self.view_ofs),((((self.origin + self.view_ofs)
       + (v_forward * self.camview_z)) + (v_up * self.camview_x)) + (v_right * self.camview_y)),FALSE,self);
     setorigin (self.trigger_field,trace_endpos);
     WriteByte (MSG_ONE,5);
     WriteEntity (MSG_ONE,self.trigger_field);
     self.weaponmodel = "";
  };

  void () CCam = 
  {
     local entity camera;
     local entity spot;

	if (self.health <= BROKENITEMS)
	return;
     if (self.aflag == FALSE) 
     {
	self.cam = 1;
        self.aflag = TRUE;
        camera = spawn ();
        spot = spawn ();
        self.trigger_field = camera;
        camera.classname = "camera";
        camera.movetype = MOVETYPE_FLY;
        camera.solid = SOLID_NOT;
        setmodel (camera,"progs/eyes.mdl");
        setsize (camera,'0 0 0','0 0 0');
        makevectors (self.v_angle);
        traceline ((self.origin + self.view_ofs),(((self.origin + self.view_ofs)
           + (v_forward * -64.000))),FALSE,self);
        self.camview = '0 0 -64'; // added
        setorigin (camera,trace_endpos);
        camera.angles = self.angles;
        self.weaponmodel = "";
        msg_entity = self;
        WriteByte (MSG_ONE,5);
        WriteEntity (MSG_ONE,camera);
        WriteByte (MSG_ONE,10.000);
        WriteAngle (MSG_ONE,camera.angles_x);
        WriteAngle (MSG_ONE,camera.angles_y);
        WriteAngle (MSG_ONE,camera.angles_z);
		self.avelocity = '300 300 300';
		self.currentammo = self.mbombs;
		self.boostlives = 1;
		self.mbombs = 3;
		self.mball = 1;
		self.view_ofs = '0 0 8';
		setsize (self, '-12 -12 -40', '12 12 7');
      }
      else
      {
	//if (self.laid == LAYED)
	//return;	
		self.cam = 0;
        self.aflag = FALSE;
        msg_entity = self;
        WriteByte (MSG_ONE,5);
        WriteEntity (MSG_ONE,self);
        WriteByte (MSG_ONE,10);
        WriteAngle (MSG_ONE,self.angles_x);
        WriteAngle (MSG_ONE,self.angles_y);
        WriteAngle (MSG_ONE,self.angles_z);
        remove (self.trigger_field);
		if (self.health <= BROKENITEMS)	//For the Suit charging.(25 health)
		{}
	else
		{
	//self.weapon = IT_BLASTER;
        W_SetCurrentAmmo ();	
	self.origin = self.origin + v_up * 30;	//Solves the Spawning in the Ground Problem
		}
		self.mball = 0;
		self.view_ofs = '0 0 22';
		setsize (self, '-16 -16 -24', '16 16 32');
		self.weapon = IT_BLASTER;
		W_SetCurrentAmmo ();	
     }
  }