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
// gl_texture.c - GL texture management

#include "gl_local.h"
#include "crc.h"
#include "version.h"
#include "rc_image.h"
#include "rc_pixops.h"

#ifdef MINGW32
#include <GL/glext.h>	// GL_COLOR_INDEX8_EXT is defined here
#endif /* MINGW32 */


unsigned d_8to24table[256];
unsigned d_8to24table2[256];

static void	OnChange_gl_texturemode (cvar_t *var, char *string, qbool *cancel);

cvar_t		gl_nobind = {"gl_nobind", "0"};
cvar_t		gl_max_size = {"gl_max_size", "4096"};
cvar_t		gl_picmip = {"gl_picmip", "0"};
cvar_t		gl_picmip_world = {"gl_picmip_world", "base"};
cvar_t		gl_picmip_model = {"gl_picmip_model", "base"};
cvar_t		gl_picmip_turb = {"gl_picmip_turb", "base"};
cvar_t		gl_picmip_sprite = {"gl_picmip_sprite", "base"};
cvar_t		gl_texturemode = {"gl_texturemode", "base", 4, OnChange_gl_texturemode};
cvar_t		gl_texturemode_world = {"gl_texturemode_world", "base", 0, OnChange_gl_texturemode};
cvar_t		gl_texturemode_model = {"gl_texturemode_model", "base", 0, OnChange_gl_texturemode};
cvar_t		gl_texturemode_turb = {"gl_texturemode_turb", "base", 0, OnChange_gl_texturemode};
cvar_t		gl_texturemode_sprite = {"gl_texturemode_sprite", "base", 0, OnChange_gl_texturemode};

int		texture_extension_number = 1;

int		gl_lightmap_format = 4;
int		gl_solid_format = 3;
int		gl_alpha_format = 4;

int		gl_filter_2d = GL_LINEAR;

int		gl_max_texsize;

extern byte	scrap_texels[2][256*256*4];	// FIXME FIXME FIXME

typedef struct
{
	int		texnum;
	char	identifier[64];
	int		width, height;
	int		scaled_width, scaled_height;
	int		mode;
	unsigned	crc;
} gltexture_t;

gltexture_t	gltextures[MAX_GLTEXTURES];
int			numgltextures;

qbool	mtexenabled = false;

#ifdef _WIN32
lpMTexFUNC qglMultiTexCoord2f = NULL;
lpSelTexFUNC qglActiveTexture = NULL;
#endif

void GL_Bind (int texnum)
{
	extern int char_textures[1];

	if (gl_nobind.value)
		texnum = char_textures[0];
	if (currenttexture == texnum)
		return;
	currenttexture = texnum;
#ifdef _WIN32
	bindTexFunc (GL_TEXTURE_2D, texnum);
#else
	glBindTexture (GL_TEXTURE_2D, texnum);
#endif
}

static GLenum oldtarget = GL_TEXTURE0_ARB;

void GL_SelectTexture (GLenum target)
{
	if (!gl_mtexable)
		return;
#ifdef _WIN32 // no multitexture under Linux or Darwin yet
	qglActiveTexture (target);
#endif
	if (target == oldtarget)
		return;
	cnttextures[oldtarget-GL_TEXTURE0_ARB] = currenttexture;
	currenttexture = cnttextures[target-GL_TEXTURE0_ARB];
	oldtarget = target;
}

void GL_DisableMultitexture (void)
{
	if (mtexenabled) {
		glDisable (GL_TEXTURE_2D);
		GL_SelectTexture (GL_TEXTURE0_ARB);
		mtexenabled = false;
	}
}

void GL_EnableMultitexture (void)
{
	if (gl_mtexable) {
		GL_SelectTexture (GL_TEXTURE1_ARB);
		glEnable (GL_TEXTURE_2D);
		mtexenabled = true;
	}
}


//====================================================================

typedef struct
{
	char *name, *shortname;
	int	minimize, maximize;
} glmode_t;

