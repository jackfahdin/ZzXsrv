WINAPP = xcalc

DEFINES += XT_NO_SM IEEE

INCLUDELIBFILES = \
 $(COMPONENT_LIBXCB_DIR)\src\$(OBJDIR)\libxcb.lib \
 $(COMPONENT_LIBXPM_DIR)\src\$(OBJDIR)\libXpm.lib \
 $(COMPONENT_LIBXAU_DIR)\$(OBJDIR)\libXau.lib \
 $(COMPONENT_LIBXAW_DIR)\src\$(OBJDIR)\libXaw.lib \
 $(COMPONENT_LIBXT_DIR)\src\$(OBJDIR)\libXt.lib \
 $(COMPONENT_LIBXEXT_DIR)\src\$(OBJDIR)\libXext.lib \
 $(COMPONENT_LIBXMU_DIR)\src\$(OBJDIR)\libXmu.lib \
 $(COMPONENT_LIBX11_DIR)\$(OBJDIR)\libX11.lib

LIBDIRS=$(dir $(INCLUDELIBFILES))

load_makefile $(LIBDIRS:%$(OBJDIR)\=%makefile MAKESERVER=0 DEBUG=$(DEBUG);)

LINKLIBS += $(PTHREADLIB)

CSRCS =	\
        actions.c \
        math.c \
        xcalc.c
