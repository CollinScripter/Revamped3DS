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

#include "quakedef.h"
#include "rc_image.h"
#include "winquake.h"

#ifdef WITH_PNG
#include "qlib.h"
#include "png.h"
#endif

int image_width, image_height;


/************************************ PNG ************************************/
#ifdef WITH_PNG

#ifdef WITH_PNG_STATIC

#define png_handle 1

#define qpng_set_sig_bytes png_set_sig_bytes
#define qpng_sig_cmp png_sig_cmp
#define qpng_create_read_struct png_create_read_struct
#define qpng_create_write_struct png_create_write_struct
#define qpng_create_info_struct png_create_info_struct
#define qpng_write_info png_write_info
#define qpng_read_info png_read_info
#define qpng_set_expand png_set_expand
#define qpng_set_gray_1_2_4_to_8 png_set_gray_1_2_4_to_8
#define qpng_set_palette_to_rgb png_set_palette_to_rgb
#define qpng_set_tRNS_to_alpha png_set_tRNS_to_alpha
#define qpng_set_gray_to_rgb png_set_gray_to_rgb
#define qpng_set_filler png_set_filler
#define qpng_set_strip_16 png_set_strip_16
#define qpng_read_update_info png_read_update_info
#define qpng_read_image png_read_image
#define qpng_write_image png_write_image
#define qpng_write_end png_write_end
#define qpng_read_end png_read_end
#define qpng_destroy_read_struct png_destroy_read_struct
#define qpng_destroy_write_struct png_destroy_write_struct
#define qpng_set_compression_level png_set_compression_level
#define qpng_set_write_fn png_set_write_fn
#define qpng_set_read_fn png_set_read_fn
#define qpng_get_io_ptr png_get_io_ptr
#define qpng_get_valid png_get_valid
#define qpng_get_rowbytes png_get_rowbytes
#define qpng_get_channels png_get_channels
#define qpng_get_bit_depth png_get_bit_depth
#define qpng_get_IHDR png_get_IHDR
#define qpng_set_IHDR png_set_IHDR
#define qpng_set_PLTE png_set_PLTE

#else	// !WITH_PNG_STATIC

static QLIB_HANDLETYPE_T png_handle = NULL;
static QLIB_HANDLETYPE_T zlib_handle = NULL;

static void (*qpng_set_sig_bytes)(png_structp, int);
static int (*qpng_sig_cmp)(png_bytep, png_size_t, png_size_t);
static png_structp (*qpng_create_read_struct)(png_const_charp, png_voidp, png_error_ptr, png_error_ptr);
static png_structp (*qpng_create_write_struct)(png_const_charp, png_voidp, png_error_ptr, png_error_ptr);
static png_infop (*qpng_create_info_struct)(png_structp);
static void (*qpng_write_info)(png_structp, png_infop);
static void (*qpng_read_info)(png_structp, png_infop);
static void (*qpng_set_expand)(png_structp);
static void (*qpng_set_gray_1_2_4_to_8)(png_structp);
static void (*qpng_set_palette_to_rgb)(png_structp);
static void (*qpng_set_tRNS_to_alpha)(png_structp);
static void (*qpng_set_gray_to_rgb)(png_structp);
static void (*qpng_set_filler)(png_structp, png_uint_32, int);
static void (*qpng_set_strip_16)(png_structp);
static void (*qpng_read_update_info)(png_structp, png_infop);
static void (*qpng_read_image)(png_structp, png_bytepp);
static void (*qpng_write_image)(png_structp, png_bytepp);
static void (*qpng_write_end)(png_structp, png_infop);
static void (*qpng_read_end)(png_structp, png_infop);
static void (*qpng_destroy_read_struct)(png_structpp, png_infopp, png_infopp);
static void (*qpng_destroy_write_struct)(png_structpp, png_infopp);
static void (*qpng_set_compression_level)(png_structp, int);
static void (*qpng_set_write_fn)(png_structp, png_voidp, png_rw_ptr, png_flush_ptr);
static void (*qpng_set_read_fn)(png_structp, png_voidp, png_rw_ptr);
static png_voidp (*qpng_get_io_ptr)(png_structp);
static png_uint_32 (*qpng_get_valid)(png_structp, png_infop, png_uint_32);
static png_uint_32 (*qpng_get_rowbytes)(png_structp, png_infop);
static png_byte (*qpng_get_channels)(png_structp, png_infop);
static png_byte (*qpng_get_bit_depth)(png_structp, png_infop);
static png_uint_32 (*qpng_get_IHDR)(png_structp, png_infop, png_uint_32 *, png_uint_32 *, int *, int *, int *, int *, int *);
static void (*qpng_set_IHDR)(png_structp, png_infop, png_uint_32, png_uint_32, int, int, int, int, int);
static void (*qpng_set_PLTE)(png_structp, png_infop, png_colorp, int);

#define NUM_PNGPROCS	(sizeof(pngprocs)/sizeof(pngprocs[0]))

