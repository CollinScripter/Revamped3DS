#=================
# ZQuake Makefile
#=================

#==============================================================================
# Here are the targets:

.PHONY: default all server gl soft null

default: gl server soft
all: server gl soft null

#==============================================================================
# Architecture detection
#
# MACHINE = i686-linux-gnu, etc
# ARCH = mingw32 x86-linux ppc-linux x86-darwin ppc-darwin
# OS = windows linux darwin

MACHINE = $(shell $(CC) -dumpmachine)
ARCH = $(shell echo $(MACHINE) | sed -e 's/.*mingw32.*/mingw32/g' \
	-e 's/i.86/x86/g' -e 's/-gnu//' -e 's/powerpc/ppc/')
	# -e 's/\-.*//g' -

OS = $(shell echo $(ARCH) | sed -e 's/.*-//')
ifeq ($(OS),mingw32)
OS = windows
endif

#==============================================================================


CC = gcc


PRODUCT_DIR=release
GL_OBJ_DIR=release/gl
SOFT_OBJ_DIR=release/soft
SERVER_OBJ_DIR=release/server
NULL_OBJ_DIR=release/null


#------------------------------------------------------------------------------

CFLAGS = -DVWEP_TEST -DHALFLIFEBSP
CFLAGS += -Wall -Wno-format-y2k

# optimizations (should be only for release)
CFLAGS +=-ffast-math -fomit-frame-pointer -fexpensive-optimizations

ifeq ($(ARCH),mingw32)
	CFLAGS += -D_WIN32 -DMINGW32
endif
ifeq ($(OS),linux)
	CFLAGS += -DUSE_ALSA -DUSE_VMODE -DUSE_DGA
endif
ifeq ($(ARCH),ppc-linux)
	CFLAGS += -DBIGENDIAN
endif
ifeq ($(OS),darwin)
	CFLAGS += -DHAVE_STRLCPY -DHAVE_STRLCAT
endif
ifeq ($(ARCH),ppc-darwin)
	CFLAGS += -DBIGENDIAN
endif

SERVER_CFLAGS = -DSERVERONLY
GL_CFLAGS = -DGLQUAKE
SW_CFLAGS =
NULL_CFLAGS =

#------------------------------------------------------------------------------

LDFLAGS =
GL_LDFLAGS =
SW_LDFLAGS =
ifeq ($(ARCH),mingw32)
	LDFLAGS				+=-lws2_32 -luser32 -lwinmm -ldxguid -lgdi32
	GL_LDFLAGS			=-mwindows -lopengl32
	SW_LDFLAGS			=-mwindows -lddraw
endif
ifeq ($(OS),darwin)
	LDFLAGS				+=-framework "CoreAudio" -framework OpenGL
endif
ifeq ($(OS),linux)
	LDFLAGS				+=-lm -lGL -lXxf86vm -lXxf86dga
					# -L/usr/X11R6/lib -lX11 -lXext
endif

#==============================================================================

CLIENT_C_FILES = cl_cam cl_cmd cl_demo cl_draw cl_effects cl_ents cl_input \
	cl_main cl_nqdemo cl_parse cl_pred cl_sbar cl_screen cl_tent cl_view \
	console keys menu teamplay textencoding
GL_C_FILES = sv_save skin rc_wad rc_image rc_pixops \
	gl_draw gl_mesh gl_model gl_ngraph gl_ralias gl_refrag gl_rlight \
	gl_rmain gl_rmisc gl_rsprite gl_rsurf gl_texture gl_warp gl_sky
SW_C_FILES = sv_save skin rc_wad rc_image rc_pixops nonintel \
	d_edge d_fill d_init d_modech d_polyse d_sky d_sprite d_surf d_vars \
	d_zpoint r_aclip r_alias r_bsp r_draw r_edge r_efrag r_light r_main \
	r_misc r_model r_part r_rast r_scan r_sky r_sprite r_surf r_vars
SERVER_C_FILES = sv_bot sv_ccmds sv_ents sv_init sv_main sv_master \
	sv_move sv_nchan sv_phys sv_send sv_user sv_world \
	pr_cmds pr_edict pr_exec
COMMON_C_FILES = cmd cmodel com_msg com_mapcheck common crc cvar host mathlib mdfour \
	net_chan pmove pmovetst qlib q_shared version zone