static glmode_t modes[] = {
	{"base", "", 0, 0},								// 0
	{"GL_NEAREST", "N", GL_NEAREST, GL_NEAREST},	// 1
	{"GL_LINEAR", "L", GL_LINEAR, GL_LINEAR},		// 2
	{"GL_NEAREST_MIPMAP_NEAREST", "NMN", GL_NEAREST_MIPMAP_NEAREST, GL_NEAREST}, // 3
	{"GL_LINEAR_MIPMAP_NEAREST", "LMN", GL_LINEAR_MIPMAP_NEAREST, GL_LINEAR}, // 4
	{"GL_NEAREST_MIPMAP_LINEAR", "NML", GL_NEAREST_MIPMAP_LINEAR, GL_NEAREST}, // 5
	{"GL_LINEAR_MIPMAP_LINEAR", "LML", GL_LINEAR_MIPMAP_LINEAR, GL_LINEAR} // 6
};

static void FilterForMode (int mode, int *min_filter, int *max_filter)
{
	int i;

	if ((mode & TEX_MODEL) && gl_texturemode_model.value)
		i = gl_texturemode_model.value;
	else if ((mode & TEX_TURB) && gl_texturemode_turb.value)
		i = gl_texturemode_turb.value;
	else if ((mode & TEX_SPRITE) && gl_texturemode_sprite.value)
		i = gl_texturemode_sprite.value;
	else if ((mode & TEX_WORLD) && gl_texturemode_world.value)
		i = gl_texturemode_world.value;
	else
		i = gl_texturemode.value;

	// in case someone defeats the cvar system...
	i = bound (1, i, 6);

	*min_filter = modes[i].minimize;
	*max_filter = modes[i].maximize;
}

static void OnChange_gl_texturemode (cvar_t *var, char *string, qbool *cancel)
{
	int		i;
	gltexture_t	*glt;

	for (i = 0; i < 7; i++)
	{
		if (!i && var==&gl_texturemode)
			continue;	// this cvar can't be set to "base"
		if (!Q_stricmp(modes[i].name, string) || !Q_stricmp(modes[i].shortname, string))
			goto ok;
	}

	Com_Printf ("bad filter name: %s\n", string);
	*cancel = true;		// don't change the cvar
	return;

ok:
	Cvar_Set (var, modes[i].name);
	// we cheat and set a cvar's value to the filter's index,
	// so that we don't need string comparisons later on
	var->value = i;		// GL_NEAREST = 1, GL_LINEAR = 2, ...
	*cancel = true;

	// change all the existing mipmap texture objects
	for (i=0, glt=gltextures ; i<numgltextures ; i++, glt++)
	{
		if (glt->mode & TEX_MIPMAP)
		{
			int min_filter, max_filter;
			FilterForMode (glt->mode, &min_filter, &max_filter);
			GL_Bind (glt->texnum);
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, min_filter);
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, max_filter);
		}
	}
}


//====================================================================

void R_SetPalette (unsigned char *palette)
{
	int			i;
	byte		*pal;
	unsigned	r,g,b;
	byte		*table;

//
// 8 8 8 encoding
//
	pal = palette;
	table = (byte *) d_8to24table;
	for (i = 0; i < 256; i++)
	{
		r = pal[0];
		g = pal[1];
		b = pal[2];
		pal += 3;

		table[0] = r;
		table[1] = g;
		table[2] = b;
		table[3] = 255;
		table += 4;
	}
	d_8to24table[255] = 0;	// 255 is transparent

// Tonik: create a brighter palette for bmodel textures
	pal = palette;
	table = (byte *) d_8to24table2;

	for (i = 0; i < 256; i++)
	{
		r = pal[0] * (2.0 / 1.5); if (r > 255) r = 255;
		g = pal[1] * (2.0 / 1.5); if (g > 255) g = 255;
		b = pal[2] * (2.0 / 1.5); if (b > 255) b = 255;
		pal += 3;

		table[0] = r;
		table[1] = g;
		table[2] = b;
		table[3] = 255;
		table += 4;
	}
	d_8to24table2[255] = 0;	// 255 is transparent
}

//====================================================================


/*
================
GL_FindTexture
================
*/
int GL_FindTexture (char *identifier)
{
	int		i;
	gltexture_t	*glt;

	for (i=0, glt=gltextures ; i<numgltextures ; i++, glt++)
	{
		if (!strcmp (identifier, glt->identifier))
			return gltextures[i].texnum;
	}

	return -1;
}


void GL_MipMap (byte *in, byte *out, int width, int height);