qlib_dllfunction_t pngprocs[] = {
	{"png_set_sig_bytes", (void **) &qpng_set_sig_bytes},
	{"png_sig_cmp", (void **) &qpng_sig_cmp},
	{"png_create_read_struct", (void **) &qpng_create_read_struct},
	{"png_create_write_struct", (void **) &qpng_create_write_struct},
	{"png_create_info_struct", (void **) &qpng_create_info_struct},
	{"png_write_info", (void **) &qpng_write_info},
	{"png_read_info", (void **) &qpng_read_info},
	{"png_set_expand", (void **) &qpng_set_expand},
	{"png_set_gray_1_2_4_to_8", (void **) &qpng_set_gray_1_2_4_to_8},
	{"png_set_palette_to_rgb", (void **) &qpng_set_palette_to_rgb},
	{"png_set_tRNS_to_alpha", (void **) &qpng_set_tRNS_to_alpha},
	{"png_set_gray_to_rgb", (void **) &qpng_set_gray_to_rgb},
	{"png_set_filler", (void **) &qpng_set_filler},
	{"png_set_strip_16", (void **) &qpng_set_strip_16},
	{"png_read_update_info", (void **) &qpng_read_update_info},
	{"png_read_image", (void **) &qpng_read_image},
	{"png_write_image", (void **) &qpng_write_image},
	{"png_write_end", (void **) &qpng_write_end},
	{"png_read_end", (void **) &qpng_read_end},
	{"png_destroy_read_struct", (void **) &qpng_destroy_read_struct},
	{"png_destroy_write_struct", (void **) &qpng_destroy_write_struct},
	{"png_set_compression_level", (void **) &qpng_set_compression_level},
	{"png_set_write_fn", (void **) &qpng_set_write_fn},
	{"png_set_read_fn", (void **) &qpng_set_read_fn},
	{"png_get_io_ptr", (void **) &qpng_get_io_ptr},
	{"png_get_valid", (void **) &qpng_get_valid},
	{"png_get_rowbytes", (void **) &qpng_get_rowbytes},
	{"png_get_channels", (void **) &qpng_get_channels},
	{"png_get_bit_depth", (void **) &qpng_get_bit_depth},
	{"png_get_IHDR", (void **) &qpng_get_IHDR},
	{"png_set_IHDR", (void **) &qpng_set_IHDR},
	{"png_set_PLTE", (void **) &qpng_set_PLTE},
};

static void PNG_FreeLibrary(void) {
	if (png_handle)
		QLIB_FREELIBRARY(png_handle);
	if (zlib_handle)
		QLIB_FREELIBRARY(zlib_handle);
}

