DEFINES += BAD_ARPAINET

TTYAPP = xhost

INCLUDELIBFILES = \
 ..\common\$(OBJDIR)\common.lib \
 $(COMPONENT_LIBXCB_DIR)\src\$(OBJDIR)\libxcb.lib \
 $(COMPONENT_LIBXAU_DIR)\$(OBJDIR)\libXau.lib \
 $(COMPONENT_LIBXMU_DIR)\src\$(OBJDIR)\libXmu.lib \
 $(COMPONENT_LIBX11_DIR)\$(OBJDIR)\libX11.lib \

LIBDIRS=$(dir $(INCLUDELIBFILES))

load_makefile $(LIBDIRS:%$(OBJDIR)\=%makefile MAKESERVER=0 DEBUG=$(DEBUG);)

LINKLIBS += $(PTHREADLIB)

CSRCS = xhost.c
