/* A real Fontconfig cache/list/match consumer of the production FreeType DLL. */
#include <stdio.h>
#include <string.h>
#include <fontconfig/fontconfig.h>
#include <ft2build.h>
#include FT_FREETYPE_H

#define REQUIRE(condition, message) do { \
    if (!(condition)) { fprintf(stderr, "FAIL %s (line %d)\n", message, __LINE__); return 1; } \
} while (0)

int main(int argc, char **argv)
{
    FT_Library library;
    FT_Int major, minor, patch;
    FcConfig *config;
    FcCache *cache;
    FcFontSet *fonts;
    FcPattern *pattern, *match;
    FcObjectSet *objects;
    FcResult result;
    FcChar8 *file;
    FcCharSet *charset;
    int i, cache_count, listed, ttf = 0, otf = 0;
    REQUIRE(argc == 4, "usage: config fontdir build|reload");
    REQUIRE(FT_Init_FreeType(&library) == 0, "FT_Init_FreeType");
    FT_Library_Version(library, &major, &minor, &patch);
    REQUIRE(major == 2 && minor == 14 && patch == 3, "production FreeType 2.14.3");
    REQUIRE(FT_Done_FreeType(library) == 0, "FT_Done_FreeType");
    config = FcConfigCreate();
    REQUIRE(config != NULL, "FcConfigCreate");
    REQUIRE(FcConfigParseAndLoad(config, (const FcChar8 *)argv[1], FcTrue), "isolated config");
    if (strcmp(argv[3], "build") == 0)
        cache = FcDirCacheRead((const FcChar8 *)argv[2], FcTrue, config);
    else
        cache = FcDirCacheLoad((const FcChar8 *)argv[2], config, NULL);
    REQUIRE(cache != NULL, "directory cache exists");
    cache_count = FcCacheNumFont(cache);
    printf("CACHE patterns=%d\n", cache_count);
    REQUIRE(cache_count == 2, "cache contains each fixture font exactly once");
    FcDirCacheUnload(cache);
    REQUIRE(FcConfigBuildFonts(config), "FcConfigBuildFonts");
    pattern = FcPatternCreate();
    objects = FcObjectSetBuild(FC_FILE, FC_FAMILY, FC_CHARSET, NULL);
    REQUIRE(pattern && objects, "list pattern and objects");
    fonts = FcFontList(config, pattern, objects);
    REQUIRE(fonts && fonts->nfont == 2, "FcFontList returns exactly two fixture fonts");
    listed = fonts->nfont;
    /* Each fixture must appear exactly once in both cache and font listing. */
    for (i = 0; i < fonts->nfont; ++i) {
        REQUIRE(FcPatternGetString(fonts->fonts[i], FC_FILE, 0, &file) == FcResultMatch,
                "font path");
        REQUIRE(FcPatternGetCharSet(fonts->fonts[i], FC_CHARSET, 0, &charset) == FcResultMatch,
                "font charset");
        REQUIRE(FcCharSetHasChar(charset, 0x41), "font charset includes Latin A");
        if (strstr((const char *)file, "Vera.ttf"))
            ++ttf;
        else if (strstr((const char *)file, "rectangle.otf"))
            ++otf;
        else
            REQUIRE(0, "list contains an unexpected font file");
        printf("LIST %s\n", file);
    }
    REQUIRE(ttf == 1 && otf == 1, "TTF and CFF OTF discovered exactly once");
    FcFontSetDestroy(fonts);
    FcObjectSetDestroy(objects);
    FcPatternDestroy(pattern);
    pattern = FcNameParse((const FcChar8 *)"FreeType Test Rectangle");
    REQUIRE(pattern != NULL, "FcNameParse");
    REQUIRE(FcConfigSubstitute(config, pattern, FcMatchPattern), "FcConfigSubstitute");
    FcDefaultSubstitute(pattern);
    match = FcFontMatch(config, pattern, &result);
    REQUIRE(match && result == FcResultMatch, "FcFontMatch");
    REQUIRE(FcPatternGetString(match, FC_FILE, 0, &file) == FcResultMatch &&
            strstr((const char *)file, "rectangle.otf"), "CFF family resolves to fixture");
    FcPatternDestroy(match);
    FcPatternDestroy(pattern);
    FcConfigDestroy(config);
    FcFini();
    printf("PASS fontconfig %s cache-patterns=%d list-patterns=%d unique-files=2 "
           "CFF-match=rectangle.otf FreeType=2.14.3\n", argv[3], cache_count, listed);
    return 0;
}
