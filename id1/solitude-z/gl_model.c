/*
Copyright (C) 1996-1997 Id Software, Inc.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  

See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

*/
// gl_model.c -- model loading and caching

#include "gl_local.h"
#include "rc_wad.h"
#include "crc.h"

cvar_t gl_scaleModelTextures = {"gl_scaleModelTextures", "0"};
cvar_t gl_scaleTurbTextures = {"gl_scaleTurbTextures", "1"};
cvar_t gl_mipTexLevel = {"gl_mipTexLevel", "0"};
cvar_t gl_externalTextures_world = {"gl_externalTextures_world", "1"};
cvar_t gl_externalTextures_bmodels = {"gl_externalTextures_bmodels", "1"};

//#define HALFLIFEBSP	// enable Half-Life map support

model_t	*loadmodel;
char	loadname[32];	// for hunk tags

void Mod_LoadSpriteModel (model_t *mod, void *buffer);
void Mod_LoadBrushModel (model_t *mod, void *buffer, qbool worldmodel);
void Mod_LoadAliasModel (model_t *mod, void *buffer);
model_t *Mod_LoadModel (model_t *mod, qbool crash, qbool worldmodel);

byte	mod_novis[MAX_MAP_LEAFS/8];

#define	MAX_MOD_KNOWN	512
model_t	mod_known[MAX_MOD_KNOWN];
int		mod_numknown;

/*
===============
Mod_Init
===============
*/
void Mod_Init (void)
{
	memset (mod_novis, 0xff, sizeof(mod_novis));

	Cvar_Register (&gl_scaleModelTextures);
	Cvar_Register (&gl_scaleTurbTextures);
	Cvar_Register (&gl_mipTexLevel);
	Cvar_Register (&gl_externalTextures_world);
	Cvar_Register (&gl_externalTextures_bmodels);
}

/*
===============
Mod_Init

Caches the data if needed
===============
*/
void *Mod_Extradata (model_t *mod)
{
	void	*r;

	r = Cache_Check (&mod->cache);
	if (r)
		return r;

	Mod_LoadModel (mod, true, false);

	if (!mod->cache.data)
		Sys_Error ("Mod_Extradata: caching failed");
	return mod->cache.data;
}

/*
===============
Mod_PointInLeaf
===============
*/
mleaf_t *Mod_PointInLeaf (vec3_t p, model_t *model)
{
	mnode_t		*node;
	float		d;
	mplane_t	*plane;
	
	if (!model || !model->nodes)
		Sys_Error ("Mod_PointInLeaf: bad model");

	node = model->nodes;
	while (1)
	{
		if (node->contents < 0)
			return (mleaf_t *)node;
		plane = node->plane;
		d = DotProduct (p,plane->normal) - plane->dist;
		if (d > 0)
			node = node->children[0];
		else
			node = node->children[1];
	}

	return NULL;	// never reached
}


/*
===================
Mod_DecompressVis
===================
*/
byte *Mod_DecompressVis (byte *in, model_t *model)
{
	static byte	decompressed[MAX_MAP_LEAFS/8];
	int		c;
	byte	*out;
	int		row;

	row = (model->numleafs+7)>>3;	
	out = decompressed;

#if 0
	memcpy (out, in, row);
#else
	if (!in)
	{	// no vis info, so make all visible
		while (row)
		{
			*out++ = 0xff;
			row--;
		}
		return decompressed;
	}

	do
	{
		if (*in)
		{
			*out++ = *in++;
			continue;
		}
	
		c = in[1];
		in += 2;
		while (c)
		{
			*out++ = 0;
			c--;
		}
	} while (out - decompressed < row);
#endif
	
	return decompressed;
}

byte *Mod_LeafPVS (mleaf_t *leaf, model_t *model)
{
	if (leaf == model->leafs)
		return mod_novis;
	return Mod_DecompressVis (leaf->compressed_vis, model);
}

/*
===================
Mod_ClearAll
===================
*/
void Mod_ClearAll (void)
{
	int		i;
	model_t	*mod;
	
	for (i = 0, mod = mod_known; i < mod_numknown; i++, mod++)
		if (mod->type != mod_alias)
			mod->needload = true;
}

/*
==================
Mod_FindName

==================
*/
model_t *Mod_FindName (char *name)
{
	int		i;
	model_t	*mod;
	
	if (!name[0])
		Sys_Error ("Mod_ForName: NULL name");
		
//
// search the currently loaded models
//
	for (i = 0, mod = mod_known; i < mod_numknown; i++, mod++)
		if (!strcmp (mod->name, name) )
			break;
			
	if (i == mod_numknown)
	{
		if (mod_numknown == MAX_MOD_KNOWN)
			Sys_Error ("mod_numknown == MAX_MOD_KNOWN");
		strcpy (mod->name, name);
		mod->needload = true;
		mod_numknown++;
	}

	return mod;
}

/*
==================
Mod_TouchModel

==================
*/
void Mod_TouchModel (char *name)
{
	model_t	*mod;
	
	mod = Mod_FindName (name);
	
	if (!mod->needload)
	{
		if (mod->type == mod_alias)
			Cache_Check (&mod->cache);
	}
}

/*
==================
Mod_LoadModel

Loads a model into the cache
==================
*/
model_t *Mod_LoadModel (model_t *mod, qbool crash, qbool worldmodel)
{
	void	*d;
	unsigned *buf;
	byte	stackbuf[1024];		// avoid dirtying the cache heap

	if (!mod->needload)
	{
		if (mod->type == mod_alias)
		{
			d = Cache_Check (&mod->cache);
			if (d)
				return mod;
		}
		else
			return mod;		// not cached at all
	}

//
// because the world is so huge, load it one piece at a time
//
	if (!crash)
	{
	
	}

//
// load the file
//
	buf = (unsigned *)FS_LoadStackFile (mod->name, stackbuf, sizeof(stackbuf));
	if (!buf)
	{
		if (crash)
			Host_Error ("Mod_LoadModel: %s not found", mod->name);
		return NULL;
	}

//
// allocate a new model
//
	COM_FileBase (mod->name, loadname);

	loadmodel = mod;

//
// fill it in
//

// call the apropriate loader
	mod->needload = false;
	
	switch (LittleLong(*(unsigned *)buf))
	{
	case IDPOLYHEADER:
		Mod_LoadAliasModel (mod, buf);
		break;
		
	case IDSPRITEHEADER:
		Mod_LoadSpriteModel (mod, buf);
		break;
	
	default:
		Mod_LoadBrushModel (mod, buf, worldmodel);
		break;
	}

	return mod;
}

/*
==================
Mod_ForName

Loads in a model for the given name
==================
*/
model_t *Mod_ForName (char *name, qbool crash, qbool worldmodel)
{
	model_t	*mod;
	
	mod = Mod_FindName (name);
	
	return Mod_LoadModel (mod, crash, worldmodel);
}


qbool Img_HasFullbrights (byte *pixels, int size)
{
	int i;

	for (i = 0; i < size; i++)
		if (pixels[i] >= 224)
			return true;

	return false;
}


/*
===============================================================================

					BRUSHMODEL LOADING

===============================================================================
*/

byte	*mod_base;

/* Some id maps have textures with identical names but different looks.
We hardcode a list of names, checksums and alternative names to provide a way
for external texture packs to differentiate them. */
static struct {
	int md4;
	char *origname, *newname;
} translate_names[] = {
	{ 0x8a010dc0, "sky4", "sky4_blue" },
	{ 0xde688b77, "sky4", "sky1" },
	{ 0x45d110ec, "metal5_2", "metal5_2_arc" },
	{ 0x0d275f87, "metal5_2", "metal5_2_x" },
	{ 0xf8e27da8, "metal5_4", "metal5_4_arc" },
	{ 0xa301c52e, "metal5_4", "metal5_4_double" },
	{ 0xfaa8bf77, "metal5_8", "metal5_8_back" },
	{ 0x88792923, "metal5_8", "metal5_8_rune" },
	{ 0xfe4f9f5a, "plat_top1", "plat_top1_bolt" },
	{ 0x9ac3fccf, "plat_top1", "plat_top1_cable" },
	{ 0, NULL, NULL },
};

static char *TranslateTextureName (texture_t *tx)
{
	int i;
	int checksum;
	qbool checksum_done = false;

	for (i = 0; translate_names[i].origname; i++) {
		if (strcmp(tx->name, translate_names[i].origname))
			continue;
		if (!checksum_done) {
			checksum = Com_BlockChecksum(tx+1, tx->width*tx->height);
			checksum_done = true;
			//Com_DPrintf ("checksum(\"%s\") = 0x%x\n", tx->name, checksum);
		}
		if (translate_names[i].md4 == checksum) {
			//Com_DPrintf ("Translating %s --> %s\n", tx->name, translate_names[i].newname);
			assert (strlen(translate_names[i].newname) < sizeof(tx->name));
			return translate_names[i].newname;
		}
	}

	return NULL;
}

