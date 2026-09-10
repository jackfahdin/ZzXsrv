ifeq ($(MAKESERVER),1)
$(error Please do not specify MAKESERVER=1)
endif

DESTDIR=$(COMPONENT_XORG_SERVER_DIR)\xkbdata\geometry\digital_vndr

dist_geom_DATA = \
lk  pc  unix

DATA_FILES=$(dist_geom_DATA:%=$(DESTDIR)\%)

include ..\..\xkbrules.mak
