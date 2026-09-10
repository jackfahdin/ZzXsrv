ifeq ($(MAKESERVER),1)
$(error Please do not specify MAKESERVER=1)
endif

DESTDIR=$(COMPONENT_XORG_SERVER_DIR)\xkbdata\symbols\sharp_vndr

dist_symbols_DATA = sl-c3x00 ws003sh ws007sh ws011sh ws020sh

DATA_FILES=$(dist_symbols_DATA:%=$(DESTDIR)\%)

include ..\..\xkbrules.mak