/*
=================
Mod_LoadTextures
=================
*/
void R_LoadBrushModelTextures (model_t *m);
void Mod_LoadTextures (lump_t *l)
{
	int		i, j, pixels, num, max, altmax;
	miptex_t	*mt;
	texture_t	*tx, *tx2;
	texture_t	*anims[10];
	texture_t	*altanims[10];
	dmiptexlump_t *m;

	if (!l->filelen)
	{
		loadmodel->textures = NULL;
		return;
	}
	m = (dmiptexlump_t *)(mod_base + l->fileofs);
	
	m->nummiptex = LittleLong (m->nummiptex);
	
	loadmodel->numtextures = m->nummiptex;
	loadmodel->textures = Hunk_AllocName (m->nummiptex * sizeof(*loadmodel->textures) , loadname);

	for (i = 0; i < m->nummiptex; i++)
	{
		m->dataofs[i] = LittleLong(m->dataofs[i]);
		if (m->dataofs[i] == -1)
			continue;
		mt = (miptex_t *)((byte *)m + m->dataofs[i]);
		mt->width = LittleLong (mt->width);
		mt->height = LittleLong (mt->height);
		for (j = 0; j < MIPLEVELS; j++)
			mt->offsets[j] = LittleLong (mt->offsets[j]);

		if ( (mt->width & 15) || (mt->height & 15) )
			Host_Error ("Texture %s is not 16 aligned", mt->name);

		pixels = mt->width*mt->height/64*85;
		if (loadmodel->halflifebsp)
			pixels += 2 + 256*3;	/* palette and unknown two bytes */
		tx = Hunk_AllocName (sizeof(texture_t) + pixels, loadname);
		loadmodel->textures[i] = tx;

		memcpy (tx->name, mt->name, sizeof(tx->name));
		tx->width = mt->width;
		tx->height = mt->height;

#ifdef HALFLIFEBSP
		if (loadmodel->halflifebsp && mt->offsets[0])
		{
			// the pixels immediately follow the structures
			memcpy (tx+1, mt+1, pixels);
			for (j = 0; j < MIPLEVELS; j++)
				tx->offsets[j] = mt->offsets[j] + sizeof(texture_t) - sizeof(miptex_t);
			continue;
		}
#endif

		if (mt->offsets[0])
		{
			// the pixels immediately follow the structures
			memcpy (tx+1, mt+1, pixels);

			for (j = 0; j < MIPLEVELS; j++)
				tx->offsets[j] = mt->offsets[j] + sizeof(texture_t) - sizeof(miptex_t);

			// HACK HACK HACK
			if (!strcmp(mt->name, "shot1sid") && mt->width==32 && mt->height==32
				&& CRC_Block((byte*)(mt+1), mt->width*mt->height) == 65393)
			{	// This texture in b_shell1.bsp has some of the first 32 pixels painted white.
				// They are invisible in software, but look really ugly in GL. So we just copy
				// 32 pixels from the bottom to make it look nice.
				memcpy (tx+1, (byte *)(tx+1) + 32*31, 32);
			}

			// just for r_fastturb's sake
			{
				byte *data = (byte *) &d_8to24table[*((byte *) mt + mt->offsets[0] + ((mt->height * mt->width) >> 1))];
				tx->flatcolor[0] = data[0];
				tx->flatcolor[1] = data[1];
				tx->flatcolor[2] = data[2];
			}
		}
	}

	R_LoadBrushModelTextures (loadmodel);

//
// sequence the animations
//
	for (i = 0; i < m->nummiptex; i++)
	{
		tx = loadmodel->textures[i];
		if (!tx || tx->name[0] != '+')
			continue;
		if (tx->anim_next)
			continue;	// already sequenced

	// find the number of frames in the animation
		memset (anims, 0, sizeof(anims));
		memset (altanims, 0, sizeof(altanims));

		max = (int)(unsigned char)tx->name[1];
		altmax = 0;
		if ( islower(max) )
			max -= 'a' - 'A';
		if ( isdigit(max) )
		{
			max -= '0';
			altmax = 0;
			anims[max] = tx;
			max++;
		}
		else if (max >= 'A' && max <= 'J')
		{
			altmax = max - 'A';
			max = 0;
			altanims[altmax] = tx;
			altmax++;
		}
		else
			Host_Error ("Bad animating texture %s", tx->name);

		for (j = i+1; j < m->nummiptex; j++)
		{
			tx2 = loadmodel->textures[j];
			if (!tx2 || tx2->name[0] != '+')
				continue;
			if (strcmp (tx2->name+2, tx->name+2))
				continue;

			num = (int)(unsigned char)tx2->name[1];
			if ( islower(num) )
				num -= 'a' - 'A';
			if ( isdigit(num) )
			{
				num -= '0';
				anims[num] = tx2;
				if (num+1 > max)
					max = num + 1;
			}
			else if (num >= 'A' && num <= 'J')
			{
				num = num - 'A';
				altanims[num] = tx2;
				if (num+1 > altmax)
					altmax = num+1;
			}
			else
				Host_Error ("Bad animating texture %s", tx->name);
		}

#define	ANIM_CYCLE	2
	// link them all together
		for (j = 0; j < max; j++)
		{
			tx2 = anims[j];
			if (!tx2)
				Host_Error ("Missing frame %i of %s",j, tx->name);
			tx2->anim_total = max * ANIM_CYCLE;
			tx2->anim_min = j * ANIM_CYCLE;
			tx2->anim_max = (j+1) * ANIM_CYCLE;
			tx2->anim_next = anims[ (j+1)%max ];
			if (altmax)
				tx2->alternate_anims = altanims[0];
		}
		for (j = 0; j < altmax; j++)
		{
			tx2 = altanims[j];
			if (!tx2)
				Host_Error ("Missing frame %i of %s",j, tx->name);
			tx2->anim_total = altmax * ANIM_CYCLE;
			tx2->anim_min = j * ANIM_CYCLE;
			tx2->anim_max = (j+1) * ANIM_CYCLE;
			tx2->anim_next = altanims[ (j+1)%altmax ];
			if (max)
				tx2->alternate_anims = anims[0];
		}
	}
}

int GL_LoadTextureImage (char *filename, char *identifier, int matchwidth, int matchheight, int mode);

static int LoadExternalTexture (texture_t *tx, int mode)
{
	char *name, *altname, *mapname /*, *groupname*/;
	qbool noscale;

	if (loadmodel->halflifebsp)
		return 0;

	if (loadmodel->isworldmodel) {
		if (!gl_externalTextures_world.value)
			return 0;
	} else {
		if (!gl_externalTextures_bmodels.value)
			return 0;
	}

	name = tx->name;
	altname = TranslateTextureName (tx);
	mapname = Cvar_String("mapname");
//	groupname = TP_GetMapGroupName(mapname, NULL);

#define TEX_LUMA 512

#define ISTURBTEX(name)		((name)[0] == '*')

	if (loadmodel->isworldmodel)
		mode |= TEX_WORLD;
	else
		mode |= TEX_MODEL;

	noscale = ((!gl_scaleModelTextures.value && !loadmodel->isworldmodel) ||
			(!gl_scaleTurbTextures.value && (tx->name[0] == '*')));
	if (noscale)
		mode |= TEX_NOSCALE;

	if (tx->name[0] == '*')
		 // turb textures are drawn without lightmaps, so we don't brighten them
		mode |= TEX_TURB;
#if 0  // Baker: everything too bright
	else
		mode |= TEX_BRIGHTEN;
#endif

	if (loadmodel->isworldmodel) {
		if ((tx->gl_texturenum = GL_LoadTextureImage (va("textures/%s/%s", mapname, name), name, 0, 0, mode))) {
			if (!ISTURBTEX(name))
				tx->fb_texturenum = GL_LoadTextureImage (va("textures/%s/%s_luma", mapname, name), va("@fb_%s", name), 0, 0, mode | TEX_LUMA);
		} else {
/*
			if (groupname) {
				if ((tx->gl_texturenum = GL_LoadTextureImage (va("textures/%s/%s", groupname, name), name, 0, 0, mode))) {
					if (!ISTURBTEX(name))
						tx->fb_texturenum = GL_LoadTextureImage (va("textures/%s/%s_luma", groupname, name), va("@fb_%s", name), 0, 0, mode | TEX_LUMA);
				}
			}
*/
		}
	} else {
		if ((tx->gl_texturenum = GL_LoadTextureImage (va("textures/bmodels/%s", name), name, 0, 0, mode))) {
			if (!ISTURBTEX(name))
				tx->fb_texturenum = GL_LoadTextureImage (va("textures/bmodels/%s_luma", name), va("@fb_%s", name), 0, 0, mode | TEX_LUMA);
		}
	}

	if (!tx->gl_texturenum && altname) {
		if ((tx->gl_texturenum = GL_LoadTextureImage (va("textures/%s", altname), altname, 0, 0, mode))) {
			if (!ISTURBTEX(name))
				tx->fb_texturenum = GL_LoadTextureImage (va("textures/%s_luma", altname), va("@fb_%s", altname), 0, 0, mode | TEX_LUMA);
		}
	}

	if (!tx->gl_texturenum) {
		if ((tx->gl_texturenum = GL_LoadTextureImage (va("textures/%s", name), name, 0, 0, mode))) {
			if (!ISTURBTEX(name))
				tx->fb_texturenum = GL_LoadTextureImage (va("textures/%s_luma", name), va("@fb_%s", name), 0, 0, mode | TEX_LUMA);
		}
	}

	// FIXME, no luma textures right now
	tx->fb_texturenum = 0;

//	if (tx->fb_texturenum)
//		tx->isLumaTexture = true;

	return tx->gl_texturenum;
}

