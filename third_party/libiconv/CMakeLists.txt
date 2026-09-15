cmake_minimum_required(VERSION 3.18)
project(vcxsrv_libiconv VERSION 1.19 LANGUAGES C)

add_library(libiconv SHARED
    source/lib/iconv.c
    source/libcharset/lib/localcharset.c
    source/lib/compat.c
)

target_include_directories(libiconv PRIVATE
    source
    source/lib
    source/include
)
target_compile_definitions(libiconv PRIVATE
    BUILDING_LIBICONV
    BUILDING_DLL
    PIC
    HAVE_CONFIG_H
    ENABLE_RELOCATABLE=1
    IN_LIBRARY
    INSTALLPREFIX=""
    INSTALLDIR=""
    LIBDIR=""
    NO_XMALLOC
    set_relocation_prefix=libiconv_set_relocation_prefix
    relocate=libiconv_relocate
    _CRT_SECURE_NO_WARNINGS
)
set_target_properties(libiconv PROPERTIES
    WINDOWS_EXPORT_ALL_SYMBOLS ON
    MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>DLL"
)
if(MSVC)
    target_compile_options(libiconv PRIVATE /W3)
    target_link_options(libiconv PRIVATE /DYNAMICBASE /NXCOMPAT)
endif()
