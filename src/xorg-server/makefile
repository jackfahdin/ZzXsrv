ifneq ($(MAKESERVER),1)
$(error Please specify MAKESERVER=1 on the command line or as environment variable)
endif

INCLUDELIBFILES =  \
 composite\$(OBJDIR)\libcomposite.lib \
 config\$(OBJDIR)\libconfig.lib \
 damageext\$(OBJDIR)\libdamageext.lib \
 dbe\$(OBJDIR)\libdbe.lib \
 dix\$(OBJDIR)\libdix.lib \
 fb\$(OBJDIR)\libfb.lib \
 glx\$(OBJDIR)\libglx.lib \
 hw\xwin\$(OBJDIR)\libXWin.lib \
 hw\xwin\glx\$(OBJDIR)\libwinglx.lib \
 hw\xwin\winclipboard\$(OBJDIR)\libXWinclipboard.lib \
 mi\$(OBJDIR)\libmi.lib \
 miext\damage\$(OBJDIR)\libdamage.lib \
 miext\shadow\$(OBJDIR)\libshadow.lib \
 miext\sync\$(OBJDIR)\libsync.lib \
 miext\rootless\$(OBJDIR)\librootless.lib \
 os\$(OBJDIR)\libos.lib \
 randr\$(OBJDIR)\librandr.lib \
 record\$(OBJDIR)\librecord.lib \
 Xext\$(OBJDIR)\libxext.lib \
 xfixes\$(OBJDIR)\libxfixes.lib \
 Xi\$(OBJDIR)\libXi.lib \
 xkb\$(OBJDIR)\libxkb.lib \
 render\$(OBJDIR)\librender.lib \
 present\$(OBJDIR)\libpresent.lib \
 pseudoramiX\$(OBJDIR)\libPseudoramiX.lib

INCLUDENOSERVLIBFILES =  \
 $(COMPONENT_LIBX11_DIR)\$(NOSERVOBJDIR)\libX11.lib \
 $(COMPONENT_LIBXCB_DIR)\src\$(NOSERVOBJDIR)\libxcb.lib \
 $(COMPONENT_PIXMAN_DIR)\pixman\$(NOSERVOBJDIR)\libpixman-1.lib \
 $(COMPONENT_LIBXDMCP_DIR)\$(NOSERVOBJDIR)\libXdmcp.lib \
 $(COMPONENT_LIBXAU_DIR)\$(NOSERVOBJDIR)\libXau.lib \
 $(COMPONENT_LIBXFIXES_DIR)\src\$(NOSERVOBJDIR)\libXfixes.lib \
 $(COMPONENT_LIBXFONT2_DIR)\$(NOSERVOBJDIR)\libXfont2.lib \
 $(COMPONENT_LIBFONTENC_DIR)\src\$(NOSERVOBJDIR)\libfontenc.lib \
 $(COMPONENT_LIBXINERAMA_DIR)\src\$(NOSERVOBJDIR)\libXinerama.lib \
 $(COMPONENT_ZLIB_DIR)\$(NOSERVOBJDIR)\zlib1.lib

LIBDIRS=$(dir $(INCLUDELIBFILES))
NOSERVLIBDIRS=$(dir $(INCLUDENOSERVLIBFILES))

load_makefile $(LIBDIRS:%$(OBJDIR)\=%makefile MAKESERVER=$(MAKESERVER) DEBUG=$(DEBUG);)
load_makefile $(NOSERVLIBDIRS:%$(NOSERVOBJDIR)\=%makefile MAKESERVER=0 DEBUG=$(DEBUG);)

OBJS = dix\$(OBJDIR)\main.obj

LINKLIBS += $(PTHREADLIB) $(FREETYPELIB) $(OPENSSLLIB) opengl32.lib dwmapi.lib

ifeq ($(DEBUG),1)
TTYAPP=vcxsrv
APP:=$(TTYAPP)
else
WINAPP=vcxsrv
APP:=$(WINAPP)
endif

RCINCLUDES += include hw\xwin $(MHMAKECONF)\include $(MHMAKECONF)

XWin.rc: hw\xwin\XWin.rc
	copy $< $@

RESOURCES = XWin.rc

$(OBJDIR)\$(APP).exe: $(LINKLIBS)

load_makefile fonts.src\makefile MAKESERVER=0 DEBUG=$(DEBUG)
load_makefile xkeyboard-config\makefile MAKESERVER=0 DEBUG=$(DEBUG)

EXTRASTOBUILD =  \
 hw\xwin\xlaunch\$(NOSERVOBJDIR)\xlaunch.exe \
 ..\..\third_party\xorg\xkbcomp\$(NOSERVOBJDIR)\xkbcomp.exe \
 ..\..\third_party\xorg\apps\xcalc\$(NOSERVOBJDIR)\xcalc.exe \
 ..\..\third_party\xorg\apps\xclock\$(NOSERVOBJDIR)\xclock.exe \
 ..\..\third_party\xorg\apps\xwininfo\$(NOSERVOBJDIR)\xwininfo.exe \
 ..\..\third_party\xorg\apps\xhost\$(NOSERVOBJDIR)\xhost.exe \
 ..\..\third_party\xorg\apps\xrdb\$(NOSERVOBJDIR)\xrdb.exe \
 ..\..\third_party\xorg\apps\xauth\$(NOSERVOBJDIR)\xauth.exe \
 ..\..\tools\plink\$(NOSERVOBJDIR)\plink.exe \
 hw\xwin\swrastwgl_dri\$(NOSERVOBJDIR)\swrastwgl_dri.dll \
 ..\..\third_party\graphics\dxtn\$(NOSERVOBJDIR)\dxtn.dll

EXTRASTOBUILDDIRS=$(dir $(EXTRASTOBUILD))

load_makefile $(EXTRASTOBUILDDIRS:%$(NOSERVOBJDIR)\=%makefile MAKESERVER=0 DEBUG=$(DEBUG);)
all: $(EXTRASTOBUILD)

load_makefile $(COMPONENT_MESALIB_DIR)\src\makefile MAKESERVER=0 DEBUG=$(DEBUG)
all: $(COMPONENT_MESALIB_DIR)\src\$(NOSERVOBJDIR)\swrast_dri.lib $(COMPONENT_MESALIB_DIR)\src\$(NOSERVOBJDIR)\swrast_dri.dll

all: fonts.src\all xkeyboard-config\all