static qbool LoadExternalSkyTexture (texture_t *tx)
{
	char *altname, *mapname;
	char solidname[MAX_QPATH], alphaname[MAX_QPATH];
	char altsolidname[MAX_QPATH], altalphaname[MAX_QPATH];
	byte alphapixel = 255;

	if (!gl_externalTextures_world.value)
		return false;

	altname = TranslateTextureName (tx);
	mapname = Cvar_String("mapname");
	snprintf (solidname, sizeof(solidname), "%s_solid", tx->name);
	snprintf (alphaname, sizeof(alphaname), "%s_alpha", tx->name);

	solidskytexture = GL_LoadTextureImage (va("textures/%s/%s", mapname, solidname), solidname, 0, 0, 0);
	if (!solidskytexture && altname) {
		snprintf (altsolidname, sizeof(altsolidname), "%s_solid", altname);
		solidskytexture = GL_LoadTextureImage (va("textures/%s", altsolidname), altsolidname, 0, 0, 0);
	}
	if (!solidskytexture)
		solidskytexture = GL_LoadTextureImage (va("textures/%s", solidname), solidname, 0, 0, 0);
	if (!solidskytexture)
		return false;

	alphaskytexture = GL_LoadTextureImage (va("textures/%s/%s", mapname, alphaname), alphaname, 0, 0, TEX_ALPHA);
	if (!alphaskytexture && altname) {
		snprintf (altalphaname, sizeof(altalphaname), "%s_alpha", altname);
		alphaskytexture = GL_LoadTextureImage (va("textures/%s", altalphaname), altalphaname, 0, 0, TEX_ALPHA);
	}
	if (!alphaskytexture)
		alphaskytexture = GL_LoadTextureImage (va("textures/%s", alphaname), alphaname, 0, 0, TEX_ALPHA);
	if (!alphaskytexture) {
		// Load a texture consisting of a single transparent pixel
		alphaskytexture = GL_LoadTexture (alphaname, 1, 1, &alphapixel, TEX_ALPHA);
	}
	return true;
}

void R_LoadBrushModelTextures (model_t *m)
{
	int		i;
	texture_t	*tx;
	int			mipcap, base_texmode, texmode;
	qbool		noscale;
	byte		*data;
	int			width, height;

	loadmodel = m;

	for (i = 0; i < loadmodel->numtextures; i++)
	{
		tx = loadmodel->textures[i];
		if (!tx)
			continue;

#ifdef HALFLIFEBSP
		if (loadmodel->halflifebsp) {
			byte *data = WAD3_LoadTexture(tx);
			if (!data) {
				tx->gl_texturenum = GL_LoadTexture ("r_notexture_mip", r_notexture_mip->width, 
							r_notexture_mip->height, (byte *)(r_notexture_mip + 1), TEX_WORLD|TEX_MIPMAP|TEX_BRIGHTEN);
				continue;
			}

			{
				qbool alpha = (tx->name[0] == '{');
				tx->gl_texturenum = GL_LoadTexture32 (tx->name, tx->width, tx->height, data,
					TEX_WORLD|TEX_MIPMAP|TEX_BRIGHTEN | (alpha ? TEX_ALPHA : 0));
			}
			Q_free (data);
			continue;
		}
#endif

		if (loadmodel->isworldmodel && !loadmodel->halflifebsp && !strncmp(tx->name,"sky",3))
		{
			if (!LoadExternalSkyTexture(tx))
				R_InitSky (tx);
			continue;
		}

		if (LoadExternalTexture(tx, TEX_MIPMAP))
			continue;

		if (!tx->offsets[0]) {
			tx->width = r_notexture_mip->width;
			tx->height = r_notexture_mip->height;
			tx->gl_texturenum = GL_LoadTexture ("r_notexture_mip", tx->width, 
							tx->height, (byte *)(r_notexture_mip + 1), TEX_WORLD|TEX_MIPMAP|TEX_BRIGHTEN);
			continue;
		}

		noscale = ((!gl_scaleModelTextures.value && !loadmodel->isworldmodel) ||
				(!gl_scaleTurbTextures.value && (tx->name[0] == '*')));

		mipcap = noscale ? 0 : bound(0, gl_mipTexLevel.value, 3);

		base_texmode = TEX_MIPMAP;
		if (loadmodel->isworldmodel)
			base_texmode |= TEX_WORLD;
		else
			base_texmode |= TEX_MODEL;
		if (noscale)
			base_texmode |= TEX_NOSCALE;

		if (tx->name[0] == '*')
			 // turb textures are drawn without lightmaps, so we don't brighten them
			texmode = base_texmode | TEX_TURB;
		else
			texmode = base_texmode | TEX_BRIGHTEN;

		data = (byte *)tx + tx->offsets[mipcap];
		width = tx->width >> mipcap;
		height = tx->height >> mipcap;

		tx->gl_texturenum = GL_LoadTexture (tx->name, width, height,
														data, texmode);

		if (Img_HasFullbrights((byte *)(tx+1), tx->width*tx->height)) {
			tx->fb_texturenum = GL_LoadTexture (va("@fb_%s", tx->name), width,
					height, (byte *)(tx+1), base_texmode|TEX_FULLBRIGHTMASK);
		}
	}
}

void R_LoadSpriteModelTextures (model_t *m)
{
	// TODO
}

void R_LoadModelTextures (model_t *m)
{
	if (m->type == mod_brush)
		R_LoadBrushModelTextures (m);
	else if (m->type == mod_sprite)
		R_LoadSpriteModelTextures (m);
}


/*
=================
Mod_LoadLighting
=================
*/
qbool r_gpl_map;	// exported to the client
void Mod_LoadLighting (lump_t *l)
{
	char	litname[256];
	int		i, ver;
	int		hunkmark;
	byte	*data;
	byte	*in, *out;

	if (l->filelen <= 0) {
		loadmodel->lightdata = NULL;
		return;
	}

#ifdef HALFLIFEBSP
	if (loadmodel->halflifebsp) {
		loadmodel->lightdata = Hunk_AllocName(l->filelen, loadname);
		memcpy (loadmodel->lightdata, mod_base + l->fileofs, l->filelen);
		return;
	}
#endif

	// LordHavoc's .lit support
	if (!gl_loadlitfiles.value || !gl_colorlights.value)
		goto loadmono;

	strlcpy (litname, loadmodel->name, sizeof(litname));
	COM_StripExtension (litname, litname);
	if (r_gpl_map)
		strlcat (litname, "_gpl.lit", sizeof(litname));
	else
		strlcat (litname, ".lit", sizeof(litname));

	hunkmark = Hunk_LowMark ();
	data = (byte *) FS_LoadHunkFile (litname);
	if (!data)
		goto loadmono;

	if (fs_filesize < 4 || data[0] != 'Q' || data[1] != 'L'
						|| data[2] != 'I' || data[3] != 'T') {
		Com_DPrintf ("Corrupt .lit file (old version?), ignoring\n");
		Hunk_FreeToLowMark (hunkmark);
		goto loadmono;
	}

	if ((ver = LittleLong(*(int *)(data + 4))) != 1) {
		Com_DPrintf ("Unknown .lit file version (%d)\n", ver);
		Hunk_FreeToLowMark (hunkmark);
		goto loadmono;
	}

	if (fs_filesize != l->filelen*3 + 8) {
		Com_DPrintf ("Incorrect .lit file size, ignoring\n");
		Hunk_FreeToLowMark (hunkmark);
		goto loadmono;
	}

	// a valid .lit was successfully loaded
	// clamp brightness to original level. also helps broken lits (e1m1.lit)
	// where brighness is abnormally low in some places
	in = mod_base + l->fileofs;
	out = loadmodel->lightdata = data + 8;
	for (i = l->filelen; i; i--) {
		byte b = max(out[0], max(out[1], out[2]));
		if (!b) {
			out[0] = *in;
			out[1] = *in;
			out[2] = *in;
		} else {
			float scale = ((int)*in << 16) / b;
			out[0] = (int)(out[0] * scale) >> 16;
			out[1] = (int)(out[1] * scale) >> 16;
			out[2] = (int)(out[2] * scale) >> 16;
		}
		out += 3;
		in++;
	}
	return;

loadmono:
	// Expand white lighting data
	loadmodel->lightdata = (byte *) Hunk_AllocName (l->filelen * 3, loadname);	
	in = mod_base + l->fileofs;
	out = loadmodel->lightdata;
	for (i = l->filelen; i; i--) {
		byte b = *in++;
		*out++ = b;
		*out++ = b;
		*out++ = b;
	}
}


