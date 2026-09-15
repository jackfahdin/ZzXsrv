INCLUDELIBFILES = window\$(OBJDIR)\window.lib \
                  $(COMPONENT_LIBX11_DIR)\$(OBJDIR)\libX11.lib \
                  $(COMPONENT_LIBXCB_DIR)\src\$(OBJDIR)\libxcb.lib \
                  $(COMPONENT_LIBXAU_DIR)\$(OBJDIR)\libXau.lib

CSRCS=config.cc main.cc xml_input.cpp

INCLUDES += $(LIBXMLINCLUDE) $(COMPONENT_LIBXML2_DIR)\source\include

WINAPP = xlaunch

RESOURCES = resources.rc

$(OBJDIR)\%.res : resources\%.rc $(wildcard resources\*.rc)
	$(RC) $(RCFLAGS) $(RCDEFINES:%=-d "%") $(RCINCLUDES:%=-i %) -Fo$(relpath $@) $<

LIBDIRS=$(dir $(INCLUDELIBFILES))

load_makefile $(LIBDIRS:%$(OBJDIR)\=%makefile MAKESERVER=0 DEBUG=$(DEBUG);)

LINKLIBS += $(LIBXMLLIB) $(PTHREADLIB) winhttp.lib

