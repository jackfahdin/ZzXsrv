ifeq ($(MAKESERVER),1)
$(error Please do not specify MAKESERVER=1)
endif

DESTDIR=$(COMPONENT_XORG_SERVER_DIR)\xkbdata\keycodes\digital_vndr

dist_keycodes_DATA = lk pc

DATA_FILES=$(dist_keycodes_DATA:%=$(DESTDIR)\%)

include ..\..\xkbrules.mak
