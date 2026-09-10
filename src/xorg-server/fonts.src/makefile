SUBDIRS=font-util 75dpi 100dpi cyrillic encodings misc OTF Speedo TTF Type1 terminus-font

DESTDIR=$(COMPONENT_XORG_SERVER_DIR)\fonts

all: $(DESTDIR)\fonts.conf

$(DESTDIR)\fonts.conf: $(DESTDIR) fonts.conf
	copy fonts.conf $@
