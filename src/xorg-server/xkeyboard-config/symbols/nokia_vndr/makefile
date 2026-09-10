ifeq ($(MAKESERVER),1)
$(error Please do not specify MAKESERVER=1)
endif

DESTDIR=$(COMPONENT_XORG_SERVER_DIR)\xkbdata\symbols\nokia_vndr

dist_symbols_DATA = rx-44 rx-51 su-8w

DATA_FILES=$(dist_symbols_DATA:%=$(DESTDIR)\%)

include ..\..\xkbrules.mak
