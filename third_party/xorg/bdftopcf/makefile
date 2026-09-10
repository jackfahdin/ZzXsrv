TTYAPP = bdftopcf

INCLUDELIBFILES = \
 $(COMPONENT_APPS_DIR)\common\$(OBJDIR)\common.lib \
 $(COMPONENT_ZLIB_DIR)\$(OBJDIR)\zlib1.lib \
 $(COMPONENT_LIBXFONT2_DIR)\$(OBJDIR)\libXfont2.lib \
 $(COMPONENT_LIBFONTENC_DIR)\src\$(OBJDIR)\libfontenc.lib

LIBDIRS=$(dir $(INCLUDELIBFILES))

load_makefile $(LIBDIRS:%$(OBJDIR)\=%makefile MAKESERVER=0 DEBUG=$(DEBUG);)

CSRCS = \
	atom.c \
	bdfread.c \
	bdfutils.c \
	bitmap.c \
	bitmaputil.c \
	bufio.c \
	defaults.c \
	fileio.c \
	filewr.c \
	fontaccel.c \
	fontink.c \
	pcfwrite.c \
	private.c \
	utilbitmap.c \
	bdftopcf.c

LINKLIBS += $(FREETYPELIB)