/*
================
GL_ResampleTexture
================
*/
void GL_ResampleTexture (unsigned *indata, int inwidth, int inheight,
		unsigned *outdata, int outwidth, int outheight)
{
	// _pixops_scale is too slow for large downsampling factors, so make use
	// of the fast GL_MipMap when possible
	if (inwidth >= outwidth*2 && inheight >= outheight*2) {
		int tw, th;
		byte *in, *buf;

		for (tw = outwidth, th = outheight; tw*2 <= inwidth && th*2 <= inheight; ) {
			tw *= 2;
			th *= 2;
		}

		if (inwidth > tw || inheight > th) {
			buf = Q_malloc (tw * th * 4);
			_pixops_scale ((guchar *)buf, 0, 0, tw, th, tw * 4, 4, 1, (const guchar *)indata,
				inwidth, inheight, inwidth * 4, 4, 1, (double)tw/inwidth, (double)th/inheight, PIXOPS_INTERP_BILINEAR);
			in = buf;
		} else {
			buf = Q_malloc ((tw/2) * (th/2) * 4);
			in = (byte *)indata;
		}

		while (tw > outwidth) {
			GL_MipMap (in, buf, tw, th);
			in = buf;
			tw >>= 1;
			th >>= 1;
		}

		memcpy (outdata, buf, outwidth*outheight*4);
		Q_free (buf);
		return;
	}

	_pixops_scale ((guchar *)outdata, 0, 0, outwidth, outheight, outwidth * 4, 4, 1, (const guchar *)indata,
		inwidth, inheight, inwidth * 4, 4, 1, (double)outwidth/inwidth, (double)outheight/inheight, PIXOPS_INTERP_BILINEAR);
}


/*
================
GL_MipMap

Operates in place, quartering the size of the texture
================
*/
void GL_MipMap (byte *in, byte *out, int width, int height)
{
	int		i, j;

	width <<=2;
	height >>= 1;
	for (i = 0; i < height; i++, in+=width)
	{
		for (j=0 ; j<width ; j+=8, out+=4, in+=8)
		{
			out[0] = (in[0] + in[4] + in[width+0] + in[width+4])>>2;
			out[1] = (in[1] + in[5] + in[width+1] + in[width+5])>>2;
			out[2] = (in[2] + in[6] + in[width+2] + in[width+6])>>2;
			out[3] = (in[3] + in[7] + in[width+3] + in[width+7])>>2;
		}
	}
}

static void
ScaleDimensions (int width, int height, int *scaled_width, int *scaled_height, int mode)
{
	int picmip, max_texsize;
	qbool scale;

	scale = (mode & TEX_MIPMAP) && !(mode & TEX_NOSCALE);

	for (*scaled_width = 1; *scaled_width < width; *scaled_width <<= 1) {};
	for (*scaled_height = 1; *scaled_height < height; *scaled_height <<= 1) {};

	picmip =
(mode & TEX_MODEL && (gl_picmip_model.value || gl_picmip_model.string[0] == '0')) ?
			gl_picmip_model.value :
(mode & TEX_TURB && (gl_picmip_turb.value || gl_picmip_turb.string[0] == '0')) ?
			gl_picmip_turb.value :
(mode & TEX_SPRITE && (gl_picmip_sprite.value || gl_picmip_sprite.string[0] == '0')) ?
			gl_picmip_sprite.value :
(mode & TEX_WORLD && (gl_picmip_world.value || gl_picmip_world.string[0] == '0')) ?
			gl_picmip_world.value :
			scale ? gl_picmip.value : 0;

	picmip = (int) bound(0, picmip, 16);
	*scaled_width >>= picmip;
	*scaled_height >>= picmip;

	if (mode & TEX_MIPMAP && !(mode & TEX_NOSCALE) && gl_max_size.value) {
		max_texsize = min(gl_max_texsize, gl_max_size.value);
		max_texsize = max(max_texsize, 1);
	} else {
		max_texsize = gl_max_texsize;
	}
	*scaled_width = bound(1, *scaled_width, max_texsize);
	*scaled_height = bound(1, *scaled_height, max_texsize);
}

/*
static int RoundToPowerOf2 (int in) {
	int out;
	for (out = 1; out < in; out <<= 1)
		;
	return out;
}
*/

