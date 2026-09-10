TTYAPP = xauth

INCLUDELIBFILES = \
 ..\common\$(OBJDIR)\common.lib \
 $(COMPONENT_LIBXCB_DIR)\src\$(OBJDIR)\libxcb.lib \
 $(COMPONENT_LIBXAU_DIR)\$(OBJDIR)\libXau.lib \
 $(COMPONENT_LIBXMU_DIR)\src\$(OBJDIR)\libXmu.lib \
 $(COMPONENT_LIBXEXT_DIR)\src\$(OBJDIR)\libXext.lib \
 $(COMPONENT_LIBX11_DIR)\$(OBJDIR)\libX11.lib

LIBDIRS=$(dir $(INCLUDELIBFILES))

load_makefile $(LIBDIRS:%$(OBJDIR)\=%makefile MAKESERVER=0 DEBUG=$(DEBUG);)

LINKLIBS += $(PTHREADLIB)

INCLUDES += $(MHMAKECONF)\include\xcb

CSRCS =	\
        gethost.c \
        parsedpy.c \
        process.c \
        xauth.c

