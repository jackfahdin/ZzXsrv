INCLUDELIBFILES = $(COMPONENT_LIBX11_DIR)\$(OBJDIR)\libX11.lib \
                  $(COMPONENT_LIBXCB_DIR)\src\$(OBJDIR)\libxcb.lib \
                  $(COMPONENT_LIBXAU_DIR)\$(OBJDIR)\libXau.lib \
                  $(COMPONENT_LIBXKBFILE_DIR)\src\$(OBJDIR)\libxkbfile.lib

LIBDIRS=$(dir $(INCLUDELIBFILES))

load_makefile $(LIBDIRS:%$(OBJDIR)\=%makefile MAKESERVER=0 DEBUG=$(DEBUG);)

ifeq $(DEBUG),1
TTYAPP = xkbcomp
else
WINAPP = xkbcomp
endif

DEFINES += DFLT_XKB_CONFIG_ROOT="\".\""  PACKAGE_VERSION="\"1.5.0\""

INCLUDES += $(OBJDIR)

CSRCS = action.c \
        alias.c \
        compat.c \
        expr.c \
        geometry.c \
        indicators.c \
        keycodes.c \
        keymap.c \
        keytypes.c \
        listing.c \
        misc.c \
        parseutils.c \
        symbols.c \
        utils.c \
        vmod.c \
        xkbcomp.c \
        xkbparse.c \
        xkbpath.c \
        xkbscan.c

LINKLIBS += $(PTHREADLIB) $(FREETYPELIB) $(OPENSSLLIB)

$(OBJDIR)\xkbparse.c $(OBJDIR)\xkbparse.h: xkbparse.y
	bison.bat -d -o$(OBJDIR)\xkbparse.c $<
