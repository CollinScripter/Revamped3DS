# Microsoft Developer Studio Project File - Name="enginez" - Package Owner=<4>
# Microsoft Developer Studio Generated Build File, Format Version 6.00
# ** DO NOT EDIT **

# TARGTYPE "Win32 (x86) Application" 0x0101

CFG=enginez - Win32 GLDebug
!MESSAGE This is not a valid makefile. To build this project using NMAKE,
!MESSAGE use the Export Makefile command and run
!MESSAGE 
!MESSAGE NMAKE /f "enginez.mak".
!MESSAGE 
!MESSAGE You can specify a configuration when running NMAKE
!MESSAGE by defining the macro CFG on the command line. For example:
!MESSAGE 
!MESSAGE NMAKE /f "enginez.mak" CFG="enginez - Win32 GLDebug"
!MESSAGE 
!MESSAGE Possible choices for configuration are:
!MESSAGE 
!MESSAGE "enginez - Win32 GLDebug" (based on "Win32 (x86) Application")
!MESSAGE "enginez - Win32 Release" (based on "Win32 (x86) Application")
!MESSAGE "enginez - Win32 GLRelease" (based on "Win32 (x86) Application")
!MESSAGE "enginez - Win32 Debug" (based on "Win32 (x86) Application")
!MESSAGE 

# Begin Project
# PROP AllowPerConfigDependencies 0
# PROP Scc_ProjName ""
# PROP Scc_LocalPath ""
CPP=cl.exe
MTL=midl.exe
RSC=rc.exe

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP BASE Use_MFC 0
# PROP BASE Use_Debug_Libraries 1
# PROP BASE Output_Dir ".\Debug-gl"
# PROP BASE Intermediate_Dir ".\Debug-gl"
# PROP BASE Target_Dir ""
# PROP Use_MFC 0
# PROP Use_Debug_Libraries 1
# PROP Output_Dir ".\Debug-gl"
# PROP Intermediate_Dir ".\Debug-gl"
# PROP Target_Dir ""
# ADD BASE CPP /nologo /G6 /ML /W3 /WX /GX /ZI /Od /D "WIN32" /D "_DEBUG" /D "_WINDOWS" /D "id386" /D "GLQUAKE" /D "WITH_JPEG" /D "WITH_PNG" /D "WITH_ZLIB" /GZ PRECOMP_VC7_TOBEREMOVED /c
# ADD CPP /nologo /G6 /ML /W3 /WX /GX /ZI /Od /D "WIN32" /D "_DEBUG" /D "_WINDOWS" /D "id386" /D "GLQUAKE" /D "WITH_JPEG" /D "WITH_PNG" /D "WITH_ZLIB" /GZ PRECOMP_VC7_TOBEREMOVED /c
# ADD BASE MTL /nologo /D "_DEBUG" /mktyplib203 /win32
# ADD MTL /nologo /D "_DEBUG" /mktyplib203 /win32
# ADD BASE RSC /l 0xc09 /d "_DEBUG"
# ADD RSC /l 0xc09 /d "_DEBUG"
BSC32=bscmake.exe
# ADD BASE BSC32 /nologo
# ADD BSC32 /nologo
LINK32=link.exe
# ADD BASE LINK32 kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib dxguid.lib opengl32.lib wsock32.lib winmm.lib /nologo /subsystem:windows /debug /machine:I386 /out:"$(Outdir)\enginez-gl.exe" /pdbtype:sept
# SUBTRACT BASE LINK32 /pdb:none
# ADD LINK32 kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib dxguid.lib opengl32.lib wsock32.lib winmm.lib /nologo /subsystem:windows /debug /machine:I386 /out:"$(Outdir)\enginez-gl.exe" /pdbtype:sept
# SUBTRACT LINK32 /pdb:none

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