/*
===============
GL_Upload32

Accepts TEX_MIPMAP, TEX_ALPHA, TEX_NOSCALE
===============
*/
void GL_Upload32 (unsigned *data, int width, int height, int mode /*qbool mipmap, qbool alpha*/)
{
	int			samples;
	unsigned	*scaled, *scaled_buf = NULL;
	int			scaled_width, scaled_height;
	int min_filter, max_filter;

	ScaleDimensions (width, height, &scaled_width, &scaled_height, mode);

	samples = (mode & TEX_ALPHA) ? gl_alpha_format : gl_solid_format;

	if (scaled_width == width && scaled_height == height)
	{
		if (!(mode & TEX_MIPMAP))
		{
			glTexImage2D (GL_TEXTURE_2D, 0, samples, scaled_width, scaled_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data);
			goto done;
		}
		scaled = data;
	}
	else
	{
		scaled_buf = Q_malloc (scaled_width * scaled_height * 4);
		scaled = scaled_buf;
		GL_ResampleTexture (data, width, height, scaled, scaled_width, scaled_height);
	}

	glTexImage2D (GL_TEXTURE_2D, 0, samples, scaled_width, scaled_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, scaled);
	if (mode & TEX_MIPMAP)
	{
		int		miplevel;

		miplevel = 0;
		while (scaled_width > 1 || scaled_height > 1)
		{
			GL_MipMap ((byte *)scaled, (byte *)scaled, scaled_width, scaled_height);
			scaled_width >>= 1;
			scaled_height >>= 1;
			if (scaled_width < 1)
				scaled_width = 1;
			if (scaled_height < 1)
				scaled_height = 1;
			miplevel++;
			glTexImage2D (GL_TEXTURE_2D, miplevel, samples, scaled_width, scaled_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, scaled);
		}
	}
done: ;


	if (mode & TEX_MIPMAP) {
		FilterForMode (mode, &min_filter, &max_filter);
	} else {
		min_filter = gl_filter_2d;
		max_filter = gl_filter_2d;
	}
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, min_filter);
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, max_filter);

	free (scaled_buf);
}

/*
===============
GL_Upload8

Accepts TEX_MIPMAP, TEX_ALPHA, TEX_FULLBRIGHTMASK, TEX_BRIGHTEN, TEX_NOSCALE
===============
*/
void GL_Upload8 (byte *data, int width, int height, int mode)
{
	static	unsigned	trans[640*480];		// FIXME, temporary
	int			i, s;
	qbool		noalpha;
	int			p;
	unsigned	*table;

	if (mode & TEX_BRIGHTEN)
		table = d_8to24table2;
	else
		table = d_8to24table;

	s = width*height;

	if (mode & TEX_FULLBRIGHTMASK)
	{
		mode |= TEX_ALPHA;
	// this is a fullbright mask, so make all non-fullbright
	// colors transparent
		for (i=0 ; i<s ; i++)
		{
			p = data[i];
			if (p < 224)
				trans[i] = table[p] & LittleLong(0x00FFFFFF); // transparent
			else
				trans[i] = table[p];	// fullbright
		}
	}
	else if (mode & TEX_ALPHA)
	{
	// if there are no transparent pixels, make it a 3 component
	// texture even if it was specified as otherwise
		noalpha = true;
		for (i=0 ; i<s ; i++)
		{
			p = data[i];
			if (p == 255)
				noalpha = false;
			trans[i] = table[p];
		}

		if (noalpha)
			mode &= ~TEX_ALPHA;
	}
	else
	{
		if (s&3)
			Sys_Error ("GL_Upload8: s&3");
		for (i=0 ; i<s ; i+=4)
		{
			trans[i] = table[data[i]];
			trans[i+1] = table[data[i+1]];
			trans[i+2] = table[data[i+2]];
			trans[i+3] = table[data[i+3]];
		}
	}

	GL_Upload32 (trans, width, height, mode);
}