static qbool PNG_LoadLibrary(void) {
	if (COM_CheckParm("-nolibpng"))
		return false;

#ifdef _WIN32
	if (!(png_handle = LoadLibrary("libpng.dll"))) {
#else
#ifdef __APPLE__
	if (!(png_handle = dlopen("libpng12.dylib", RTLD_NOW))) {
		if (!(zlib_handle = dlopen("libz.dylib", RTLD_NOW))) {
#else
	if (!(png_handle = dlopen("libpng12.so.0", RTLD_NOW)) && !(png_handle = dlopen("libpng.so", RTLD_NOW))) {
		if (!(zlib_handle = dlopen("libz.so", RTLD_NOW | RTLD_GLOBAL))) {
#endif
			QLib_MissingModuleError(QLIB_ERROR_MODULE_NOT_FOUND, "libz", "-nolibpng", "png image features");
			png_handle = zlib_handle = NULL;
			return false;
		}
#ifdef __APPLE__
		if (!(png_handle = dlopen("libpng12.dylib", RTLD_NOW)))
#else
		if (!(png_handle = dlopen("libpng12.so.0", RTLD_NOW)) && !(png_handle = dlopen("libpng.so", RTLD_NOW)))
#endif
#endif
		{
			PNG_FreeLibrary();
			QLib_MissingModuleError(QLIB_ERROR_MODULE_NOT_FOUND, "libpng", "-nolibpng", "png image features");
			png_handle = zlib_handle = NULL;
			return false;
		}
	}

	if (!QLib_ProcessProcdef(png_handle, pngprocs, NUM_PNGPROCS)) {
		PNG_FreeLibrary();
		QLib_MissingModuleError(QLIB_ERROR_MODULE_MISSING_PROC, "libpng", "-nolibpng", "png image features");
		png_handle = zlib_handle = NULL;
		return false;
	}

	return true;
}
#endif	// !WITH_PNG_STATIC

static void PNG_IO_user_read_data(png_structp png_ptr, png_bytep data, png_size_t length) {
	FILE *f = (FILE *) qpng_get_io_ptr(png_ptr);
	fread(data, 1, length, f);
}

static void PNG_IO_user_write_data(png_structp png_ptr, png_bytep data, png_size_t length) {
	FILE *f = (FILE *) qpng_get_io_ptr(png_ptr);
	fwrite(data, 1, length, f);
}

static void PNG_IO_user_flush_data(png_structp png_ptr) {
	FILE *f = (FILE *) qpng_get_io_ptr(png_ptr);
	fflush(f);
}


byte *Image_LoadPNG (FILE *fin, char *filename, int matchwidth, int matchheight) {
	byte header[8], **rowpointers, *data;
	png_structp png_ptr;
	png_infop pnginfo;
	int y, width, height, bitdepth, colortype, interlace, compression, filter, bytesperpixel;
	unsigned long rowbytes;

	if (!png_handle)
		return NULL;

	if (!fin && FS_FOpenFile (filename, &fin) == -1)
		return NULL;

	fread(header, 1, 8, fin);

	if (qpng_sig_cmp(header, 0, 8)) {
		Com_DPrintf ("Invalid PNG image %s\n", COM_SkipPath(filename));
		fclose(fin);
		return NULL;
	}

	if (!(png_ptr = qpng_create_read_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL))) {
		fclose(fin);
		return NULL;
	}

	if (!(pnginfo = qpng_create_info_struct(png_ptr))) {
		qpng_destroy_read_struct(&png_ptr, &pnginfo, NULL);
		fclose(fin);
		return NULL;
	}

	if (setjmp(png_ptr->jmpbuf)) {
		qpng_destroy_read_struct(&png_ptr, &pnginfo, NULL);
		fclose(fin);
		return NULL;
	}

    qpng_set_read_fn(png_ptr, fin, PNG_IO_user_read_data);
	qpng_set_sig_bytes(png_ptr, 8);
	qpng_read_info(png_ptr, pnginfo);
	qpng_get_IHDR(png_ptr, pnginfo, (png_uint_32 *) &width, (png_uint_32 *) &height, &bitdepth,
		&colortype, &interlace, &compression, &filter);

	if (width > IMAGE_MAX_DIMENSIONS || height > IMAGE_MAX_DIMENSIONS) {
		Com_DPrintf ("PNG image %s exceeds maximum supported dimensions\n", COM_SkipPath(filename));
		qpng_destroy_read_struct(&png_ptr, &pnginfo, NULL);
		fclose(fin);
		return NULL;
	}

	if ((matchwidth && width != matchwidth) || (matchheight && height != matchheight)) {
		qpng_destroy_read_struct(&png_ptr, &pnginfo, NULL);
		fclose(fin);
		return NULL;
	}

	if (colortype == PNG_COLOR_TYPE_PALETTE) {
		qpng_set_palette_to_rgb(png_ptr);
		qpng_set_filler(png_ptr, 255, PNG_FILLER_AFTER);		
	}

	if (colortype == PNG_COLOR_TYPE_GRAY && bitdepth < 8) 
		qpng_set_gray_1_2_4_to_8(png_ptr);
	
	if (qpng_get_valid(png_ptr, pnginfo, PNG_INFO_tRNS))	
		qpng_set_tRNS_to_alpha(png_ptr);

	if (colortype == PNG_COLOR_TYPE_GRAY || colortype == PNG_COLOR_TYPE_GRAY_ALPHA)
		qpng_set_gray_to_rgb(png_ptr);

	if (colortype != PNG_COLOR_TYPE_RGBA)				
		qpng_set_filler(png_ptr, 255, PNG_FILLER_AFTER);

	if (bitdepth < 8)
		qpng_set_expand (png_ptr);
	else if (bitdepth == 16)
		qpng_set_strip_16(png_ptr);


	qpng_read_update_info(png_ptr, pnginfo);
	rowbytes = qpng_get_rowbytes(png_ptr, pnginfo);
	bytesperpixel = qpng_get_channels(png_ptr, pnginfo);
	bitdepth = qpng_get_bit_depth(png_ptr, pnginfo);

	if (bitdepth != 8 || bytesperpixel != 4) {
		Com_DPrintf ("Unsupported PNG image %s: Bad color depth and/or bpp\n", COM_SkipPath(filename));
		qpng_destroy_read_struct(&png_ptr, &pnginfo, NULL);
		fclose(fin);
		return NULL;
	}

	data = (byte *) Q_malloc(height * rowbytes );
	rowpointers = (byte **) Q_malloc(height * sizeof(*rowpointers));

	for (y = 0; y < height; y++)
		rowpointers[y] = data + y * rowbytes;

	qpng_read_image(png_ptr, rowpointers);
	qpng_read_end(png_ptr, NULL);

	qpng_destroy_read_struct(&png_ptr, &pnginfo, NULL);
	Q_free(rowpointers);
	fclose(fin);
	image_width = width;
	image_height = height;
	return data;
}

int Image_WritePNG (char *filename, int compression, byte *pixels, int width, int height) {
	char name[MAX_OSPATH];
	int i, bpp = 3, pngformat, width_sign;
	FILE *fp;
	png_structp png_ptr;
	png_infop info_ptr;
	png_byte **rowpointers;
	snprintf (name, sizeof(name), "%s/%s", com_basedir, filename);

	if (!png_handle)
		return false;

	width_sign = (width < 0) ? -1 : 1;
	width = abs(width);

	if (!(fp = fopen (name, "wb"))) {
		COM_CreatePath (name);
		if (!(fp = fopen (name, "wb")))
			return false;
	}

	if (!(png_ptr = qpng_create_write_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL))) {
		fclose(fp);
		return false;
	}

	if (!(info_ptr = qpng_create_info_struct(png_ptr))) {
		qpng_destroy_write_struct(&png_ptr, (png_infopp) NULL);
		fclose(fp);
		return false;
	}

	if (setjmp(png_ptr->jmpbuf)) {
		qpng_destroy_write_struct(&png_ptr, &info_ptr);
		fclose(fp);
		return false;
	}

    qpng_set_write_fn(png_ptr, fp, PNG_IO_user_write_data, PNG_IO_user_flush_data);
	qpng_set_compression_level(png_ptr, bound(Z_NO_COMPRESSION, compression, Z_BEST_COMPRESSION));

	pngformat = (bpp == 4) ? PNG_COLOR_TYPE_RGBA : PNG_COLOR_TYPE_RGB;
	qpng_set_IHDR(png_ptr, info_ptr, width, height, 8, pngformat,
		PNG_INTERLACE_NONE, PNG_COMPRESSION_TYPE_DEFAULT, PNG_FILTER_TYPE_DEFAULT);

	qpng_write_info(png_ptr, info_ptr);

	rowpointers = (png_byte **) Q_malloc (height * sizeof(*rowpointers));
	for (i = 0; i < height; i++)
		rowpointers[i] = pixels + i * width_sign * width * bpp;
	qpng_write_image(png_ptr, rowpointers);
	qpng_write_end(png_ptr, info_ptr);
	Q_free(rowpointers);
	qpng_destroy_write_struct(&png_ptr, &info_ptr);
	fclose(fp);
	return true;
}

int Image_WritePNGPLTE (char *filename, int compression,
#ifdef GLQUAKE
	byte *pixels, int width, int height, byte *palette)
#else
	byte *pixels, int width, int height, int rowbytes, byte *palette)
