// Solitude defs
#define DEFAULT_GRAVITY			340
#define DEFAULT_MAXSPEED		170			// max walk speed on ground

.float next_jump_time;		// next time the player can jump (usually after landing)
.float setup_death;			// setup respawn timer on player death
void () Player_SetupDeath;

.float needles;				// how many needler needles a player has in him

void () W_StartWeapon;
float (float wep, float cliptype) W_GetMaxClip;
void (float wtype, float ttype) ThrowWeapon;
void () player_throw_grenade;
void () pre_player_throw_grenade;
void () pre_player_melee;
void ( entity t_ent, float weptype, float cliptype, float newamt ) SetAmmoFor;
void () NeedlerHome;

.float selnade; // the type of nade being thrown
#define GRENADE_REGULAR		0
#define GRENADE_STICKY		1

.float weaponheat;

.entity pp_cooldown;

.float aflag;

.float pickup_time, canpickup_time;

.float lives;		// times an item can respawn

.float exshells;
.float exshells2;
.float exhshells;
.float exnails;
.float exrockets;
.float excells;

//sniper rifle
.float ammo_sniper;
.float exsniper;

// plasma pistol
.float ammo_ppistol;
.float exppistol;

// plasma rifle
.float ammo_prifle;
.float exprifle;
.float prifle_heat;			// plasma rifle fires faster the longer it's fired

// energy sword
.float ammo_sword;
.float exsword;

// needler
.float ammo_needler;
.float exneedler;
.float needler_heat;		// needler fires faster the longer it's held down

.float ammo_shells2;
.float ammo_hshells;

.float axhitme;

.float ohealth;		// for regen
.float regen;		///


// animations
//weapon frame
.float donefire;
.float wepanim;
//player frame
.float fireframe;
.float jump_time;
.float pain_time;
.float reload_time;
.float pull_time;
.float nade_time, melee_time;
.float death_type;

#define MOD_SOLITUDE		666			// undefined mode of death

// weapons
#define WEAPON_SWORD		IT_AXE
#define WEAPON_PISTOL		IT_SHOTGUN
#define WEAPON_SHOT			IT_SUPER_SHOTGUN
#define WEAPON_AR			IT_NAILGUN
#define WEAPON_UZI			IT_SUPER_NAILGUN
#define WEAPON_SNIPER		IT_GRENADE_LAUNCHER
#define WEAPON_RL			IT_ROCKET_LAUNCHER
#define WEAPON_PPISTOL		IT_LIGHTNING
#define WEAPON_NEEDLER		IT_EXTRA_WEAPON
#define WEAPON_PRIFLE		IT_EXTRA_WEAPON2
#define WEAPON_SKULL		IT_SKULL

// Zooming
.float pfov;
#define FOV_DEFAULT			90

// Frikbot
void(float to, float f) WriteByte;
void(float to, string s) WriteString;
void () reload;