/*
=================
Mod_LoadVisibility
=================
*/
void Mod_LoadVisibility (lump_t *l)
{
	if (!l->filelen)
	{
		loadmodel->visdata = NULL;
		return;
	}
	loadmodel->visdata = Hunk_AllocName ( l->filelen, loadname);	
	memcpy (loadmodel->visdata, mod_base + l->fileofs, l->filelen);
}


/*
=================
Mod_LoadVertexes
=================
*/
void Mod_LoadVertexes (lump_t *l)
{
	dvertex_t	*in;
	mvertex_t	*out;
	int			i, count;

	in = (dvertex_t *)(mod_base + l->fileofs);
	if (l->filelen % sizeof(*in))
		Host_Error ("MOD_LoadBmodel: funny lump size in %s",loadmodel->name);
	count = l->filelen / sizeof(*in);
	out = Hunk_AllocName ( count*sizeof(*out), loadname);	

	loadmodel->vertexes = out;
	loadmodel->numvertexes = count;

	for (i = 0; i < count; i++, in++, out++)
	{
		out->position[0] = LittleFloat (in->point[0]);
		out->position[1] = LittleFloat (in->point[1]);
		out->position[2] = LittleFloat (in->point[2]);
	}
}

/*
=================
Mod_LoadSubmodels
=================
*/
void Mod_LoadSubmodels (lump_t *l)
{
	dmodel_t	*in;
	dmodel_t	*out;
	int			i, j, count;

	in = (dmodel_t *)(mod_base + l->fileofs);
	if (l->filelen % sizeof(*in))
		Host_Error ("MOD_LoadBmodel: funny lump size in %s",loadmodel->name);
	count = l->filelen / sizeof(*in);
	out = Hunk_AllocName ( count*sizeof(*out), loadname);	

	loadmodel->submodels = out;
	loadmodel->numsubmodels = count;

	for (i = 0; i < count; i++, in++, out++)
	{
		for (j = 0; j < 3; j++)
		{	// spread the mins / maxs by a pixel
			out->mins[j] = LittleFloat (in->mins[j]) - 1;
			out->maxs[j] = LittleFloat (in->maxs[j]) + 1;
			out->origin[j] = LittleFloat (in->origin[j]);
		}
		for (j = 0; j < MAX_MAP_HULLS; j++)
			out->headnode[j] = LittleLong (in->headnode[j]);
		out->visleafs = LittleLong (in->visleafs);
		out->firstface = LittleLong (in->firstface);
		out->numfaces = LittleLong (in->numfaces);
	}
}

/*
=================
Mod_LoadEdges
=================
*/
void Mod_LoadEdges (lump_t *l)
{
	dedge_t *in;
	medge_t *out;
	int 	i, count;

	in = (dedge_t *)(mod_base + l->fileofs);
	if (l->filelen % sizeof(*in))
		Host_Error ("MOD_LoadBmodel: funny lump size in %s",loadmodel->name);
	count = l->filelen / sizeof(*in);
	out = Hunk_AllocName ( (count + 1) * sizeof(*out), loadname);	

	loadmodel->edges = out;
	loadmodel->numedges = count;

	for (i = 0; i < count; i++, in++, out++)
	{
		out->v[0] = (unsigned short)LittleShort(in->v[0]);
		out->v[1] = (unsigned short)LittleShort(in->v[1]);
	}
}

/*
=================
Mod_LoadTexinfo
=================
*/
void Mod_LoadTexinfo (lump_t *l)
{
	texinfo_t *in;
	mtexinfo_t *out;
	int 	i, j, count;
	int		miptex;

	in = (texinfo_t *)(mod_base + l->fileofs);
	if (l->filelen % sizeof(*in))
		Host_Error ("MOD_LoadBmodel: funny lump size in %s",loadmodel->name);
	count = l->filelen / sizeof(*in);
	out = Hunk_AllocName ( count*sizeof(*out), loadname);	

	loadmodel->texinfo = out;
	loadmodel->numtexinfo = count;

	for (i = 0; i < count; i++, in++, out++)
	{
		for (j = 0; j < 8; j++)
			out->vecs[0][j] = LittleFloat (in->vecs[0][j]);

		miptex = LittleLong (in->miptex);
		out->flags = LittleLong (in->flags);
	
		if (!loadmodel->textures)
		{
			out->texture = r_notexture_mip;	// checkerboard texture
			out->flags = 0;
		}
		else
		{
			if (miptex >= loadmodel->numtextures)
				Host_Error ("miptex >= loadmodel->numtextures");
			out->texture = loadmodel->textures[miptex];
			if (!out->texture)
			{
				out->texture = r_notexture_mip; // texture not found
				out->flags = 0;
			}
		}
	}
}

/*
================
CalcSurfaceExtents

Fills in s->texturemins[] and s->extents[]
================
*/
void CalcSurfaceExtents (msurface_t *s)
{
	float	mins[2], maxs[2], val;
	int		i,j, e;
	mvertex_t	*v;
	mtexinfo_t	*tex;
	int		bmins[2], bmaxs[2];

	mins[0] = mins[1] = 999999;
	maxs[0] = maxs[1] = -99999;

	tex = s->texinfo;
	
	for (i = 0; i < s->numedges; i++)
	{
		e = loadmodel->surfedges[s->firstedge+i];
		if (e >= 0)
			v = &loadmodel->vertexes[loadmodel->edges[e].v[0]];
		else
			v = &loadmodel->vertexes[loadmodel->edges[-e].v[1]];
		
		for (j = 0; j < 2; j++)
		{
			val = v->position[0] * tex->vecs[j][0] + 
				v->position[1] * tex->vecs[j][1] +
				v->position[2] * tex->vecs[j][2] +
				tex->vecs[j][3];
			if (val < mins[j])
				mins[j] = val;
			if (val > maxs[j])
				maxs[j] = val;
		}
	}

	for (i = 0; i < 2; i++)
	{	
		bmins[i] = floor(mins[i]/16);
		bmaxs[i] = ceil(maxs[i]/16);

		s->texturemins[i] = bmins[i] * 16;
		s->extents[i] = (bmaxs[i] - bmins[i]) * 16;
		if ( !(tex->flags & TEX_SPECIAL) && s->extents[i] > 512 /* 256 */ )
			Host_Error ("Bad surface extents");
	}
}