/*
================
GL_LoadTexture

Accepts TEX_MIPMAP, TEX_ALPHA, TEX_FULLBRIGHTMASK, TEX_BRIGHTEN, TEX_NOSCALE
================
*/
int GL_LoadTexture (char *identifier, int width, int height, byte *data, int mode)
{
	int i, scaled_width, scaled_height;
	unsigned	crc = 0;
	gltexture_t	*glt;

	if (lightmode != 2)
		mode &= ~TEX_BRIGHTEN;

	ScaleDimensions (width, height, &scaled_width, &scaled_height, mode);

	// see if the texture is already present
	if (identifier[0]) {
		crc = CRC_Block (data, width*height);
		for (i=0, glt=gltextures ; i<numgltextures ; i++, glt++) {
			if (!strncmp (identifier, glt->identifier, sizeof(glt->identifier)-1)) {
				if (width == glt->width && height == glt->height
					&& crc == glt->crc && (mode & TEX_BRIGHTEN) == (glt->mode & TEX_BRIGHTEN)
					&& scaled_width == glt->scaled_width && scaled_height == glt->scaled_height)
					return gltextures[i].texnum;
				else
					goto setuptexture;	// reload the texture into the same slot
			}
		}
	}
	else
		glt = &gltextures[numgltextures];

	if (numgltextures == MAX_GLTEXTURES)
		Sys_Error ("GL_LoadTexture: numgltextures == MAX_GLTEXTURES");
	numgltextures++;

	strlcpy (glt->identifier, identifier, sizeof(glt->identifier));
	glt->texnum = texture_extension_number;
	texture_extension_number++;

setuptexture:
	glt->width = width;
	glt->height = height;
	glt->scaled_width = scaled_width;
	glt->scaled_height = scaled_height;
	glt->mode = mode;
	glt->crc = crc;

	GL_Bind (glt->texnum);

	GL_Upload8 (data, width, height, mode);

	return glt->texnum;
}


static void brighten32 (byte *data, int size)
{
	byte *p;
	int i;

	p = data;
	for (i = 0; i < size/4; i++)
	{
		p[0] = min(p[0] * 2.0/1.5, 255);
		p[1] = min(p[1] * 2.0/1.5, 255);
		p[2] = min(p[2] * 2.0/1.5, 255);
		p += 4;
	}
}

/*
================
GL_LoadTexture32

Accepts TEX_MIPMAP, TEX_ALPHA, TEX_BRIGHTEN(FIXME not yet), TEX_NOSCALE

FIXME: merge with GL_LoadTexture
================
*/
int GL_LoadTexture32 (char *identifier, int width, int height, byte *data, int mode)
{
	int			i;
	unsigned	crc = 0;
	gltexture_t	*glt;

	if (lightmode != 2)
		mode &= ~TEX_BRIGHTEN;

	crc = CRC_Block (data, width*height);

	// see if the texture is already present
	if (identifier[0]) {
		for (i=0, glt=gltextures ; i<numgltextures ; i++, glt++) {
			if (!strncmp (identifier, glt->identifier, sizeof(glt->identifier)-1)) {
				if (width == glt->width && height == glt->height
					&& crc == glt->crc && ((mode & TEX_BRIGHTEN) == (glt->mode & TEX_BRIGHTEN)))
					return gltextures[i].texnum;
				else
					goto setuptexture;	// reload the texture into the same slot
			}
		}
	}
	else
		glt = &gltextures[numgltextures];

	if (numgltextures == MAX_GLTEXTURES)
		Sys_Error ("GL_LoadTexture: numgltextures == MAX_GLTEXTURES");
	numgltextures++;

	strlcpy (glt->identifier, identifier, sizeof(glt->identifier));
	glt->texnum = texture_extension_number;
	texture_extension_number++;

setuptexture:
	glt->width = width;
	glt->height = height;
	glt->mode = mode;
	glt->crc = crc;

	GL_Bind (glt->texnum);

	if (mode & TEX_BRIGHTEN) {
		// FIXME, we're not supposed to modify data passed in to LoadTexture,
		// but it doesn't currently break anything so we do
		brighten32 (data, width * height * 4);
	}

	GL_Upload32 ((unsigned int *)data, width, height, mode);

	return glt->texnum;
}