# PROP BASE Use_MFC 0
# PROP BASE Use_Debug_Libraries 0
# PROP BASE Output_Dir ".\Release"
# PROP BASE Intermediate_Dir ".\Release"
# PROP BASE Target_Dir ""
# PROP Use_MFC 0
# PROP Use_Debug_Libraries 0
# PROP Output_Dir ".\Release"
# PROP Intermediate_Dir ".\Release"
# PROP Target_Dir ""
# ADD BASE CPP /nologo /G6 /W3 /WX /GX /Oi /Oy /Ob2 /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "id386" /D "WITH_PNG" /D "WITH_ZLIB" /GF PRECOMP_VC7_TOBEREMOVED /c
# ADD CPP /nologo /G6 /W3 /WX /GX /Oi /Oy /Ob2 /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "id386" /D "WITH_PNG" /D "WITH_ZLIB" /GF PRECOMP_VC7_TOBEREMOVED /c
# ADD BASE MTL /nologo /D "NDEBUG" /mktyplib203 /win32
# ADD MTL /nologo /D "NDEBUG" /mktyplib203 /win32
# ADD BASE RSC /l 0xc09 /d "NDEBUG"
# ADD RSC /l 0xc09 /d "NDEBUG"
BSC32=bscmake.exe
# ADD BASE BSC32 /nologo
# ADD BSC32 /nologo
LINK32=link.exe
# ADD BASE LINK32 kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib mgllt.lib dxguid.lib wsock32.lib winmm.lib /nologo /subsystem:windows /machine:I386 /nodefaultlib:"libcmt" /out:"$(Outdir)\enginez.exe" /pdbtype:sept /release
# SUBTRACT BASE LINK32 /pdb:none
# ADD LINK32 kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib mgllt.lib dxguid.lib wsock32.lib winmm.lib /nologo /subsystem:windows /machine:I386 /nodefaultlib:"libcmt" /out:"$(Outdir)\enginez.exe" /pdbtype:sept /release
# SUBTRACT LINK32 /pdb:none

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP BASE Use_MFC 0
# PROP BASE Use_Debug_Libraries 0
# PROP BASE Output_Dir ".\Release-gl"
# PROP BASE Intermediate_Dir ".\Release-gl"
# PROP BASE Target_Dir ""
# PROP Use_MFC 0
# PROP Use_Debug_Libraries 0
# PROP Output_Dir ".\Release-gl"
# PROP Intermediate_Dir ".\Release-gl"
# PROP Ignore_Export_Lib 0
# PROP Target_Dir ""
# ADD BASE CPP /nologo /G6 /W3 /WX /GX /Ot /Og /Oi /Oy /Ob2 /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "id386" /D "GLQUAKE" /D "WITH_JPEG" /D "WITH_PNG" /D "WITH_ZLIB" /GF PRECOMP_VC7_TOBEREMOVED /c
# ADD CPP /nologo /G6 /W3 /WX /GX /O2 /Ob2 /D "_WIN32" /D "NDEBUG" /D "_WINDOWS" /D "id386" /D "GLQUAKE" /FR /GF /c
# ADD BASE MTL /nologo /D "_DEBUG" /mktyplib203 /win32
# ADD MTL /nologo /D "_DEBUG" /mktyplib203 /win32
# ADD BASE RSC /l 0xc09 /d "_DEBUG"
# ADD RSC /l 0xc09 /d "_DEBUG"
BSC32=bscmake.exe
# ADD BASE BSC32 /nologo
# ADD BSC32 /nologo
LINK32=link.exe
# ADD BASE LINK32 kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib dxguid.lib opengl32.lib wsock32.lib winmm.lib /nologo /subsystem:windows /machine:I386 /out:"$(Outdir)\enginez-gl.exe" /pdbtype:sept /release
# SUBTRACT BASE LINK32 /pdb:none
# ADD LINK32 kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib dxguid.lib opengl32.lib wsock32.lib winmm.lib /nologo /subsystem:windows /map /machine:I386 /out:"e:\kurokx\enginez.exe" /pdbtype:sept /release
# SUBTRACT LINK32 /pdb:none

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

# PROP BASE Use_MFC 0
# PROP BASE Use_Debug_Libraries 1
# PROP BASE Output_Dir ".\Debug"
# PROP BASE Intermediate_Dir ".\Debug"
# PROP BASE Target_Dir ""
# PROP Use_MFC 0
# PROP Use_Debug_Libraries 1
# PROP Output_Dir ".\Debug"
# PROP Intermediate_Dir ".\Debug"
# PROP Target_Dir ""
# ADD BASE CPP /nologo /G6 /ML /W3 /WX /GX /ZI /Od /D "WIN32" /D "_DEBUG" /D "_WINDOWS" /D "id386" /D "WITH_PNG" /D "WITH_ZLIB" /GZ PRECOMP_VC7_TOBEREMOVED /c
# ADD CPP /nologo /G6 /ML /W3 /WX /GX /ZI /Od /D "WIN32" /D "_DEBUG" /D "_WINDOWS" /D "id386" /D "WITH_PNG" /D "WITH_ZLIB" /GZ PRECOMP_VC7_TOBEREMOVED /c
# ADD BASE MTL /nologo /D "_DEBUG" /mktyplib203 /win32
# ADD MTL /nologo /D "_DEBUG" /mktyplib203 /win32
# ADD BASE RSC /l 0xc09 /d "_DEBUG"
# ADD RSC /l 0xc09 /d "_DEBUG"
BSC32=bscmake.exe
# ADD BASE BSC32 /nologo
# ADD BSC32 /nologo
LINK32=link.exe
# ADD BASE LINK32 kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib mgllt.lib dxguid.lib wsock32.lib winmm.lib /nologo /subsystem:windows /debug /machine:I386 /nodefaultlib:"libcmt" /out:"$(Outdir)\enginez.exe" /pdbtype:sept
# SUBTRACT BASE LINK32 /pdb:none
# ADD LINK32 kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib mgllt.lib dxguid.lib wsock32.lib winmm.lib /nologo /subsystem:windows /debug /machine:I386 /nodefaultlib:"libcmt" /out:"$(Outdir)\enginez.exe" /pdbtype:sept
# SUBTRACT LINK32 /pdb:none

!ENDIF 

# Begin Target

# Name "enginez - Win32 GLDebug"
# Name "enginez - Win32 Release"
# Name "enginez - Win32 GLRelease"
# Name "enginez - Win32 Debug"
# Begin Group "Source Files"

# PROP Default_Filter "cpp;c;cxx;rc;def;r;odl;hpj;bat;for;f90"
# Begin Group "ref. GL"

# PROP Default_Filter "cpp;c;cxx;rc;def;r;odl;hpj;bat;for;f90"
# Begin Source File