#endif
{
#ifdef GLQUAKE
	int rowbytes = width;
#endif
	int i;
	char name[MAX_OSPATH];
	FILE *fp;
	png_structp png_ptr;
	png_infop info_ptr;
	png_byte **rowpointers;

	if (!png_handle)
		return false;

	snprintf (name, sizeof(name), "%s/%s", com_basedir, filename);
	
	if (!(fp = fopen (name, "wb"))) {
		COM_CreatePath (name);
		if (!(fp = fopen (name, "wb")))
			return false;
	}

	if (!(png_ptr = qpng_create_write_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL))) {
		fclose(fp);
		return false;
	}

	if (!(info_ptr = qpng_create_info_struct(png_ptr))) {
		qpng_destroy_write_struct(&png_ptr, (png_infopp) NULL);
		fclose(fp);
		return false;
	}

	if (setjmp(png_ptr->jmpbuf)) {
		qpng_destroy_write_struct(&png_ptr, &info_ptr);
		fclose(fp);
		return false;
	}

    qpng_set_write_fn(png_ptr, fp, PNG_IO_user_write_data, PNG_IO_user_flush_data);
	qpng_set_compression_level(png_ptr, bound(Z_NO_COMPRESSION, compression, Z_BEST_COMPRESSION));

	qpng_set_IHDR(png_ptr, info_ptr, width, height, 8, PNG_COLOR_TYPE_PALETTE,
		PNG_INTERLACE_NONE, PNG_COMPRESSION_TYPE_DEFAULT, PNG_FILTER_TYPE_DEFAULT);
	qpng_set_PLTE(png_ptr, info_ptr, (png_color *) palette, 256);

	qpng_write_info(png_ptr, info_ptr);

	rowpointers = (png_byte **) Q_malloc (height * sizeof(*rowpointers));
	for (i = 0; i < height; i++)
		rowpointers[i] = pixels + i * rowbytes;
	qpng_write_image(png_ptr, rowpointers);
	qpng_write_end(png_ptr, info_ptr);
	Q_free(rowpointers);
	qpng_destroy_write_struct(&png_ptr, &info_ptr);
	fclose(fp);
	return true;
}
#endif

/************************************ TGA ************************************/

/*
=========================================================

TARGA LOADING

=========================================================
*/

typedef struct _TargaHeader {
	unsigned char 	id_length, colormap_type, image_type;
	unsigned short	colormap_index, colormap_length;
	unsigned char	colormap_size;
	unsigned short	x_origin, y_origin, width, height;
	unsigned char	pixel_size, attributes;
} TargaHeader;

