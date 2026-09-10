ifeq ($(MAKESERVER),1)
$(error Please do not specify MAKESERVER=1)
endif

DESTDIR=$(COMPONENT_XORG_SERVER_DIR)\xkbdata\symbols\jolla_vndr

dist_symbols_DATA = sbj

DATA_FILES=$(dist_symbols_DATA:%=$(DESTDIR)\%)

include ..\..\xkbrules.mak
