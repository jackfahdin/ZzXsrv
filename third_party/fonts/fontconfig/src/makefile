$(OBJDIR)\fcobjshash.gperf: fcobjshash.gperf.h fcobjs.h
	copy $< $<.c
	$(CPP) -EP -I.. $<.c | \
	$(PYTHON) cleangperf.py | \
	$(BUILD_NATIVE) cut-out > $@.tmp
	copy $@.tmp $@
	del $@.tmp
	del $<.c

$(OBJDIR)\fcobjshash.h: $(OBJDIR)\fcobjshash.gperf converttype.py
	$(GPERF_COMMAND) -m 100 < $< > $@
	$(PYTHON) converttype.py $@

DEFINES+=FC_TEMPLATEDIR=\"./conf.avail\"

load_makefile NORELDBG=1 ..\fc-case\makefile
load_makefile NORELDBG=1 ..\fc-lang\makefile

CSRCS = \
	fcatomic.c \
	fccache.c \
	fccfg.c \
	fccharset.c \
	fccompat.c \
	fcconffile.c \
	fcgenericalias.c \
	fcdbg.c \
	fcdefault.c \
	fcdir.c \
	fcformat.c \
	fcfreetype.c \
	fcfs.c \
	fcptrlist.c \
	fchash.c \
	fcinit.c \
	fclang.c \
	fclist.c \
	fcmatch.c \
	fcmatrix.c \
	fcname.c \
	fcobjs.c \
	fcpat.c \
	fcrange.c \
	fcserialize.c \
	fcstat.c \
	fcstr.c \
	fcweight.c \
	fcxml.c \
	ftglue.c \
	gen_uuid.c \
	copy.c \
	parse.c \
	pack.c \
	unpack.c \
	unparse.c

LIBRARY = libfontconfig

INCLUDES := .. uuid $(OBJDIR) $(INCLUDES) $(COMPONENT_FREETYPE_DIR)\include\freetype $(COMPONENT_FREETYPE_DIR)\include $(LIBXMLINCLUDE) $(COMPONENT_LIBXML2_DIR)\source\include $(MHMAKECONF)\third_party\libiconv\source\include \
	..\fc-lang\$(OBJDIR)\..	..\fc-case\$(OBJDIR)\..

load_makefile IS64=0 NORELDBG=1 makefile.srcs


# New upstream constant and generic-family tables. All inputs are dependencies.
$(OBJDIR)\fcconst.h: ..\fc-const\fc-const.py ..\fc-const\fcconst.list fcobjs.h
	$(PYTHON) ..\fc-const\fc-const.py ..\fc-const\fcconst.list fcobjs.h --output $@

GENERIC_INPUTS = $(wildcard ..\fc-genericfamily\*.txt)
$(OBJDIR)\fcgenericfamily.gperf: ..\fc-genericfamily\fc-genericfamily.py $(GENERIC_INPUTS)
	$(PYTHON) ..\fc-genericfamily\fc-genericfamily.py -d ..\fc-genericfamily -o $@

$(OBJDIR)\fcgenericfamily.h: $(OBJDIR)\fcgenericfamily.gperf converttype.py
	$(GPERF_COMMAND) --pic -m 100 < $< > $@
	$(PYTHON) converttype.py $@