/*
=============
LoadTGA
=============
*/
#if 0
void LoadTGA (char *filename, byte **out, int *width, int *height)
{
	int		columns, rows, numPixels;
	byte	*pixbuf, *tgabuf;
	int		row, column;
	TargaHeader targa_header;

	*out = NULL;
	tgabuf = FS_LoadTempFile (filename);
	if (!tgabuf)
	{
		Com_DPrintf ("LoadTGA: Could not open %s\n", filename);
		return;
	}

	targa_header.id_length = *(byte *)tgabuf++;
	targa_header.colormap_type = *(byte *)tgabuf++;
	targa_header.image_type = *(byte *)tgabuf++;
	
	targa_header.colormap_index = LittleShort (*(short *)tgabuf); tgabuf += 2;
	targa_header.colormap_length = LittleShort (*(short *)tgabuf); tgabuf += 2;
	targa_header.colormap_size = *(byte *)tgabuf++;
	targa_header.x_origin = LittleShort (*(short *)tgabuf); tgabuf += 2;
	targa_header.y_origin = LittleShort (*(short *)tgabuf); tgabuf += 2;
	targa_header.width = LittleShort (*(short *)tgabuf); tgabuf += 2;
	targa_header.height = LittleShort (*(short *)tgabuf); tgabuf += 2;
	targa_header.pixel_size = *(byte *)tgabuf++;
	targa_header.attributes = *(byte *)tgabuf++;

	if (targa_header.image_type != 2 && targa_header.image_type != 10)
	{
		Com_DPrintf ("LoadTGA: Only type 2 and 10 targa RGB images supported\n");
		return;
	}

	if (targa_header.colormap_type != 0 || (targa_header.pixel_size != 32 && targa_header.pixel_size != 24))
	{
		Com_DPrintf ("LoadTGA: Only 32 or 24 bit images supported (no colormaps)\n");
		return;
	}

	columns = targa_header.width;
	rows = targa_header.height;
	numPixels = columns * rows;

	if (width)
		*width = columns;
	if (height)
		*height = rows;

	*out = Q_malloc (numPixels*4 + 128000 /* !!!!TESTING */);

	if (targa_header.id_length != 0)
		tgabuf += targa_header.id_length;
	
	if (targa_header.image_type==2) {  // Uncompressed, RGB images
		for (row = rows - 1; row >= 0; row--) {
			pixbuf = *out + ((targa_header.attributes & 0x20) ? rows-1-row : row) * columns * 4;
			for(column=0; column<columns; column++) {
				unsigned char red,green,blue,alphabyte;
				switch (targa_header.pixel_size) {
					case 24:
							
							blue = *(byte *)tgabuf++;
							green = *(byte *)tgabuf++;
							red = *(byte *)tgabuf++;
							*pixbuf++ = red;
							*pixbuf++ = green;
							*pixbuf++ = blue;
							*pixbuf++ = 255;
							break;
					case 32:
							blue = *(byte *)tgabuf++;
							green = *(byte *)tgabuf++;
							red = *(byte *)tgabuf++;
							alphabyte = *(byte *)tgabuf++;
							*pixbuf++ = red;
							*pixbuf++ = green;
							*pixbuf++ = blue;
							*pixbuf++ = alphabyte;
							break;
				}
			}
		}
	}
	else if (targa_header.image_type==10) {   // Runlength encoded RGB images
		unsigned char red = 0,green = 0,blue = 0,alphabyte = 0,packetHeader = 0,packetSize = 0,j = 0;
		for (row = rows - 1; row >= 0; row--) {
			pixbuf = *out + ((targa_header.attributes & 0x20) ? rows-1-row : row) * columns * 4;
			for(column=0; column<columns; ) {
				packetHeader = *(byte *)tgabuf++;
				packetSize = 1 + (packetHeader & 0x7f);
				if (packetHeader & 0x80) {        // run-length packet
					switch (targa_header.pixel_size) {
						case 24:
								blue = *(byte *)tgabuf++;
								green = *(byte *)tgabuf++;
								red = *(byte *)tgabuf++;
								alphabyte = 255;
								break;
						case 32:
								blue = *(byte *)tgabuf++;
								green = *(byte *)tgabuf++;
								red = *(byte *)tgabuf++;
								alphabyte = *(byte *)tgabuf++;
								break;
					}
	
					for(j=0;j<packetSize;j++) {
						*pixbuf++=red;
						*pixbuf++=green;
						*pixbuf++=blue;
						*pixbuf++=alphabyte;
						column++;
						if (column==columns) { // run spans across rows
							column=0;
							if (row>0)
								row--;
							else
								goto breakOut;
							pixbuf = *out + row*columns*4;
						}
					}
				}
				else {                            // non run-length packet
					for(j=0;j<packetSize;j++) {
						switch (targa_header.pixel_size) {
							case 24:
									blue = *(byte *)tgabuf++;
									green = *(byte *)tgabuf++;
									red = *(byte *)tgabuf++;
									*pixbuf++ = red;
									*pixbuf++ = green;
									*pixbuf++ = blue;
									*pixbuf++ = 255;
									break;
							case 32:
									blue = *(byte *)tgabuf++;
									green = *(byte *)tgabuf++;
									red = *(byte *)tgabuf++;
									alphabyte = *(byte *)tgabuf++;
									*pixbuf++ = red;
									*pixbuf++ = green;
									*pixbuf++ = blue;
									*pixbuf++ = alphabyte;
									break;
						}
						column++;
						if (column==columns) { // pixel packet run spans across rows
							column=0;
							if (row>0)
								row--;
							else
								goto breakOut;
							pixbuf = *out + row*columns*4;
						}
					}
				}
			}
			breakOut:;
		}
	}
}