int GL_LoadTextureImage (char *filename, char *identifier, int matchwidth, int matchheight, int mode)
{
	int texnum;
	byte *data;
//	gltexture_t *gltexture;
	int width, height;
	char	extname[MAX_QPATH], *c;

//	if (no24bit)
//		return 0;

	if (!identifier)
		identifier = filename;

#if 0
	gltexture = current_texture = GL_FindTexture(identifier);

	if (!(data = GL_LoadImagePixels (filename, matchwidth, matchheight, mode))) {
		texnum =  (gltexture && !current_texture) ? gltexture->texnum : 0;
	} else {
		texnum = GL_LoadTexturePixels(data, identifier, image_width, image_height, mode);
		Q_free(data);	// data was Q_malloc'ed by GL_LoadImagePixels
	}
#endif

#ifdef WITH_PNG
	snprintf (extname, sizeof(extname), "%s.png", filename);
	for (c = extname; *c; c++)
		if (*c == '*')
			*c = '#';
	data = Image_LoadPNG (NULL, extname, 0, 0);
	if (data) {
		extern int image_width, image_height;
		width = image_width;
		height = image_height;
		goto ok;
	}
#endif

	snprintf (extname, sizeof(extname), "%s.tga", filename);
	for (c = extname; *c; c++)
		if (*c == '*')
			*c = '#';
	LoadTGA (extname, &data, &width, &height);
	if (!data)
		return 0;

#ifdef WITH_PNG
ok:
#endif
	texnum = GL_LoadTexture32 (identifier, width, height, data, mode);

	Q_free (data);

	return texnum;
}


static void R_InitParticleTexture (void)
{
	int		i, x, y;
	unsigned int	data[32][32];

	particletexture = texture_extension_number++;
    GL_Bind (particletexture);

	// clear to transparent white
	for (i=0 ; i<32*32 ; i++)
		((unsigned *)data)[i] = LittleLong(0x00FFFFFF);

	// draw a circle in the top left corner
	for (x=0 ; x<16 ; x++)
		for (y=0 ; y<16 ; y++) {
			if ((x - 7.5)*(x - 7.5) + (y - 7.5)*(y - 7.5) <= 8*8)
				data[y][x] = LittleLong(0xFFFFFFFF);	// solid white
		}

	glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE);
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_NEAREST);
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
	GL_Upload32 ((unsigned *) data, 32, 32, TEX_MIPMAP|TEX_ALPHA);
}


static void R_InitDefaultTexture (void)
{
	int		x,y, m;
	byte	*dest;

// create a simple checkerboard texture for the default
	r_notexture_mip = Hunk_AllocName (sizeof(texture_t) + 16*16+8*8+4*4+2*2, "notexture");

	r_notexture_mip->width = r_notexture_mip->height = 16;
	r_notexture_mip->offsets[0] = sizeof(texture_t);
	r_notexture_mip->offsets[1] = r_notexture_mip->offsets[0] + 16*16;
	r_notexture_mip->offsets[2] = r_notexture_mip->offsets[1] + 8*8;
	r_notexture_mip->offsets[3] = r_notexture_mip->offsets[2] + 4*4;

	for (m=0 ; m<4 ; m++)
	{
		dest = (byte *)r_notexture_mip + r_notexture_mip->offsets[m];
		for (y=0 ; y< (16>>m) ; y++)
			for (x=0 ; x< (16>>m) ; x++)
			{
				if (  (y< (8>>m) ) ^ (x< (8>>m) ) )
					*dest++ = 0;
				else
					*dest++ = 15;
			}
	}
}


/*
===============
R_InitTextures
===============
*/
void R_InitTextures (void)
{
	Cvar_Register (&gl_nobind);
	Cvar_Register (&gl_max_size);
	Cvar_Register (&gl_picmip);
	Cvar_Register (&gl_picmip_world);
	Cvar_Register (&gl_picmip_model);
	Cvar_Register (&gl_picmip_turb);
	Cvar_Register (&gl_picmip_sprite);
	Cvar_Register (&gl_texturemode);
	Cvar_Register (&gl_texturemode_world);
	Cvar_Register (&gl_texturemode_model);
	Cvar_Register (&gl_texturemode_turb);
	Cvar_Register (&gl_texturemode_sprite);

	texture_extension_number = 1;
	numgltextures = 0;

	// get the maximum texture size from driver
	glGetIntegerv (GL_MAX_TEXTURE_SIZE, (GLint *) &gl_max_texsize);

	GL_AllocTextureSlots ();

	R_InitDefaultTexture ();
	R_InitParticleTexture ();

}

/* vi: set noet ts=4 sts=4 ai sw=4: */
