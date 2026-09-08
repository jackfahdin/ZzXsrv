ifeq ($(MAKESERVER),1)
$(error Please do not specify MAKESERVER=1)
endif

DESTDIR=$(MHMAKECONF)\xorg-server\xkbdata

# The old rules makefiles predate the current Meson part numbering. The native
# installer uses the checked-in Meson data lists and upstream Python generators
# to create both the core data and compatibility rules without WSL or Meson.
XKB_INPUTS = $(wildcard compat/* compat/*/* geometry/* geometry/*/* keycodes/* keycodes/*/* symbols/* symbols/*/* types/* rules/* rules/compat/* scripts/registry.py)

$(DESTDIR)\.native-build.stamp: $(XKB_INPUTS) meson.build symbols/meson.build $(MHMAKECONF)/tools/build_xkbdata.py
	$(PYTHON) "$(MHMAKECONF)/tools/build_xkbdata.py" --source . --output "$(DESTDIR)" --perl "$(PERL)"

all: $(DESTDIR)\.native-build.stamp