#else


// Definitions for image types
#define TGA_MAPPED		1	// Uncompressed, color-mapped images
#define TGA_MAPPED_RLE	9	// Runlength encoded color-mapped images
#define TGA_RGB			2	// Uncompressed, RGB images
#define TGA_RGB_RLE		10	// Runlength encoded RGB images
#define TGA_MONO		3	// Uncompressed, black and white images
#define TGA_MONO_RLE	11	// Compressed, black and white images

// Custom definitions to simplify code
#define MYTGA_MAPPED	80
#define MYTGA_RGB15		81
#define MYTGA_RGB24		82
#define MYTGA_RGB32		83
#define MYTGA_MONO8		84
#define MYTGA_MONO16	85

#define	IMAGE_MAX_DIMENSIONS	4096

typedef struct TGAHeader_s {
	byte			idLength, colormapType, imageType;
	unsigned short	colormapIndex, colormapLength;
	byte			colormapSize;
	unsigned short	xOrigin, yOrigin, width, height;
	byte			pixelSize, attributes;
} TGAHeader_t;

static void TGA_upsample15(byte *dest, byte *src, qbool alpha) {
	dest[2] = (byte) ((src[0] & 0x1F) << 3);
	dest[1] = (byte) ((((src[1] & 0x03) << 3) + ((src[0] & 0xE0) >> 5)) << 3);
	dest[0] = (byte) (((src[1] & 0x7C) >> 2) << 3);
	dest[3] = (alpha && !(src[1] & 0x80)) ? 0 : 255;
}

static void TGA_upsample24(byte *dest, byte *src) {
	dest[2] = src[0];
	dest[1] = src[1];
	dest[0] = src[2];
	dest[3] = 255;
}

static void TGA_upsample32(byte *dest, byte *src) {
	dest[2] = src[0];
	dest[1] = src[1];
	dest[0] = src[2];
	dest[3] = src[3];
}

#define TGA_ERROR(msg)	{if (msg) {Com_DPrintf((msg), COM_SkipPath(filename));} Q_free(fileBuffer); return NULL;}

static unsigned short BuffLittleShort(const byte *buffer) {
	return (buffer[1] << 8) | buffer[0];
}