/*
=================
Mod_LoadFaces
=================
*/
void Mod_LoadFaces (lump_t *l)
{
	dface_t		*in;
	msurface_t 	*out;
	int			i, count, surfnum;
	int			planenum, side;
	char		turbchar = loadmodel->halflifebsp ? '!' : '*';

	in = (dface_t *)(mod_base + l->fileofs);
	if (l->filelen % sizeof(*in))
		Host_Error ("MOD_LoadBmodel: funny lump size in %s",loadmodel->name);
	count = l->filelen / sizeof(*in);
	out = Hunk_AllocName ( count*sizeof(*out), loadname);	

	loadmodel->surfaces = out;
	loadmodel->numsurfaces = count;

	for (surfnum = 0; surfnum < count; surfnum++, in++, out++)
	{
		out->firstedge = LittleLong(in->firstedge);
		out->numedges = LittleShort(in->numedges);		
		out->flags = 0;

		planenum = LittleShort(in->planenum);
		side = LittleShort(in->side);
		if (side)
			out->flags |= SURF_PLANEBACK;			

		out->plane = loadmodel->planes + planenum;

		out->texinfo = loadmodel->texinfo + LittleShort (in->texinfo);

		CalcSurfaceExtents (out);
				
	// lighting info

		for (i = 0; i < MAXLIGHTMAPS; i++)
			out->styles[i] = in->styles[i];
		i = LittleLong(in->lightofs);
		if (i == -1)
			out->samples = NULL;
		else
			out->samples = loadmodel->lightdata + (loadmodel->halflifebsp ? i : i * 3);
		
	// set the drawing flags flag

		if (!strncmp(out->texinfo->texture->name,"sky", 3))	// sky
		{
			out->flags |= (SURF_DRAWSKY | SURF_UNLIT);
			GL_BuildSkySurfacePolys (out);	// build gl polys
			continue;
		}

		if (out->texinfo->texture->name[0] == turbchar)		// turbulent
		{
			out->flags |= (SURF_DRAWTURB | SURF_UNLIT);
			GL_SubdivideSurface (out);	// cut up polygon for warps
			continue;
		}

	}
}


/*
=================
Mod_SetParent
=================
*/
void Mod_SetParent (mnode_t *node, mnode_t *parent)
{
	node->parent = parent;
	if (node->contents < 0)
		return;
	Mod_SetParent (node->children[0], node);
	Mod_SetParent (node->children[1], node);
}

/*
=================
Mod_LoadNodes
=================
*/
void Mod_LoadNodes (lump_t *l)
{
	int			i, j, count, p;
	dnode_t		*in;
	mnode_t 	*out;

	in = (dnode_t *)(mod_base + l->fileofs);
	if (l->filelen % sizeof(*in))
		Host_Error ("MOD_LoadBmodel: funny lump size in %s",loadmodel->name);
	count = l->filelen / sizeof(*in);
	out = Hunk_AllocName ( count*sizeof(*out), loadname);	

	loadmodel->nodes = out;
	loadmodel->numnodes = count;

	for (i = 0; i < count; i++, in++, out++)
	{
		for (j = 0; j < 3; j++)
		{
			out->minmaxs[j] = LittleShort (in->mins[j]);
			out->minmaxs[3+j] = LittleShort (in->maxs[j]);
		}
	
		p = LittleLong(in->planenum);
		out->plane = loadmodel->planes + p;

		out->firstsurface = LittleShort (in->firstface);
		out->numsurfaces = LittleShort (in->numfaces);
		
		for (j = 0; j < 2; j++)
		{
			p = LittleShort (in->children[j]);
			if (p >= 0)
				out->children[j] = loadmodel->nodes + p;
			else
				out->children[j] = (mnode_t *)(loadmodel->leafs + (-1 - p));
		}
	}
	
	Mod_SetParent (loadmodel->nodes, NULL);	// sets nodes and leafs
}

/*
=================
Mod_LoadLeafs
=================
*/
void Mod_LoadLeafs (lump_t *l)
{
	dleaf_t 	*in;
	mleaf_t 	*out;
	int			i, j, count, p;

	in = (dleaf_t *)(mod_base + l->fileofs);
	if (l->filelen % sizeof(*in))
		Host_Error ("MOD_LoadBmodel: funny lump size in %s",loadmodel->name);
	count = l->filelen / sizeof(*in);
	out = Hunk_AllocName ( count*sizeof(*out), loadname);	

	loadmodel->leafs = out;
	loadmodel->numleafs = count;
	for (i = 0; i < count; i++, in++, out++)
	{
		for (j = 0; j < 3; j++)
		{
			out->minmaxs[j] = LittleShort (in->mins[j]);
			out->minmaxs[3+j] = LittleShort (in->maxs[j]);
		}

		p = LittleLong(in->contents);
		out->contents = p;

		out->firstmarksurface = loadmodel->marksurfaces +
			LittleShort(in->firstmarksurface);
		out->nummarksurfaces = LittleShort(in->nummarksurfaces);
		
		p = LittleLong(in->visofs);
		if (p == -1)
			out->compressed_vis = NULL;
		else
			out->compressed_vis = loadmodel->visdata + p;
		out->efrags = NULL;
	}	
}

/*
=================
Mod_LoadMarksurfaces
=================
*/
void Mod_LoadMarksurfaces (lump_t *l)
{	
	int		i, j, count;
	short		*in;
	msurface_t **out;

	in = (short *)(mod_base + l->fileofs);
	if (l->filelen % sizeof(*in))
		Host_Error ("MOD_LoadBmodel: funny lump size in %s",loadmodel->name);
	count = l->filelen / sizeof(*in);
	out = Hunk_AllocName ( count*sizeof(*out), loadname);	

	loadmodel->marksurfaces = out;
	loadmodel->nummarksurfaces = count;

	for (i = 0; i < count; i++)
	{
		j = LittleShort(in[i]);
		if (j >= loadmodel->numsurfaces)
			Host_Error ("Mod_LoadMarksurfaces: bad surface number");
		out[i] = loadmodel->surfaces + j;
	}
}

/*
=================
Mod_LoadSurfedges
=================
*/
void Mod_LoadSurfedges (lump_t *l)
{	
	int		i, count;
	int		*in, *out;
	
	in = (int *)(mod_base + l->fileofs);
	if (l->filelen % sizeof(*in))
		Host_Error ("MOD_LoadBmodel: funny lump size in %s",loadmodel->name);
	count = l->filelen / sizeof(*in);
	out = Hunk_AllocName ( count*sizeof(*out), loadname);	

	loadmodel->surfedges = out;
	loadmodel->numsurfedges = count;

	for (i = 0; i < count; i++)
		out[i] = LittleLong (in[i]);
}


/*
=================
Mod_LoadPlanes
=================
*/
void Mod_LoadPlanes (lump_t *l)
{
	int			i, j;
	mplane_t	*out;
	dplane_t 	*in;
	int			count;
	int			bits;
	
	in = (dplane_t *)(mod_base + l->fileofs);
	if (l->filelen % sizeof(*in))
		Host_Error ("MOD_LoadBmodel: funny lump size in %s",loadmodel->name);
	count = l->filelen / sizeof(*in);
	out = Hunk_AllocName ( count*sizeof(*out), loadname);	
	
	loadmodel->planes = out;
	loadmodel->numplanes = count;

	for (i = 0; i < count; i++, in++, out++)
	{
		bits = 0;
		for (j = 0; j < 3; j++)
		{
			out->normal[j] = LittleFloat (in->normal[j]);
			if (out->normal[j] < 0)
				bits |= 1<<j;
		}

		out->dist = LittleFloat (in->dist);
		out->type = LittleLong (in->type);
		out->signbits = bits;
	}
}

/*
=================
RadiusFromBounds
=================
*/
float RadiusFromBounds (vec3_t mins, vec3_t maxs)
{
	int		i;
	vec3_t	corner;

	for (i = 0; i < 3; i++)
	{
		corner[i] = fabs(mins[i]) > fabs(maxs[i]) ? fabs(mins[i]) : fabs(maxs[i]);
	}

	return VectorLength (corner);
}

#ifdef HALFLIFEBSP
static void Mod_ParseWadsFromEntityLump(lump_t *l)
{
	char *data;
	char *s, key[1024], value[1024];	
	int i, j, k;

	if (!l->filelen)
		return;

	data = (char *)(mod_base + l->fileofs);
	data = COM_Parse(data);
	if (!data)
		return;

	if (com_token[0] != '{')
		return; // error

	while (1) {
		if (!(data = COM_Parse(data)))
			return; // error

		if (com_token[0] == '}')
			break; // end of worldspawn

		strlcpy (key, (com_token[0] == '_') ? com_token + 1 : com_token, sizeof(key));

		for (s = key + strlen(key) - 1; s >= key && *s == ' '; s--)		// remove trailing spaces
			*s = 0;

		if (!(data = COM_Parse(data)))
			return; // error

		strlcpy (value, com_token, sizeof(value));

//let the server decide
//		if (!strcmp("sky", key) || !strcmp("skyname", key))
//			R_SetSky (value);

		if (!strcmp("wad", key)) {
			j = 0;
			for (i = 0; i < strlen(value); i++) {
				if (value[i] != ';' && value[i] != '\\' && value[i] != '/' && value[i] != ':')
					break;
			}
			if (!value[i])
				continue;
			for ( ; i < sizeof(value); i++) {
				// skip path
				if (value[i] == '\\' || value[i] == '/' || value[i] == ':') {
					j = i + 1;
				} else if (value[i] == ';' || value[i] == 0) {
					k = value[i];
					value[i] = 0;
					if (value[j])
						WAD3_LoadWadFile (value + j);
					j = i + 1;
					if (!k)
						break;
				}
			}
		}
	}
}
#endif /* HALFLIFEBSP */


