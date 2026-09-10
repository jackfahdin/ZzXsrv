TTYAPP = xwininfo

INCLUDELIBFILES = \
 $(COMPONENT_LIBXCB_DIR)\src\$(OBJDIR)\libxcb.lib \
 $(COMPONENT_LIBXAU_DIR)\$(OBJDIR)\libXau.lib \
 $(COMPONENT_LIBXEXT_DIR)\src\$(OBJDIR)\libXext.lib \
 $(COMPONENT_LIBX11_DIR)\$(OBJDIR)\libX11.lib

LIBDIRS=$(dir $(INCLUDELIBFILES))

load_makefile $(LIBDIRS:%$(OBJDIR)\=%makefile MAKESERVER=0 DEBUG=$(DEBUG);)

LINKLIBS += $(PTHREADLIB)

CSRCS = \
        clientwin.c \
        dsimple.c \
        xwininfo.c