byte *Image_LoadTGA(FILE *fin, char *filename, int matchwidth, int matchheight) {
	TGAHeader_t header;
	int i, x, y, bpp, alphabits, compressed, mytype, row_inc, runlen, readpixelcount;
	byte *fileBuffer, *in, *out, *data, *enddata, rgba[4], palette[256 * 4];

	if (!fin && FS_FOpenFile (filename, &fin) == -1)
		return NULL;

	fileBuffer = (byte *) Q_malloc(fs_filesize);
	fread(fileBuffer, 1, fs_filesize, fin);
	fclose(fin);

	if (fs_filesize < 19)
		TGA_ERROR(NULL);

	header.idLength = fileBuffer[0];
	header.colormapType = fileBuffer[1];
	header.imageType = fileBuffer[2];

	header.colormapIndex = BuffLittleShort(fileBuffer + 3);
	header.colormapLength = BuffLittleShort(fileBuffer + 5);
	header.colormapSize = fileBuffer[7];
	header.xOrigin = BuffLittleShort(fileBuffer + 8);
	header.yOrigin = BuffLittleShort(fileBuffer + 10);
	header.width = image_width = BuffLittleShort(fileBuffer + 12);
	header.height = image_height = BuffLittleShort(fileBuffer + 14);
	header.pixelSize = fileBuffer[16];
	header.attributes = fileBuffer[17];

	if (image_width > IMAGE_MAX_DIMENSIONS || image_height > IMAGE_MAX_DIMENSIONS || image_width <= 0 || image_height <= 0)
		TGA_ERROR(NULL);
	if ((matchwidth && image_width != matchwidth) || (matchheight && image_height != matchheight))
		TGA_ERROR(NULL);

	bpp = (header.pixelSize + 7) >> 3;
	alphabits = (header.attributes & 0x0F);
	compressed = (header.imageType & 0x08);

	in = fileBuffer + 18 + header.idLength;
	enddata = fileBuffer + fs_filesize;

	// error check the image type's pixel size
	if (header.imageType == TGA_RGB || header.imageType == TGA_RGB_RLE) {
		if (!(header.pixelSize == 15 || header.pixelSize == 16 || header.pixelSize == 24 || header.pixelSize == 32))
			TGA_ERROR("Unsupported TGA image %s: Bad pixel size for RGB image\n");
		mytype = (header.pixelSize == 24) ? MYTGA_RGB24 : (header.pixelSize == 32) ? MYTGA_RGB32 : MYTGA_RGB15;
	} else if (header.imageType == TGA_MAPPED || header.imageType == TGA_MAPPED_RLE) {
		if (header.pixelSize != 8)
			TGA_ERROR("Unsupported TGA image %s: Bad pixel size for color-mapped image.\n");
		if (!(header.colormapSize == 15 || header.colormapSize == 16 || header.colormapSize == 24 || header.colormapSize == 32))
			TGA_ERROR("Unsupported TGA image %s: Bad colormap size.\n");
		if (header.colormapType != 1 || header.colormapLength * 4 > sizeof(palette))
			TGA_ERROR("Unsupported TGA image %s: Bad colormap type and/or length for color-mapped image.\n");

		// read in the palette
		if (header.colormapSize == 15 || header.colormapSize == 16) {
			for (i = 0, out = palette; i < header.colormapLength; i++, in += 2, out += 4)
				TGA_upsample15(out, in, alphabits == 1);
		} else if (header.colormapSize == 24) {
			for (i = 0, out = palette; i < header.colormapLength; i++, in += 3, out += 4)
				TGA_upsample24(out, in);
		} else if (header.colormapSize == 32) {
			for (i = 0, out = palette; i < header.colormapLength; i++, in += 4, out += 4)
				TGA_upsample32(out, in);
		}
		mytype = MYTGA_MAPPED;
	} else if (header.imageType == TGA_MONO || header.imageType == TGA_MONO_RLE) {
		if (!(header.pixelSize == 8 || (header.pixelSize == 16 && alphabits == 8)))
			TGA_ERROR("Unsupported TGA image %s: Bad pixel size for grayscale image.\n");
		mytype = (header.pixelSize == 8) ? MYTGA_MONO8 : MYTGA_MONO16;
	} else {
		TGA_ERROR("Unsupported TGA image %s: Bad image type.\n");
	}

	if (header.attributes & 0x10)
		TGA_ERROR("Unsupported TGA image %s: Pixel data spans right to left.\n");

	data = (byte *) Q_malloc(image_width * image_height * 4);

	// if bit 5 of attributes isn't set, the image has been stored from bottom to top
	if ((header.attributes & 0x20)) {
		out = data;
		row_inc = 0;
	} else {
		out = data + (image_height - 1) * image_width * 4;
		row_inc = -image_width * 4 * 2;
	}

	x = y = 0;
	rgba[0] = rgba[1] = rgba[2] = rgba[3] = 255;

	while (y < image_height) {
		// decoder is mostly the same whether it's compressed or not
		readpixelcount = runlen = 0x7FFFFFFF;
		if (compressed && in < enddata) {
			runlen = *in++;
			// high bit indicates this is an RLE compressed run
			if (runlen & 0x80)
				readpixelcount = 1;
			runlen = 1 + (runlen & 0x7F);
		}

		while (runlen-- && y < image_height) {
			if (readpixelcount > 0) {
				readpixelcount--;
				rgba[0] = rgba[1] = rgba[2] = rgba[3] = 255;

				if (in + bpp <= enddata) {
					switch(mytype) {
					case MYTGA_MAPPED:
						for (i = 0; i < 4; i++)
							rgba[i] = palette[in[0] * 4 + i];
						break;
					case MYTGA_RGB15:
						TGA_upsample15(rgba, in, alphabits == 1);
						break;
					case MYTGA_RGB24:
						TGA_upsample24(rgba, in);
						break;
					case MYTGA_RGB32:
						TGA_upsample32(rgba, in);
						break;
					case MYTGA_MONO8:
						rgba[0] = rgba[1] = rgba[2] = in[0];
						break;
					case MYTGA_MONO16:
						rgba[0] = rgba[1] = rgba[2] = in[0];
						rgba[3] = in[1];
						break;
					}
					in += bpp;
				}
			}
			for (i = 0; i < 4; i++)
				*out++ = rgba[i];
			if (++x == image_width) {
				// end of line, advance to next
				x = 0;
				y++;
				out += row_inc;
			}
		}
	}

	Q_free(fileBuffer);
	return data;
}

void LoadTGA (char *filename, byte **out, int *width, int *height)
{
	byte *data;

	*out = NULL;

	data = Image_LoadTGA (NULL, filename, 0, 0);
	if (!data)
		return;

	*out = data;
	*width = image_width;
	*height = image_height;
}

#endif


/*
=================================================================

  PCX Loading

=================================================================
*/

typedef struct
{
    char	manufacturer;
    char	version;
    char	encoding;
    char	bits_per_pixel;
    unsigned short	xmin,ymin,xmax,ymax;
    unsigned short	hres,vres;
    unsigned char	palette[48];
    char	reserved;
    char	color_planes;
    unsigned short	bytes_per_line;
    unsigned short	palette_type;
    char	filler[58];
    unsigned char	data;			// unbounded
} pcx_t;

