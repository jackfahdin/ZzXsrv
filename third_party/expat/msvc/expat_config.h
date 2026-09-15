/* Local Windows configuration for the mhmake build. See README.vcxsrv.md. */
#ifndef EXPAT_CONFIG_H
#define EXPAT_CONFIG_H 1

#define BYTEORDER 1234
#define HAVE_FCNTL_H 1
#define HAVE_INTTYPES_H 1
#define HAVE_MEMORY_H 1
#define HAVE_STDINT_H 1
#define HAVE_STDLIB_H 1
#define HAVE_STRING_H 1
#define HAVE_SYS_STAT_H 1
#define HAVE_SYS_TYPES_H 1
#define STDC_HEADERS 1

#define PACKAGE "expat"
#define PACKAGE_NAME "expat"
#define PACKAGE_STRING "expat 2.8.4"
#define PACKAGE_TARNAME "expat"
#define PACKAGE_VERSION "2.8.4"
#define PACKAGE_BUGREPORT "https://github.com/libexpat/libexpat/issues"
#define PACKAGE_URL "https://libexpat.github.io/"

#define XML_CONTEXT_BYTES 1024
#define XML_DTD 1
#define XML_GE 1
#define XML_NS 1

/* XML_UNICODE, XML_LARGE_SIZE and XML_ATTR_INFO remain disabled.
 * _WIN32 selects upstream rand_s; no Unix entropy/header macros are enabled. */
#endif
