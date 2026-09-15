cmake_minimum_required(VERSION 3.18)
project(vcxsrv_libxml2 LANGUAGES C)

add_subdirectory(source upstream)

# Keep one stable runtime/import-library name for every supported configuration.
set_target_properties(LibXml2 PROPERTIES DEBUG_POSTFIX "")