/*
============
LoadPCX
============
*/
void LoadPCX (char *filename, byte **pic, int *width, int *height)
{
	pcx_t	*pcx;
	byte	*pcxbuf, *out, *pix;
	int		x, y;
	int		dataByte, runLength;

	*pic = NULL;
	pcxbuf = FS_LoadTempFile (filename);
	if (!pcxbuf)
	{
		Com_DPrintf ("LoadPCX: Could not open %s\n", filename);
		return;
	}

//
// parse the PCX file
//
	pcx = (pcx_t *)pcxbuf;
	pcx->xmax = LittleShort (pcx->xmax);
	pcx->xmin = LittleShort (pcx->xmin);
	pcx->ymax = LittleShort (pcx->ymax);
	pcx->ymin = LittleShort (pcx->ymin);
	pcx->hres = LittleShort (pcx->hres);
	pcx->vres = LittleShort (pcx->vres);
	pcx->bytes_per_line = LittleShort (pcx->bytes_per_line);
	pcx->palette_type = LittleShort (pcx->palette_type);

	pix = &pcx->data;

	if (pcx->manufacturer != 0x0a
		|| pcx->version != 5
		|| pcx->encoding != 1
		|| pcx->bits_per_pixel != 8
		|| pcx->xmax >= 640
		|| pcx->ymax >= 480)
	{
		Com_DPrintf ("LoadPCX: Bad pcx file %s\n", filename);
		return;
	}

	if (width)
		*width = pcx->xmax+1;
	if (height)
		*height = pcx->ymax+1;

	*pic = out = Q_malloc ((pcx->xmax+1) * (pcx->ymax+1));

	for (y=0 ; y<=pcx->ymax ; y++, out += pcx->xmax+1)
	{
		for (x=0 ; x<=pcx->xmax ; )
		{
			if (pix - (byte *)pcx > fs_filesize) 
			{
				Q_free (*pic);
				*pic = NULL;
				Com_DPrintf ("LoadPCX: %s is malformed\n", filename);
				return;
			}

			dataByte = *pix++;

			if((dataByte & 0xC0) == 0xC0)
			{
				runLength = dataByte & 0x3F;
				if (pix - (byte *)pcx > fs_filesize) 
				{
					Q_free (*pic);
					*pic = NULL;
					Com_DPrintf ("LoadPCX: %s is malformed\n", filename);
					return;
				}
				dataByte = *pix++;
			}
			else
				runLength = 1;

			// sanity check
			if (runLength + x > pcx->xmax + 2)
			{
				Q_free (*pic);
				*pic = NULL;
				Com_DPrintf ("LoadPCX: %s is malformed\n", filename);
				return;
			}

			while (runLength-- > 0)
				out[x++] = dataByte;
		}
	}

	if (pix - (byte *)pcx > fs_filesize)
	{
		Q_free (*pic);
		*pic = NULL;
		Com_DPrintf ("LoadPCX: %s is malformed\n", filename);
	}
}

void WritePCX (byte *data, int width, int height, int rowbytes, byte *palette,	// [in]
				byte **pcxdata, int *pcxsize)									// [out]
{
	int		i, j;
	pcx_t	*pcx;
	byte	*pack;

	assert (pcxdata != NULL);
	assert (pcxsize != NULL);

	pcx = Hunk_TempAlloc (width*height*2+1000);
	if (!pcx) {
		Com_Printf ("WritePCX: not enough memory\n");
		*pcxdata = NULL;
		*pcxsize = 0;
		return;
	} 

	pcx->manufacturer = 0x0a;	// PCX id
	pcx->version = 5;			// 256 color
	pcx->encoding = 1;			// uncompressed
	pcx->bits_per_pixel = 8;	// 256 color
	pcx->xmin = 0;
	pcx->ymin = 0;
	pcx->xmax = LittleShort((short)(width-1));
	pcx->ymax = LittleShort((short)(height-1));
	pcx->hres = LittleShort((short)width);
	pcx->vres = LittleShort((short)height);
	memset (pcx->palette, 0, sizeof(pcx->palette));
	pcx->color_planes = 1;				// chunky image
	pcx->bytes_per_line = LittleShort((short)width);
	pcx->palette_type = LittleShort(2);	// not a grey scale
	memset (pcx->filler, 0, sizeof(pcx->filler));

	// pack the image
	pack = &pcx->data;

	for (i=0 ; i<height ; i++)
	{
		for (j=0 ; j<width ; j++)
		{
			if ( (*data & 0xc0) != 0xc0)
				*pack++ = *data++;
			else
			{
				*pack++ = 0xc1;
				*pack++ = *data++;
			}
		}
		data += rowbytes - width;
	}

	// write the palette
	*pack++ = 0x0c; // palette ID byte
	for (i=0 ; i<768 ; i++)
		*pack++ = *palette++;

	// fill results
	*pcxdata = (byte *) pcx;
	*pcxsize = pack - (byte *)pcx;
}

void Image_Init(void) {
#ifdef WITH_PNG
#ifndef WITH_PNG_STATIC
	if (PNG_LoadLibrary())
		QLib_RegisterModule(qlib_libpng, PNG_FreeLibrary);
#endif
//	Cvar_Register (&image_png_compression_level);
#endif

/*
#ifdef WITH_JPEG
#ifndef WITH_JPEG_STATIC
	if (JPEG_LoadLibrary())
		QLib_RegisterModule(qlib_libjpeg, JPEG_FreeLibrary);
#endif
	Cvar_Register (&image_jpeg_quality_level);
#endif
*/
}

/* vi: set noet ts=4 sts=4 ai sw=4: */
