ifeq ($(MAKESERVER),1)
$(error Please do not specify MAKESERVER=1)
endif

DESTDIR=$(COMPONENT_XORG_SERVER_DIR)\xkbdata\symbols\sony_vndr

dist_symbols_DATA = us

DATA_FILES=$(dist_symbols_DATA:%=$(DESTDIR)\%)

include ..\..\xkbrules.mak