NULL_C_FILES = sv_save rc_null vid_null snd_null cd_null in_null sys_null
ifeq ($(ARCH),mingw32)
ZQDS_PLATFORM_C_FILES = sys_win net_wins
ZQGL_PLATFORM_C_FILES = sys_win net_wins snd_dma snd_mem snd_mix snd_win cd_win in_win vid_wgl
ZQSW_PLATFORM_C_FILES = sys_win net_wins snd_dma snd_mem snd_mix snd_win cd_win in_win vid_ddraw
NULL_C_FILES += net_wins
else
ZQDS_PLATFORM_C_FILES = sv_sys_unix net_udp
ZQGL_PLATFORM_C_FILES = net_udp
ZQSW_PLATFORM_C_FILES = net_udp
NULL_C_FILES += net_udp
endif
ifeq ($(OS),darwin)
ZQGL_PLATFORM_C_FILES += snd_null cd_null
ZQSW_PLATFORM_C_FILES += snd_null cd_null
endif
ifeq ($(OS),linux)
ZQGL_PLATFORM_C_FILES += sys_linux cd_linux snd_dma snd_mem snd_mix snd_linux snd_oss snd_alsa vid_glx
ZQSW_PLATFORM_C_FILES += sys_linux cd_linux snd_dma snd_mem snd_mix snd_linux snd_oss snd_alsa vid_x
endif
ZQDS_C_FILES = $(SERVER_C_FILES) $(COMMON_C_FILES) $(ZQDS_PLATFORM_C_FILES) cl_null
ZQSW_C_FILES = $(CLIENT_C_FILES) $(ZQSW_PLATFORM_C_FILES) $(SW_C_FILES) $(SERVER_C_FILES) $(COMMON_C_FILES)
ZQGL_C_FILES = $(CLIENT_C_FILES) $(ZQGL_PLATFORM_C_FILES) $(GL_C_FILES) $(SERVER_C_FILES) $(COMMON_C_FILES)
ZQNULL_C_FILES = $(CLIENT_C_FILES) $(SERVER_C_FILES) $(COMMON_C_FILES) $(NULL_C_FILES)
ZQDS_C_OBJS = $(addprefix $(SERVER_OBJ_DIR)/, $(addsuffix .o, $(ZQDS_C_FILES)))
ZQGL_C_OBJS = $(addprefix $(GL_OBJ_DIR)/, $(addsuffix .o, $(ZQGL_C_FILES)))
ZQSW_C_OBJS = $(addprefix $(SOFT_OBJ_DIR)/, $(addsuffix .o, $(ZQSW_C_FILES)))
ZQNULL_C_OBJS = $(addprefix $(NULL_OBJ_DIR)/, $(addsuffix .o, $(ZQNULL_C_FILES)))

#==============================================================================

printvars:
	@echo "MACHINE       = $(MACHINE)"
	@echo "ARCH          = $(ARCH)"
	@echo "OS            = $(OS)"
	@echo ""
	@echo "PRODUCT_DIR   = $(PRODUCT_DIR)"
	@echo ""
	@echo "CFLAGS        = $(CFLAGS)"
	@echo "LDFLAGS       = $(LDFLAGS)"

#.PHONY: server
#server:
#	@echo [MAKE] server
#	@make server_do
#server_do: $(PRODUCT_DIR)/zqds
server: $(PRODUCT_DIR)/zqds
$(PRODUCT_DIR)/zqds: $(ZQDS_C_OBJS)
	@echo [LINK] $@
	@$(CC) -o $@ $(ZQDS_C_OBJS) $(LDFLAGS)
$(ZQDS_C_OBJS): $(SERVER_OBJ_DIR)/%.o: %.c
	@-mkdir -p $(SERVER_OBJ_DIR)
	@echo [CC] $<
	@$(CC) $(CFLAGS) $(SERVER_CFLAGS) -c -o $@ $<
#------------------------------------------------------------------------------
gl: $(PRODUCT_DIR)/zquake-gl
$(PRODUCT_DIR)/zquake-gl: $(ZQGL_C_OBJS)
	@echo [LINK] $@
	@$(CC) -o $@ $(ZQGL_C_OBJS) $(LDFLAGS) $(GL_LDFLAGS)
$(ZQGL_C_OBJS): $(GL_OBJ_DIR)/%.o: %.c
	@-mkdir -p $(GL_OBJ_DIR)
	@echo [CC] $<
	@$(CC) $(CFLAGS) $(GL_CFLAGS) -c -o $@ $<
#------------------------------------------------------------------------------
soft: $(PRODUCT_DIR)/zquake
$(PRODUCT_DIR)/zquake: $(ZQSW_C_OBJS)
	@echo [LINK] $@
	@$(CC) -o $@ $(ZQSW_C_OBJS) $(LDFLAGS) $(SW_LDFLAGS)
$(ZQSW_C_OBJS): $(SOFT_OBJ_DIR)/%.o: %.c
	@-mkdir -p $(SOFT_OBJ_DIR)
	@echo [CC] $<
	@$(CC) $(CFLAGS) $(SW_CFLAGS) -c -o $@ $<
#------------------------------------------------------------------------------
null: $(PRODUCT_DIR)/zquake-null
$(PRODUCT_DIR)/zquake-null: $(ZQNULL_C_OBJS)
	@echo [LINK] $@
	@$(CC) -o $@ $(ZQNULL_C_OBJS) $(LDFLAGS)
$(ZQNULL_C_OBJS): $(NULL_OBJ_DIR)/%.o: %.c
	@-mkdir -p $(NULL_OBJ_DIR)
	@echo [CC] $<
	@$(CC) $(CFLAGS) $(NULL_CFLAGS) -c -o $@ $<
#------------------------------------------------------------------------------
clean:
	@echo [CLEAN]
	@-rm $(SERVER_OBJ_DIR)/*.o $(SOFT_OBJ_DIR)/*.o $(GL_OBJ_DIR)/*.o $(NULL_OBJ_DIR)/*.o 2>/dev/null
	@-rmdir $(SERVER_OBJ_DIR) $(SOFT_OBJ_DIR) $(GL_OBJ_DIR) $(NULL_OBJ_DIR) 2>/dev/null
	@-rm $(PRODUCT_DIR)/zqds $(PRODUCT_DIR)/zquake $(PRODUCT_DIR)/zquake-gl $(PRODUCT_DIR)/zquake-null 2>/dev/null
	@-rm $(PRODUCT_DIR) 2>/dev/null

#==============================================================================