SOURCE=.\gl_draw.c
DEP_CPP_GL_DR=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmdlib.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\crc.h"\
	".\cvar.h"\
	".\draw.h"\
	".\gl_local.h"\
	".\gl_model.h"\
	".\gl_texture.h"\
	".\mathlib.h"\
	".\modelgen.h"\
	".\net.h"\
	".\pmove.h"\
	".\png.h"\
	".\pngconf.h"\
	".\pr_comp.h"\
	".\progsint.h"\
	".\progslib.h"\
	".\progtype.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\rc_image.h"\
	".\rc_wad.h"\
	".\render.h"\
	".\spritegn.h"\
	".\sys.h"\
	".\vid.h"\
	".\zconf.h"\
	".\zlib.h"\
	".\zone.h"\
	
NODEP_CPP_GL_DR=\
	".\config.h"\
	".\dictlib.h"\
	".\lbmlib.h"\
	".\pngusr.h"\
	".\qcd.h"\
	".\scriplib.h"\
	".\trilib.h"\
	

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# SUBTRACT CPP /WX

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\gl_mesh.c
DEP_CPP_GL_ME=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmdlib.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\gl_local.h"\
	".\gl_model.h"\
	".\gl_texture.h"\
	".\mathlib.h"\
	".\modelgen.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progsint.h"\
	".\progslib.h"\
	".\progtype.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\spritegn.h"\
	".\sys.h"\
	".\vid.h"\
	".\zone.h"\
	
NODEP_CPP_GL_ME=\
	".\dictlib.h"\
	".\lbmlib.h"\
	".\qcd.h"\
	".\scriplib.h"\
	".\trilib.h"\
	

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# SUBTRACT CPP /WX

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\gl_model.c
DEP_CPP_GL_MO=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmdlib.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\crc.h"\
	".\cvar.h"\
	".\draw.h"\
	".\gl_local.h"\
	".\gl_model.h"\
	".\gl_texture.h"\
	".\mathlib.h"\
	".\modelgen.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progsint.h"\
	".\progslib.h"\
	".\progtype.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\rc_wad.h"\
	".\render.h"\
	".\spritegn.h"\
	".\sys.h"\
	".\vid.h"\
	".\zone.h"\
	
NODEP_CPP_GL_MO=\
	".\dictlib.h"\
	".\lbmlib.h"\
	".\qcd.h"\
	".\scriplib.h"\
	".\trilib.h"\
	
# End Source File
# Begin Source File

SOURCE=.\gl_ngraph.c
DEP_CPP_GL_NG=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmdlib.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\gl_local.h"\
	".\gl_model.h"\
	".\gl_texture.h"\
	".\mathlib.h"\
	".\modelgen.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progsint.h"\
	".\progslib.h"\
	".\progtype.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\spritegn.h"\
	".\sys.h"\
	".\vid.h"\
	".\zone.h"\
	
NODEP_CPP_GL_NG=\
	".\dictlib.h"\
	".\lbmlib.h"\
	".\qcd.h"\
	".\scriplib.h"\
	".\trilib.h"\
	
# End Source File
# Begin Source File

SOURCE=.\gl_ralias.c
DEP_CPP_GL_RA=\
	".\anorm_dots.h"\
	".\anorms.h"\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmdlib.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\gl_local.h"\
	".\gl_model.h"\
	".\gl_texture.h"\
	".\mathlib.h"\
	".\modelgen.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progsint.h"\
	".\progslib.h"\
	".\progtype.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\spritegn.h"\
	".\sys.h"\
	".\vid.h"\
	".\zone.h"\
	
NODEP_CPP_GL_RA=\
	".\dictlib.h"\
	".\lbmlib.h"\
	".\qcd.h"\
	".\scriplib.h"\
	".\trilib.h"\
	
# End Source File
# Begin Source File

SOURCE=.\gl_refrag.c
DEP_CPP_GL_RE=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmdlib.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\gl_local.h"\
	".\gl_model.h"\
	".\gl_texture.h"\
	".\mathlib.h"\
	".\modelgen.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progsint.h"\
	".\progslib.h"\
	".\progtype.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\spritegn.h"\
	".\sys.h"\
	".\vid.h"\
	".\zone.h"\
	
NODEP_CPP_GL_RE=\
	".\dictlib.h"\
	".\lbmlib.h"\
	".\qcd.h"\
	".\scriplib.h"\
	".\trilib.h"\
	
# End Source File
# Begin Source File

SOURCE=.\gl_rlight.c
DEP_CPP_GL_RL=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmdlib.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\gl_local.h"\
	".\gl_model.h"\
	".\gl_texture.h"\
	".\mathlib.h"\
	".\modelgen.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progsint.h"\
	".\progslib.h"\
	".\progtype.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\spritegn.h"\
	".\sys.h"\
	".\vid.h"\
	".\zone.h"\
	
NODEP_CPP_GL_RL=\
	".\dictlib.h"\
	".\lbmlib.h"\
	".\qcd.h"\
	".\scriplib.h"\
	".\trilib.h"\
	
# End Source File
# Begin Source File

SOURCE=.\gl_rmain.c
DEP_CPP_GL_RM=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmdlib.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\gl_local.h"\
	".\gl_model.h"\
	".\gl_texture.h"\
	".\mathlib.h"\
	".\modelgen.h"\
	".\net.h"\
	".\pmove.h"\
	".\png.h"\
	".\pngconf.h"\
	".\pr_comp.h"\
	".\progsint.h"\
	".\progslib.h"\
	".\progtype.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\qlib.h"\
	".\quakedef.h"\
	".\rc_image.h"\
	".\render.h"\
	".\sound.h"\
	".\spritegn.h"\
	".\sys.h"\
	".\vid.h"\
	".\zconf.h"\
	".\zlib.h"\
	".\zone.h"\
	