/*
=================
Mod_LoadBrushModel
=================
*/
void Mod_LoadBrushModel (model_t *mod, void *buffer, qbool worldmodel)
{
	int			i;
	dheader_t	*header;
	dmodel_t 	*bm;
	
	loadmodel->type = mod_brush;
	
	header = (dheader_t *)buffer;

	i = LittleLong (header->version);
#ifdef HALFLIFEBSP
	if (i != BSPVERSION && i != HL_BSPVERSION)
#else
	if (i != BSPVERSION)
#endif
		Host_Error ("Mod_LoadBrushModel: %s has wrong version number (%i should be %i)", mod->name, i, BSPVERSION);

	loadmodel->halflifebsp = (i == HL_BSPVERSION);
	loadmodel->isworldmodel = worldmodel;

// swap all the lumps
	mod_base = (byte *)header;

	for (i = 0; i < sizeof(dheader_t)/4; i++)
		((int *)header)[i] = LittleLong (((int *)header)[i]);


// load into heap

	Mod_LoadVertexes (&header->lumps[LUMP_VERTEXES]);
	Mod_LoadEdges (&header->lumps[LUMP_EDGES]);
	Mod_LoadSurfedges (&header->lumps[LUMP_SURFEDGES]);
#ifdef HALFLIFEBSP
	if (loadmodel->halflifebsp)
		Mod_ParseWadsFromEntityLump (&header->lumps[LUMP_ENTITIES]);
#endif
	Mod_LoadTextures (&header->lumps[LUMP_TEXTURES]);
	Mod_LoadLighting (&header->lumps[LUMP_LIGHTING]);
	Mod_LoadPlanes (&header->lumps[LUMP_PLANES]);
	Mod_LoadTexinfo (&header->lumps[LUMP_TEXINFO]);
	Mod_LoadFaces (&header->lumps[LUMP_FACES]);
	Mod_LoadMarksurfaces (&header->lumps[LUMP_MARKSURFACES]);
	Mod_LoadVisibility (&header->lumps[LUMP_VISIBILITY]);
	Mod_LoadLeafs (&header->lumps[LUMP_LEAFS]);
	Mod_LoadNodes (&header->lumps[LUMP_NODES]);
	Mod_LoadSubmodels (&header->lumps[LUMP_MODELS]);

	mod->numframes = 2;		// regular and alternate animation

//
// set up the submodels (FIXME: this is confusing)
//
	for (i = 0; i < mod->numsubmodels; i++)
	{
		bm = &mod->submodels[i];

		mod->firstmodelsurface = bm->firstface;
		mod->nummodelsurfaces = bm->numfaces;
		
		mod->firstnode = bm->headnode[0];
		if ((unsigned)mod->firstnode > loadmodel->numnodes)
			Host_Error ("Inline model %i has bad firstnode", i);

		VectorCopy (bm->maxs, mod->maxs);
		VectorCopy (bm->mins, mod->mins);

		mod->radius = RadiusFromBounds (mod->mins, mod->maxs);

		mod->numleafs = bm->visleafs;

		if (i < mod->numsubmodels-1)
		{
			// duplicate the basic information
			char	name[10];

			sprintf (name, "*%i", i+1);
			loadmodel = Mod_FindName (name);
			*loadmodel = *mod;
			strcpy (loadmodel->name, name);
			mod = loadmodel;
		}
	}
}

/*
==============================================================================

ALIAS MODELS

==============================================================================
*/

aliashdr_t	*pheader;

stvert_t	stverts[MAXALIASVERTS];
mtriangle_t	triangles[MAXALIASTRIS];

// a pose is a single set of vertexes.  a frame may be
// an animating sequence of poses
trivertx_t	*poseverts[MAXALIASFRAMES];
int			posenum;

byte		player_8bit_texels[320*200];

byte		aliasbboxmins[3], aliasbboxmaxs[3];

/*
=================
Mod_LoadAliasFrame
=================
*/
void *Mod_LoadAliasFrame (void * pin, maliasframedesc_t *frame)
{
	trivertx_t		*pinframe;
	int				i;
	daliasframe_t	*pdaliasframe;
	
	pdaliasframe = (daliasframe_t *)pin;

	strcpy (frame->name, pdaliasframe->name);
	frame->firstpose = posenum;
	frame->numposes = 1;

	for (i = 0; i < 3; i++)
	{
	// these are byte values, so we don't have to worry about
	// endianness
		frame->bboxmin.v[i] = pdaliasframe->bboxmin.v[i];
		frame->bboxmax.v[i] = pdaliasframe->bboxmax.v[i];

		aliasbboxmins[i] = min (aliasbboxmins[i], frame->bboxmin.v[i]);
		aliasbboxmaxs[i] = max (aliasbboxmaxs[i], frame->bboxmax.v[i]);
	}

	pinframe = (trivertx_t *)(pdaliasframe + 1);

	poseverts[posenum] = pinframe;
	posenum++;

	pinframe += pheader->numverts;

	return (void *)pinframe;
}


/*
=================
Mod_LoadAliasGroup
=================
*/
void *Mod_LoadAliasGroup (void * pin,  maliasframedesc_t *frame)
{
	daliasgroup_t		*pingroup;
	int					i, numframes;
	daliasinterval_t	*pin_intervals;
	void				*ptemp;
	
	pingroup = (daliasgroup_t *)pin;

	numframes = LittleLong (pingroup->numframes);

	frame->firstpose = posenum;
	frame->numposes = numframes;

	for (i = 0; i < 3; i++)
	{
	// these are byte values, so we don't have to worry about endianness
		frame->bboxmin.v[i] = pingroup->bboxmin.v[i];
		frame->bboxmax.v[i] = pingroup->bboxmax.v[i];

		aliasbboxmins[i] = min (aliasbboxmins[i], frame->bboxmin.v[i]);
		aliasbboxmaxs[i] = max (aliasbboxmaxs[i], frame->bboxmax.v[i]);
	}

	pin_intervals = (daliasinterval_t *)(pingroup + 1);

	frame->interval = LittleFloat (pin_intervals->interval);

	pin_intervals += numframes;

	ptemp = (daliasinterval_t *)pin_intervals;

	for (i = 0; i < numframes; i++)
	{
		poseverts[posenum] = (trivertx_t *)((daliasframe_t *)ptemp + 1);
		posenum++;

		ptemp = (trivertx_t *)((daliasframe_t *)ptemp + 1) + pheader->numverts;
	}

	return ptemp;
}

//=========================================================

/*
=================
Mod_FloodFillSkin

Fill background pixels so mipmapping doesn't have haloes - Ed
=================
*/

typedef struct
{
	short		x, y;
} floodfill_t;

extern unsigned d_8to24table[];

// must be a power of 2
#define FLOODFILL_FIFO_SIZE 0x1000
#define FLOODFILL_FIFO_MASK (FLOODFILL_FIFO_SIZE - 1)

#define FLOODFILL_STEP( off, dx, dy ) \
{ \
	if (pos[off] == fillcolor) \
	{ \
		pos[off] = 255; \
		fifo[inpt].x = x + (dx), fifo[inpt].y = y + (dy); \
		inpt = (inpt + 1) & FLOODFILL_FIFO_MASK; \
	} \
	else if (pos[off] != 255) fdc = pos[off]; \
}

void Mod_FloodFillSkin( byte *skin, int skinwidth, int skinheight )
{
	byte				fillcolor = *skin; // assume this is the pixel to fill
	floodfill_t			fifo[FLOODFILL_FIFO_SIZE];
	int					inpt = 0, outpt = 0;
	int					filledcolor = -1;
	int					i;

	if (filledcolor == -1)
	{
		filledcolor = 0;
		// attempt to find opaque black
		for (i = 0; i < 256; ++i)
			if (d_8to24table[i] == (255 << 0)) // alpha 1.0
			{
				filledcolor = i;
				break;
			}
	}

	// can't fill to filled color or to transparent color (used as visited marker)
	if ((fillcolor == filledcolor) || (fillcolor == 255))
	{
		//printf( "not filling skin from %d to %d\n", fillcolor, filledcolor );
		return;
	}

	fifo[inpt].x = 0, fifo[inpt].y = 0;
	inpt = (inpt + 1) & FLOODFILL_FIFO_MASK;

	while (outpt != inpt)
	{
		int			x = fifo[outpt].x, y = fifo[outpt].y;
		int			fdc = filledcolor;
		byte		*pos = &skin[x + skinwidth * y];

		outpt = (outpt + 1) & FLOODFILL_FIFO_MASK;

		if (x > 0)				FLOODFILL_STEP( -1, -1, 0 );
		if (x < skinwidth - 1)	FLOODFILL_STEP( 1, 1, 0 );
		if (y > 0)				FLOODFILL_STEP( -skinwidth, 0, -1 );
		if (y < skinheight - 1)	FLOODFILL_STEP( skinwidth, 0, 1 );
		skin[x + skinwidth * y] = fdc;
	}
}

