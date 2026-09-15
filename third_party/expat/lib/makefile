LIBRARY = libexpat

# Keep the narrow-character static ABI used by the Windows Mesa build.
DEFINES = XML_STATIC
INCLUDES = ../msvc .. $(MHMAKECONF)/include
CCFLAGS += /source-charset:utf-8

# xmltok_ns.c and xmltok_impl.c are included by xmltok.c, not separate units.
CSRCS := xmlparse.c xmltok.c xmlrole.c random_rand_s.c