NODEP_CPP_GL_RM=\
	".\config.h"\
	".\dictlib.h"\
	".\lbmlib.h"\
	".\pngusr.h"\
	".\qcd.h"\
	".\scriplib.h"\
	".\trilib.h"\
	
# End Source File
# Begin Source File

SOURCE=.\gl_rmisc.c
DEP_CPP_GL_RMI=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmdlib.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\gl_local.h"\
	".\gl_model.h"\
	".\gl_texture.h"\
	".\mathlib.h"\
	".\modelgen.h"\
	".\net.h"\
	".\pmove.h"\
	".\png.h"\
	".\pngconf.h"\
	".\pr_comp.h"\
	".\progsint.h"\
	".\progslib.h"\
	".\progtype.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\rc_image.h"\
	".\render.h"\
	".\spritegn.h"\
	".\sys.h"\
	".\vid.h"\
	".\zconf.h"\
	".\zlib.h"\
	".\zone.h"\
	
NODEP_CPP_GL_RMI=\
	".\config.h"\
	".\dictlib.h"\
	".\lbmlib.h"\
	".\pngusr.h"\
	".\qcd.h"\
	".\scriplib.h"\
	".\trilib.h"\
	
# End Source File
# Begin Source File

SOURCE=.\gl_rsprite.c
DEP_CPP_GL_RS=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmdlib.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\gl_local.h"\
	".\gl_model.h"\
	".\gl_texture.h"\
	".\mathlib.h"\
	".\modelgen.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progsint.h"\
	".\progslib.h"\
	".\progtype.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\spritegn.h"\
	".\sys.h"\
	".\vid.h"\
	".\zone.h"\
	
NODEP_CPP_GL_RS=\
	".\dictlib.h"\
	".\lbmlib.h"\
	".\qcd.h"\
	".\scriplib.h"\
	".\trilib.h"\
	
# End Source File
# Begin Source File

SOURCE=.\gl_rsurf.c
DEP_CPP_GL_RSU=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmdlib.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\gl_local.h"\
	".\gl_model.h"\
	".\gl_texture.h"\
	".\mathlib.h"\
	".\modelgen.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progsint.h"\
	".\progslib.h"\
	".\progtype.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\spritegn.h"\
	".\sys.h"\
	".\vid.h"\
	".\zone.h"\
	
NODEP_CPP_GL_RSU=\
	".\dictlib.h"\
	".\lbmlib.h"\
	".\qcd.h"\
	".\scriplib.h"\
	".\trilib.h"\
	
# End Source File
# Begin Source File

SOURCE=.\gl_sky.c
DEP_CPP_GL_SK=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmdlib.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\gl_local.h"\
	".\gl_model.h"\
	".\gl_texture.h"\
	".\mathlib.h"\
	".\modelgen.h"\
	".\net.h"\
	".\pmove.h"\
	".\png.h"\
	".\pngconf.h"\
	".\pr_comp.h"\
	".\progsint.h"\
	".\progslib.h"\
	".\progtype.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\rc_image.h"\
	".\render.h"\
	".\spritegn.h"\
	".\sys.h"\
	".\vid.h"\
	".\zconf.h"\
	".\zlib.h"\
	".\zone.h"\
	
NODEP_CPP_GL_SK=\
	".\config.h"\
	".\dictlib.h"\
	".\lbmlib.h"\
	".\pngusr.h"\
	".\qcd.h"\
	".\scriplib.h"\
	".\trilib.h"\
	
# End Source File
# Begin Source File

SOURCE=.\gl_texture.c
DEP_CPP_GL_TE=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmdlib.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\crc.h"\
	".\cvar.h"\
	".\draw.h"\
	".\gl_local.h"\
	".\gl_model.h"\
	".\gl_texture.h"\
	".\mathlib.h"\
	".\modelgen.h"\
	".\net.h"\
	".\pmove.h"\
	".\png.h"\
	".\pngconf.h"\
	".\pr_comp.h"\
	".\progsint.h"\
	".\progslib.h"\
	".\progtype.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\rc_image.h"\
	".\rc_pixops.h"\
	".\render.h"\
	".\spritegn.h"\
	".\sys.h"\
	".\version.h"\
	".\vid.h"\
	".\zconf.h"\
	".\zlib.h"\
	".\zone.h"\
	
NODEP_CPP_GL_TE=\
	".\config.h"\
	".\dictlib.h"\
	".\lbmlib.h"\
	".\pngusr.h"\
	".\qcd.h"\
	".\scriplib.h"\
	".\trilib.h"\
	
# End Source File
# Begin Source File

SOURCE=.\gl_warp.c
DEP_CPP_GL_WA=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmdlib.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\gl_local.h"\
	".\gl_model.h"\
	".\gl_texture.h"\
	".\gl_warp_sin.h"\
	".\mathlib.h"\
	".\modelgen.h"\
	".\net.h"\
	".\pmove.h"\
	".\png.h"\
	".\pngconf.h"\
	".\pr_comp.h"\
	".\progsint.h"\
	".\progslib.h"\
	".\progtype.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\rc_image.h"\
	".\render.h"\
	".\spritegn.h"\
	".\sys.h"\
	".\vid.h"\
	".\zconf.h"\
	".\zlib.h"\
	".\zone.h"\
	