/*
===============
Mod_LoadAllSkins
===============
*/
void *Mod_LoadAllSkins (int numskins, daliasskintype_t *pskintype)
{
	int		i, j, k;
	char	name[32];
	int		s;
	byte	*skin;
	daliasskingroup_t		*pinskingroup;
	int		groupskins;
	daliasskininterval_t	*pinskinintervals;
	int		noscale_flag = gl_scaleModelTextures.value ? 0 : TEX_NOSCALE;
	
	skin = (byte *)(pskintype + 1);

	if (numskins < 1 || numskins > MAX_SKINS)
		Host_Error ("Mod_LoadAliasModel: Invalid # of skins: %d\n", numskins);

	s = pheader->skinwidth * pheader->skinheight;

	for (i = 0; i < numskins; i++)
	{
		if (pskintype->type == ALIAS_SKIN_SINGLE) {
			Mod_FloodFillSkin (skin, pheader->skinwidth, pheader->skinheight);

			// save 8 bit texels for the player model to remap
			if (loadmodel->modhint == MOD_PLAYER)
			{
				if (s > sizeof(player_8bit_texels))
					Host_Error ("Player skin too large");
				memcpy (player_8bit_texels, (byte *)(pskintype + 1), s);
			}
			snprintf (name, sizeof(name), "%s_%i", loadmodel->name, i);
			pheader->gl_texturenum[i][0] =
			pheader->gl_texturenum[i][1] =
			pheader->gl_texturenum[i][2] =
			pheader->gl_texturenum[i][3] =
				GL_LoadTexture (name, pheader->skinwidth, pheader->skinheight,
				(byte *)(pskintype + 1), TEX_MODEL|TEX_MIPMAP|noscale_flag);

			if (Img_HasFullbrights((byte *)(pskintype + 1),	pheader->skinwidth*pheader->skinheight))
				pheader->fb_texturenum[i][0] = pheader->fb_texturenum[i][1] =
				pheader->fb_texturenum[i][2] = pheader->fb_texturenum[i][3] =
					GL_LoadTexture (va("@fb_%s", name), pheader->skinwidth, 
					pheader->skinheight, (byte *)(pskintype + 1), TEX_MODEL|TEX_MIPMAP|TEX_FULLBRIGHTMASK|noscale_flag);
			else
				pheader->fb_texturenum[i][0] = pheader->fb_texturenum[i][1] =
				pheader->fb_texturenum[i][2] = pheader->fb_texturenum[i][3] = 0;
			
			pskintype = (daliasskintype_t *)((byte *)(pskintype+1) + s);
		} else {
			// animating skin group.  yuck.
			pskintype++;
			pinskingroup = (daliasskingroup_t *)pskintype;
			groupskins = LittleLong (pinskingroup->numskins);
			pinskinintervals = (daliasskininterval_t *)(pinskingroup + 1);

			pskintype = (daliasskintype_t *)(pinskinintervals + groupskins);

			for (j = 0; j < groupskins; j++)
			{
					Mod_FloodFillSkin (skin, pheader->skinwidth, pheader->skinheight);
					snprintf (name, sizeof(name), "%s_%i_%i", loadmodel->name, i, j);
					pheader->gl_texturenum[i][j&3] = 
						GL_LoadTexture (name, pheader->skinwidth, 
						pheader->skinheight, (byte *)(pskintype), TEX_MODEL|TEX_MIPMAP|noscale_flag);

					if (Img_HasFullbrights((byte *)(pskintype),	pheader->skinwidth*pheader->skinheight))
						pheader->fb_texturenum[i][j&3] =
							GL_LoadTexture (va("@fb_%s", name), pheader->skinwidth, 
							pheader->skinheight, (byte *)(pskintype), TEX_MODEL|TEX_MIPMAP|TEX_FULLBRIGHTMASK|noscale_flag);
					else
						pheader->fb_texturenum[i][j&3] = 0;

					pskintype = (daliasskintype_t *)((byte *)(pskintype) + s);
			}
			k = j;
			for (/* */; j < 4; j++)
				pheader->gl_texturenum[i][j&3] = 
				pheader->gl_texturenum[i][j - k]; 
		}
	}

	return (void *)pskintype;
}


//=========================================================================

/*
=================
Mod_LoadAliasModel
=================
*/
void Mod_LoadAliasModel (model_t *mod, void *buffer)
{
	int					i, j;
	mdl_t				*pinmodel;
	stvert_t			*pinstverts;
	dtriangle_t			*pintriangles;
	int					version, numframes;
	int					size;
	daliasframetype_t	*pframetype;
	daliasskintype_t	*pskintype;
	int					start, end, total;

// some models are special
	if(!strcmp(mod->name, "progs/player.mdl"))
		mod->modhint = MOD_PLAYER;
	else if(!strcmp(mod->name, "progs/eyes.mdl"))
		mod->modhint = MOD_EYES;
	else if (!strcmp(mod->name, "progs/flame.mdl") ||
		!strcmp(mod->name, "progs/flame2.mdl"))
		mod->modhint = MOD_FLAME;
	else if (!strcmp(mod->name, "progs/bolt2.mdl"))
		mod->modhint = MOD_THUNDERBOLT2;
	else if (!strcmp(mod->name, "progs/bolt.mdl") ||
		!strcmp(mod->name, "progs/bolt3.mdl"))
		mod->modhint = MOD_THUNDERBOLT;
	else
		mod->modhint = MOD_NORMAL;

	if (mod->modhint == MOD_PLAYER || mod->modhint == MOD_EYES)
		mod->crc = CRC_Block (buffer, fs_filesize);
	
	start = Hunk_LowMark ();

	pinmodel = (mdl_t *)buffer;

	version = LittleLong (pinmodel->version);

	if (version != ALIAS_VERSION) {
		Hunk_FreeToLowMark (start);

		Host_Error ("%s has wrong version number (%i should be %i)\n",
				 mod->name, version, ALIAS_VERSION);

		return;
	}

//
// allocate space for a working header, plus all the data except the frames,
// skin and group info
//
	size = 	sizeof (aliashdr_t) 
			+ (LittleLong (pinmodel->numframes) - 1) *
			sizeof (pheader->frames[0]);
	pheader = Hunk_AllocName (size, loadname);
	
	mod->flags = LittleLong (pinmodel->flags);

//
// endian-adjust and copy the data, starting with the alias model header
//
	pheader->boundingradius = LittleFloat (pinmodel->boundingradius);
	pheader->numskins = LittleLong (pinmodel->numskins);
	pheader->skinwidth = LittleLong (pinmodel->skinwidth);
	pheader->skinheight = LittleLong (pinmodel->skinheight);

	if (pheader->skinheight > MAX_LBM_HEIGHT)
		Host_Error ("model %s has a skin taller than %d", mod->name,
				   MAX_LBM_HEIGHT);

	pheader->numverts = LittleLong (pinmodel->numverts);

	if (pheader->numverts <= 0)
		Host_Error ("model %s has no vertices", mod->name);

	if (pheader->numverts > MAXALIASVERTS)
		Host_Error ("model %s has too many vertices", mod->name);

	pheader->numtris = LittleLong (pinmodel->numtris);

	if (pheader->numtris <= 0)
		Host_Error ("model %s has no triangles", mod->name);

	pheader->numframes = LittleLong (pinmodel->numframes);
	numframes = pheader->numframes;
	if (numframes < 1)
		Host_Error ("Mod_LoadAliasModel: Invalid # of frames: %d\n", numframes);

	pheader->size = LittleFloat (pinmodel->size) * ALIAS_BASE_SIZE_RATIO;
	mod->synctype = LittleLong (pinmodel->synctype);
	mod->numframes = pheader->numframes;

	for (i = 0; i < 3; i++)
	{
		pheader->scale[i] = LittleFloat (pinmodel->scale[i]);
		pheader->scale_origin[i] = LittleFloat (pinmodel->scale_origin[i]);
		pheader->eyeposition[i] = LittleFloat (pinmodel->eyeposition[i]);
	}


//
// load the skins
//
	pskintype = (daliasskintype_t *)&pinmodel[1];
	pskintype = Mod_LoadAllSkins (pheader->numskins, pskintype);

//
// load base s and t vertices
//
	pinstverts = (stvert_t *)pskintype;

	for (i = 0; i < pheader->numverts; i++)
	{
		stverts[i].onseam = LittleLong (pinstverts[i].onseam);
		stverts[i].s = LittleLong (pinstverts[i].s);
		stverts[i].t = LittleLong (pinstverts[i].t);
	}

//
// load triangle lists
//
	pintriangles = (dtriangle_t *)&pinstverts[pheader->numverts];

	for (i = 0; i < pheader->numtris; i++)
	{
		triangles[i].facesfront = LittleLong (pintriangles[i].facesfront);

		for (j = 0; j < 3; j++)
		{
			triangles[i].vertindex[j] =
					LittleLong (pintriangles[i].vertindex[j]);
		}
	}

//
// load the frames
//
	posenum = 0;
	pframetype = (daliasframetype_t *)&pintriangles[pheader->numtris];

	aliasbboxmins[0] = aliasbboxmins[1] = aliasbboxmins[2] = 255;
	aliasbboxmaxs[0] = aliasbboxmaxs[1] = aliasbboxmaxs[2] = 0;

	for (i = 0; i < numframes; i++)
	{
		aliasframetype_t	frametype;

		frametype = LittleLong (pframetype->type);

		if (frametype == ALIAS_SINGLE)
		{
			pframetype = (daliasframetype_t *)
					Mod_LoadAliasFrame (pframetype + 1, &pheader->frames[i]);
		}
		else
		{
			pframetype = (daliasframetype_t *)
					Mod_LoadAliasGroup (pframetype + 1, &pheader->frames[i]);
		}
	}

	pheader->numposes = posenum;

	mod->type = mod_alias;

	for (i = 0; i < 3; i++)
	{
		mod->mins[i] = aliasbboxmins[i] * pheader->scale[i] + pheader->scale_origin[i];
		mod->maxs[i] = aliasbboxmaxs[i] * pheader->scale[i] + pheader->scale_origin[i];
	}

	mod->radius = RadiusFromBounds (mod->mins, mod->maxs);

	//
	// build the draw lists
	//
	GL_MakeAliasModelDisplayLists (mod, pheader);

//
// move the complete, relocatable alias model to the cache
//	
	end = Hunk_LowMark ();
	total = end - start;
	
	Cache_Alloc (&mod->cache, total, loadname);
	if (!mod->cache.data)
		return;
	memcpy (mod->cache.data, pheader, total);

	Hunk_FreeToLowMark (start);
}

