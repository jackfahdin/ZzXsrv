#define HAVE_INTTYPES_H 1
#define HAVE_FT_GET_NEXT_CHAR 1
#define ENABLE_LIBXML2
#define HAVE_RAND 1
#define HAVE_STRUCT_DIRENT_D_TYPE 1
#undef __STDC__
#define FLEXIBLE_ARRAY_MEMBER
#define inline __inline
#define HAVE_FCNTL_H 1
#define HAVE__MKTEMP_S 1
#define FC_CACHEDIR getenv("TEMP")
#define FC_DEFAULT_FONTS "fonts"
#define FC_GPERF_SIZE_T size_t
#ifdef _WIN64
#define SIZEOF_VOID_P 8
#else
#define SIZEOF_VOID_P 4
#endif
#ifndef PATH_MAX
#define PATH_MAX 1024
#endif
#define CONFIGDIR "./fonts"
#define HAVE_UNISTD_H 1


/* Native MSVC FreeType backend and locale-independent formatting. */
#define ENABLE_FREETYPE 1
#define HAVE__VSNPRINTF_L 1
#define FC_VERSION_MAJOR 2
#define FC_VERSION_MINOR 18
#define FC_VERSION_MICRO 3