NODEP_CPP_GL_WA=\
	".\config.h"\
	".\dictlib.h"\
	".\lbmlib.h"\
	".\pngusr.h"\
	".\qcd.h"\
	".\scriplib.h"\
	".\trilib.h"\
	
# End Source File
# Begin Source File

SOURCE=.\qlib.c
DEP_CPP_QLIB_=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\qlib.h"\
	".\quakedef.h"\
	".\render.h"\
	".\sys.h"\
	".\vid.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\vid_wgl.c
DEP_CPP_VID_W=\
	".\bspfile.h"\
	".\cdaudio.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmdlib.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\gl_local.h"\
	".\gl_model.h"\
	".\gl_texture.h"\
	".\keys.h"\
	".\mathlib.h"\
	".\modelgen.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progsint.h"\
	".\progslib.h"\
	".\progtype.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\sound.h"\
	".\spritegn.h"\
	".\sys.h"\
	".\vid.h"\
	".\winquake.h"\
	".\zone.h"\
	
NODEP_CPP_VID_W=\
	".\dictlib.h"\
	".\lbmlib.h"\
	".\qcd.h"\
	".\scriplib.h"\
	".\trilib.h"\
	
# End Source File
# End Group
# Begin Group "Server"

# PROP Default_Filter "cpp;c;cxx;rc;def;r;odl;hpj;bat;for;f90"
# Begin Source File

SOURCE=.\pr_cmds.c
DEP_CPP_PR_CM=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progdefs.h"\
	".\progs.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\server.h"\
	".\sv_world.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\pr_edict.c
DEP_CPP_PR_ED=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\crc.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progdefs.h"\
	".\progs.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\server.h"\
	".\sv_world.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\pr_exec.c
DEP_CPP_PR_EX=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progdefs.h"\
	".\progs.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\server.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\sv_bot.c
DEP_CPP_SV_BO=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progdefs.h"\
	".\progs.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\server.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\sv_ccmds.c
DEP_CPP_SV_CC=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progdefs.h"\
	".\progs.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\server.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\sv_ents.c
DEP_CPP_SV_EN=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progdefs.h"\
	".\progs.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\server.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\sv_init.c
DEP_CPP_SV_IN=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\crc.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progdefs.h"\
	".\progs.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\server.h"\
	".\sv_world.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\sv_main.c
DEP_CPP_SV_MA=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progdefs.h"\
	".\progs.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\server.h"\
	".\sys.h"\
	".\version.h"\
	".\zone.h"\
	
NODEP_CPP_SV_MA=\
	".\sv_authlists.h"\
	
# End Source File
# Begin Source File

SOURCE=.\sv_master.c
DEP_CPP_SV_MAS=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progdefs.h"\
	".\progs.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\server.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\sv_move.c
DEP_CPP_SV_MO=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progdefs.h"\
	".\progs.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\server.h"\
	".\sv_world.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\sv_nchan.c
DEP_CPP_SV_NC=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progdefs.h"\
	".\progs.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\server.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\sv_phys.c
DEP_CPP_SV_PH=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progdefs.h"\
	".\progs.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\server.h"\
	".\sv_world.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=sv_save.c
DEP_CPP_SV_SA=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progdefs.h"\
	".\progs.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\server.h"\
	".\sv_world.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\sv_send.c
DEP_CPP_SV_SE=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progdefs.h"\
	".\progs.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\server.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\sv_user.c
DEP_CPP_SV_US=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progdefs.h"\
	".\progs.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\server.h"\
	".\sv_world.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\sv_world.c
DEP_CPP_SV_WO=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progdefs.h"\
	".\progs.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\server.h"\
	".\sv_world.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# End Group
# Begin Group "Common"

# PROP Default_Filter "cpp;c;cxx;rc;def;r;odl;hpj;bat;for;f90"
# Begin Source File

SOURCE=.\cmd.c
DEP_CPP_CMD_C=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\cmodel.c
DEP_CPP_CMODE=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\com_mapcheck.c
DEP_CPP_COM_M=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=com_msg.c
DEP_CPP_COM_MS=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\common.c
DEP_CPP_COMMO=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\crc.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\mdfour.h"\
	".\net.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\crc.c
DEP_CPP_CRC_C=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\crc.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\cvar.c
DEP_CPP_CVAR_=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\host.c
DEP_CPP_HOST_=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\sys.h"\
	".\version.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\mathlib.c
DEP_CPP_MATHL=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\mdfour.c
DEP_CPP_MDFOU=\
	".\mdfour.h"\
	
# End Source File
# Begin Source File

SOURCE=.\net_chan.c
DEP_CPP_NET_C=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\sys.h"\
	".\winquake.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\net_wins.c
DEP_CPP_NET_W=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\sys.h"\
	".\winquake.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\nonintel.c
DEP_CPP_NONIN=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\pmove.c
DEP_CPP_PMOVE=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\pmovetst.c
DEP_CPP_PMOVET=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\q_shared.c
DEP_CPP_Q_SHA=\
	".\mathlib.h"\
	".\q_shared.h"\
	".\sys.h"\
	
# End Source File
# Begin Source File

SOURCE=.\sys_win.c
DEP_CPP_SYS_W=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\sys.h"\
	".\vid.h"\
	".\winquake.h"\
	".\zone.h"\
	

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# SUBTRACT CPP /WX

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\version.c
DEP_CPP_VERSI=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\sys.h"\
	".\version.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\zone.c