//=============================================================================

/*
=================
Mod_LoadSpriteFrame
=================
*/
void *Mod_LoadSpriteFrame (void * pin, mspriteframe_t **ppframe, int framenum)
{
	dspriteframe_t		*pinframe;
	mspriteframe_t		*pspriteframe;
	int					width, height, size, origin[2];
	char				name[64];
	int					texmode;

	pinframe = (dspriteframe_t *)pin;

	width = LittleLong (pinframe->width);
	height = LittleLong (pinframe->height);
	size = width * height;

	pspriteframe = Hunk_AllocName (sizeof (mspriteframe_t),loadname);

	memset (pspriteframe, 0, sizeof (mspriteframe_t));

	*ppframe = pspriteframe;

	pspriteframe->width = width;
	pspriteframe->height = height;
	origin[0] = LittleLong (pinframe->origin[0]);
	origin[1] = LittleLong (pinframe->origin[1]);

	pspriteframe->up = origin[1];
	pspriteframe->down = origin[1] - height;
	pspriteframe->left = origin[0];
	pspriteframe->right = width + origin[0];

	texmode = TEX_SPRITE|TEX_MIPMAP|TEX_ALPHA;
	if (!gl_scaleModelTextures.value)
		texmode |= TEX_NOSCALE;
	sprintf (name, "%s_%i", loadmodel->name, framenum);
	pspriteframe->gl_texturenum = GL_LoadTexture (name, width, height, (byte *)(pinframe + 1), texmode);

	return (void *)((byte *)pinframe + sizeof (dspriteframe_t) + size);
}


/*
=================
Mod_LoadSpriteGroup
=================
*/
void *Mod_LoadSpriteGroup (void * pin, mspriteframe_t **ppframe, int framenum)
{
	dspritegroup_t		*pingroup;
	mspritegroup_t		*pspritegroup;
	int					i, numframes;
	dspriteinterval_t	*pin_intervals;
	float				*poutintervals;
	void				*ptemp;

	pingroup = (dspritegroup_t *)pin;

	numframes = LittleLong (pingroup->numframes);

	pspritegroup = Hunk_AllocName (sizeof (mspritegroup_t) +
				(numframes - 1) * sizeof (pspritegroup->frames[0]), loadname);

	pspritegroup->numframes = numframes;

	*ppframe = (mspriteframe_t *)pspritegroup;

	pin_intervals = (dspriteinterval_t *)(pingroup + 1);

	poutintervals = Hunk_AllocName (numframes * sizeof (float), loadname);

	pspritegroup->intervals = poutintervals;

	for (i = 0; i < numframes; i++)
	{
		*poutintervals = LittleFloat (pin_intervals->interval);
		if (*poutintervals <= 0.0)
			Host_Error ("Mod_LoadSpriteGroup: interval<=0");

		poutintervals++;
		pin_intervals++;
	}

	ptemp = (dspriteinterval_t *)pin_intervals;

	for (i = 0; i < numframes; i++)
	{
		ptemp = Mod_LoadSpriteFrame (ptemp, &pspritegroup->frames[i], framenum * 100 + i);
	}

	return ptemp;
}


/*
=================
Mod_LoadSpriteModel
=================
*/
void Mod_LoadSpriteModel (model_t *mod, void *buffer)
{
	int					i;
	int					version;
	dsprite_t			*pin;
	msprite_t			*psprite;
	int					numframes;
	int					size;
	dspriteframetype_t	*pframetype;
	
	pin = (dsprite_t *)buffer;

	version = LittleLong (pin->version);

	if (version != SPRITE_VERSION) {
		Host_Error ("%s has wrong version number "
				 "(%i should be %i)", mod->name, version, SPRITE_VERSION);
		return;
	}

	numframes = LittleLong (pin->numframes);

	size = sizeof (msprite_t) +	(numframes - 1) * sizeof (psprite->frames);

	psprite = Hunk_AllocName (size, loadname);

	mod->cache.data = psprite;

	psprite->type = LittleLong (pin->type);
	psprite->maxwidth = LittleLong (pin->width);
	psprite->maxheight = LittleLong (pin->height);
	psprite->beamlength = LittleFloat (pin->beamlength);
	mod->synctype = LittleLong (pin->synctype);
	psprite->numframes = numframes;

	mod->mins[0] = mod->mins[1] = -psprite->maxwidth/2;
	mod->maxs[0] = mod->maxs[1] = psprite->maxwidth/2;
	mod->mins[2] = -psprite->maxheight/2;
	mod->maxs[2] = psprite->maxheight/2;

//
// load the frames
//
	if (numframes < 1)
		Host_Error ("Mod_LoadSpriteModel: Invalid # of frames: %d\n", numframes);

	mod->numframes = numframes;

	pframetype = (dspriteframetype_t *)(pin + 1);

	for (i = 0; i < numframes; i++)
	{
		spriteframetype_t	frametype;

		frametype = LittleLong (pframetype->type);
		psprite->frames[i].type = frametype;

		if (frametype == SPR_SINGLE)
		{
			pframetype = (dspriteframetype_t *)
					Mod_LoadSpriteFrame (pframetype + 1,
										 &psprite->frames[i].frameptr, i);
		}
		else
		{
			pframetype = (dspriteframetype_t *)
					Mod_LoadSpriteGroup (pframetype + 1,
										 &psprite->frames[i].frameptr, i);
		}
	}

	mod->type = mod_sprite;
}

//=============================================================================

/*
================
Mod_Print
================
*/
void Mod_Print (void)
{
	int		i;
	model_t	*mod;

	Com_Printf ("Cached models:\n");
	for (i = 0, mod = mod_known; i < mod_numknown; i++, mod++)
	{
		Com_Printf ("%8p : %s\n",mod->cache.data, mod->name);
	}
}


int R_ModelFlags (const struct model_s *model)
{
	return model->flags;
}

unsigned short R_ModelChecksum (const struct model_s *model)
{
	return model->crc;
}

