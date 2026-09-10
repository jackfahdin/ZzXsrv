TTYAPP = mkfontscale

DEFINES += _BSD_SOURCE

INCLUDES += $(COMPONENT_FREETYPE_DIR)\include\freetype $(COMPONENT_FREETYPE_DIR)\include

INCLUDELIBFILES = \
 $(COMPONENT_ZLIB_DIR)\$(OBJDIR)\zlib1.lib \
 $(COMPONENT_LIBXFONT2_DIR)\$(OBJDIR)\libXfont2.lib \
 $(COMPONENT_LIBFONTENC_DIR)\src\$(OBJDIR)\libfontenc.lib

LIBDIRS=$(dir $(INCLUDELIBFILES))

load_makefile $(LIBDIRS:%$(OBJDIR)\=%makefile MAKESERVER=0 DEBUG=$(DEBUG);)

CSRCS = constlist.c \
	hash.c \
	ident.c \
	list.c \
	mkfontscale.c

LINKLIBS += $(FREETYPELIB)

$(OBJDIR)/$(TTYAPP).exe: $(OBJDIR)/freetype.dll $(OBJDIR)/zlib1.dll

$(OBJDIR)/freetype.dll: $(FREETYPELIB:lib=dll)
	copy $< $@

$(OBJDIR)/zlib1.dll: $(COMPONENT_ZLIB_DIR)\$(OBJDIR)\zlib1.dll
	copy $< $@