DEP_CPP_ZONE_=\
	".\bspfile.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# End Group
# Begin Group "Draw"

# PROP Default_Filter ""
# Begin Source File

SOURCE=.\r_aclip.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\r_alias.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\r_bsp.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\r_draw.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\r_edge.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\r_efrag.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\r_light.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\r_main.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\r_misc.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\r_model.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\r_part.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\r_rast.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\r_sky.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\r_sprite.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\r_surf.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\r_vars.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# End Group
# Begin Group "Software"

# PROP Default_Filter ""
# Begin Source File

SOURCE=.\d_edge.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\d_fill.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\d_init.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\d_modech.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\d_polyse.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\d_scan.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\d_sky.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\d_sprite.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\d_surf.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\d_vars.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\d_zpoint.c

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# End Group
# Begin Group "Client"

# PROP Default_Filter "cpp;c;cxx;rc;def;r;odl;hpj;bat;for;f90"
# Begin Source File

SOURCE=.\cd_win.c
DEP_CPP_CD_WI=\
	".\bspfile.h"\
	".\cdaudio.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\cvar.h"\
	".\mathlib.h"\
	".\net.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\sys.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\cl_cam.c
DEP_CPP_CL_CA=\
	".\bspfile.h"\
	".\cl_sbar.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\sys.h"\
	".\teamplay.h"\
	".\vid.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\cl_cmd.c
DEP_CPP_CL_CM=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\mathlib.h"\
	".\menu.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\sound.h"\
	".\sys.h"\
	".\teamplay.h"\
	".\version.h"\
	".\vid.h"\
	".\winquake.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\cl_demo.c
DEP_CPP_CL_DE=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\sys.h"\
	".\teamplay.h"\
	".\vid.h"\
	".\winquake.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\cl_draw.c
DEP_CPP_CL_DR=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\sys.h"\
	".\vid.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\cl_effects.c
DEP_CPP_CL_EF=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\sys.h"\
	".\vid.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\cl_ents.c
DEP_CPP_CL_EN=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\sys.h"\
	".\teamplay.h"\
	".\vid.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\cl_input.c
DEP_CPP_CL_IN=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\input.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\sys.h"\
	".\vid.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\cl_main.c
DEP_CPP_CL_MA=\
	".\bspfile.h"\
	".\cdaudio.h"\
	".\cl_sbar.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\input.h"\
	".\keys.h"\
	".\mathlib.h"\
	".\menu.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\sound.h"\
	".\sys.h"\
	".\teamplay.h"\
	".\version.h"\
	".\vid.h"\
	".\winquake.h"\
	".\zone.h"\
	

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# SUBTRACT CPP /WX

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\cl_nqdemo.c
DEP_CPP_CL_NQ=\
	".\bspfile.h"\
	".\cdaudio.h"\
	".\cl_sbar.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\sound.h"\
	".\sys.h"\
	".\vid.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\cl_parse.c
DEP_CPP_CL_PA=\
	".\bspfile.h"\
	".\cdaudio.h"\
	".\cl_sbar.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\sound.h"\
	".\sys.h"\
	".\teamplay.h"\
	".\textencoding.h"\
	".\version.h"\
	".\vid.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\cl_pred.c
DEP_CPP_CL_PR=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\sys.h"\
	".\vid.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\cl_sbar.c
DEP_CPP_CL_SB=\
	".\bspfile.h"\
	".\cl_sbar.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\sys.h"\
	".\vid.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\cl_screen.c
DEP_CPP_CL_SC=\
	".\bspfile.h"\
	".\cl_sbar.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmdlib.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\d_iface.h"\
	".\draw.h"\
	".\gl_local.h"\
	".\gl_model.h"\
	".\gl_texture.h"\
	".\keys.h"\
	".\mathlib.h"\
	".\menu.h"\
	".\modelgen.h"\
	".\net.h"\
	".\pmove.h"\
	".\png.h"\
	".\pngconf.h"\
	".\pr_comp.h"\
	".\progsint.h"\
	".\progslib.h"\
	".\progtype.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\r_local.h"\
	".\r_model.h"\
	".\r_shared.h"\
	".\rc_image.h"\
	".\render.h"\
	".\sound.h"\
	".\spritegn.h"\
	".\sys.h"\
	".\version.h"\
	".\vid.h"\
	".\zconf.h"\
	".\zlib.h"\
	".\zone.h"\
	
NODEP_CPP_CL_SC=\
	".\config.h"\
	".\dictlib.h"\
	".\lbmlib.h"\
	".\pngusr.h"\
	".\qcd.h"\
	".\scriplib.h"\
	".\trilib.h"\
	
# End Source File
# Begin Source File

SOURCE=.\cl_tent.c
DEP_CPP_CL_TE=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\sound.h"\
	".\sys.h"\
	".\vid.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\cl_view.c
DEP_CPP_CL_VI=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmdlib.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\d_iface.h"\
	".\draw.h"\
	".\gl_local.h"\
	".\gl_model.h"\
	".\gl_texture.h"\
	".\mathlib.h"\
	".\modelgen.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progsint.h"\
	".\progslib.h"\
	".\progtype.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\r_local.h"\
	".\r_model.h"\
	".\r_shared.h"\
	".\render.h"\
	".\spritegn.h"\
	".\sys.h"\
	".\vid.h"\
	".\zone.h"\
	
NODEP_CPP_CL_VI=\
	".\dictlib.h"\
	".\lbmlib.h"\
	".\qcd.h"\
	".\scriplib.h"\
	".\trilib.h"\
	

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# SUBTRACT CPP /WX

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\console.c
DEP_CPP_CONSO=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\keys.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\sys.h"\
	".\vid.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\in_win.c
DEP_CPP_IN_WI=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\input.h"\
	".\keys.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\sys.h"\
	".\vid.h"\
	".\winquake.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\keys.c
DEP_CPP_KEYS_=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\keys.h"\
	".\mathlib.h"\
	".\menu.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\sys.h"\
	".\textencoding.h"\
	".\vid.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\menu.c
DEP_CPP_MENU_=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmdlib.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\gl_local.h"\
	".\gl_model.h"\
	".\gl_texture.h"\
	".\input.h"\
	".\keys.h"\
	".\mathlib.h"\
	".\modelgen.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progsint.h"\
	".\progslib.h"\
	".\progtype.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\sound.h"\
	".\spritegn.h"\
	".\sys.h"\
	".\version.h"\
	".\vid.h"\
	".\winquake.h"\
	".\zone.h"\
	
NODEP_CPP_MENU_=\
	".\dictlib.h"\
	".\lbmlib.h"\
	".\qcd.h"\
	".\scriplib.h"\
	".\trilib.h"\
	
# End Source File
# Begin Source File

SOURCE=.\rc_image.c
DEP_CPP_RC_IM=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\png.h"\
	".\pngconf.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\qlib.h"\
	".\quakedef.h"\
	".\rc_image.h"\
	".\render.h"\
	".\sys.h"\
	".\vid.h"\
	".\winquake.h"\
	".\zconf.h"\
	".\zlib.h"\
	".\zone.h"\
	
NODEP_CPP_RC_IM=\
	".\config.h"\
	".\pngusr.h"\
	
# End Source File
# Begin Source File

SOURCE=.\rc_pixops.c
DEP_CPP_RC_PI=\
	".\mathlib.h"\
	".\q_shared.h"\
	".\rc_pixops.h"\
	".\sys.h"\
	
# End Source File
# Begin Source File

SOURCE=.\rc_wad.c
DEP_CPP_RC_WA=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmdlib.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\crc.h"\
	".\cvar.h"\
	".\draw.h"\
	".\gl_local.h"\
	".\gl_model.h"\
	".\gl_texture.h"\
	".\mathlib.h"\
	".\modelgen.h"\
	".\net.h"\
	".\pmove.h"\
	".\pr_comp.h"\
	".\progsint.h"\
	".\progslib.h"\
	".\progtype.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\rc_wad.h"\
	".\render.h"\
	".\spritegn.h"\
	".\sys.h"\
	".\vid.h"\
	".\zone.h"\
	
NODEP_CPP_RC_WA=\
	".\dictlib.h"\
	".\lbmlib.h"\
	".\qcd.h"\
	".\scriplib.h"\
	".\trilib.h"\
	
# End Source File
# Begin Source File

SOURCE=.\skin.c
DEP_CPP_SKIN_=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmdlib.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\d_iface.h"\
	".\draw.h"\
	".\gl_local.h"\
	".\gl_model.h"\
	".\gl_texture.h"\
	".\mathlib.h"\
	".\modelgen.h"\
	".\net.h"\
	".\pmove.h"\
	".\png.h"\
	".\pngconf.h"\
	".\pr_comp.h"\
	".\progsint.h"\
	".\progslib.h"\
	".\progtype.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\r_local.h"\
	".\r_model.h"\
	".\r_shared.h"\
	".\rc_image.h"\
	".\render.h"\
	".\spritegn.h"\
	".\sys.h"\
	".\teamplay.h"\
	".\vid.h"\
	".\zconf.h"\
	".\zlib.h"\
	".\zone.h"\
	
NODEP_CPP_SKIN_=\
	".\config.h"\
	".\dictlib.h"\
	".\lbmlib.h"\
	".\pngusr.h"\
	".\qcd.h"\
	".\scriplib.h"\
	".\trilib.h"\
	
# End Source File
# Begin Source File

SOURCE=.\snd_dma.c
DEP_CPP_SND_D=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\sound.h"\
	".\sys.h"\
	".\vid.h"\
	".\winquake.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\snd_mem.c
DEP_CPP_SND_M=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\sound.h"\
	".\sys.h"\
	".\vid.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\snd_mix.c
DEP_CPP_SND_MI=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\sound.h"\
	".\sys.h"\
	".\vid.h"\
	".\winquake.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\snd_win.c
DEP_CPP_SND_W=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\sound.h"\
	".\sys.h"\
	".\vid.h"\
	".\winquake.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\teamplay.c
DEP_CPP_TEAMP=\
	".\bspfile.h"\
	".\cl_screen.h"\
	".\cl_view.h"\
	".\client.h"\
	".\cmd.h"\
	".\cmodel.h"\
	".\common.h"\
	".\console.h"\
	".\cvar.h"\
	".\draw.h"\
	".\mathlib.h"\
	".\net.h"\
	".\pmove.h"\
	".\protocol.h"\
	".\q_shared.h"\
	".\quakedef.h"\
	".\render.h"\
	".\sound.h"\
	".\sys.h"\
	".\teamplay.h"\
	".\version.h"\
	".\vid.h"\
	".\zone.h"\
	
# End Source File
# Begin Source File

SOURCE=.\textencoding.c
DEP_CPP_TEXTE=\
	".\mathlib.h"\
	".\q_shared.h"\
	".\sys.h"\
	".\textencoding.h"\
	
# End Source File
# End Group
# Begin Source File

SOURCE=.\winquake.rc
# End Source File
# End Group
# Begin Group "Resource Files"

# PROP Default_Filter "ico;cur;bmp;dlg;rc2;rct;bin;cnt;rtf;gif;jpg;jpeg;jpe"
# Begin Source File

SOURCE=.\enginez.ico
# End Source File
# End Group
# Begin Group "Asm Files"

# PROP Default_Filter ""
# Begin Source File

SOURCE=.\cl_math.s

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Debug-gl
InputPath=.\cl_math.s
InputName=cl_math

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /D "GLQUAKE" /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Release
InputPath=.\cl_math.s
InputName=cl_math

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Release-gl
InputPath=.\cl_math.s
InputName=cl_math

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /D "GLQUAKE" /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Debug
InputPath=.\cl_math.s
InputName=cl_math

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\d_draw.s

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Release
InputPath=.\d_draw.s
InputName=d_draw

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Debug
InputPath=.\d_draw.s
InputName=d_draw

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\d_draw16.s

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Release
InputPath=.\d_draw16.s
InputName=d_draw16

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Debug
InputPath=.\d_draw16.s
InputName=d_draw16

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\d_parta.s

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Release
InputPath=.\d_parta.s
InputName=d_parta

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Debug
InputPath=.\d_parta.s
InputName=d_parta

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\d_polysa.s

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Release
InputPath=.\d_polysa.s
InputName=d_polysa

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Debug
InputPath=.\d_polysa.s
InputName=d_polysa

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\d_scana.s

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Release
InputPath=.\d_scana.s
InputName=d_scana

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Debug
InputPath=.\d_scana.s
InputName=d_scana

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\d_spr8.s

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Release
InputPath=.\d_spr8.s
InputName=d_spr8

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Debug
InputPath=.\d_spr8.s
InputName=d_spr8

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\d_varsa.s

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Release
InputPath=.\d_varsa.s
InputName=d_varsa

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Debug
InputPath=.\d_varsa.s
InputName=d_varsa

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\math.s

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Debug-gl
InputPath=.\math.s
InputName=math

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /D "GLQUAKE" /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Release
InputPath=.\math.s
InputName=math

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Release-gl
InputPath=.\math.s
InputName=math

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /D "GLQUAKE" /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Debug
InputPath=.\math.s
InputName=math

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\r_aclipa.s

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Release
InputPath=.\r_aclipa.s
InputName=r_aclipa

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Debug
InputPath=.\r_aclipa.s
InputName=r_aclipa

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\r_aliasa.s

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Release
InputPath=.\r_aliasa.s
InputName=r_aliasa

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Debug
InputPath=.\r_aliasa.s
InputName=r_aliasa

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\r_drawa.s

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Release
InputPath=.\r_drawa.s
InputName=r_drawa

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Debug
InputPath=.\r_drawa.s
InputName=r_drawa

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\r_edgea.s

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Release
InputPath=.\r_edgea.s
InputName=r_edgea

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Debug
InputPath=.\r_edgea.s
InputName=r_edgea

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\r_varsa.s

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Release
InputPath=.\r_varsa.s
InputName=r_varsa

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Debug
InputPath=.\r_varsa.s
InputName=r_varsa

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\snd_mixa.s

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Debug-gl
InputPath=.\snd_mixa.s
InputName=snd_mixa

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /D "GLQUAKE" /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Release
InputPath=.\snd_mixa.s
InputName=snd_mixa

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Release-gl
InputPath=.\snd_mixa.s
InputName=snd_mixa

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /D "GLQUAKE" /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Debug
InputPath=.\snd_mixa.s
InputName=snd_mixa

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\surf8.s

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Release
InputPath=.\surf8.s
InputName=surf8

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Debug
InputPath=.\surf8.s
InputName=surf8

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\sys_x86.s

!IF  "$(CFG)" == "enginez - Win32 GLDebug"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Debug-gl
InputPath=.\sys_x86.s
InputName=sys_x86

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /D "GLQUAKE" /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "enginez - Win32 Release"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Release
InputPath=.\sys_x86.s
InputName=sys_x86

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "enginez - Win32 GLRelease"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Release-gl
InputPath=.\sys_x86.s
InputName=sys_x86

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /D "GLQUAKE" /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "enginez - Win32 Debug"

# PROP Ignore_Default_Tool 1
# Begin Custom Build
OutDir=.\Debug
InputPath=.\sys_x86.s
InputName=sys_x86

"$(OUTDIR)\$(InputName).obj" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	cl /nologo /EP > $(OUTDIR)\$(InputName).spp $(InputPath) 
	gas2masm < $(OUTDIR)\$(InputName).spp >$(OUTDIR)\$(InputName).asm 
	ml /nologo /c /Cp /coff /Fo$(OUTDIR)\$(InputName).obj /Zm /Zi $(OUTDIR)\$(InputName).asm 
	del $(OUTDIR)\$(InputName).spp 
	
# End Custom Build

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\worlda.s
# PROP Exclude_From_Build 1
# End Source File
# End Group
# End Target
# End Project
