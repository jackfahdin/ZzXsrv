/* Exercise the production FreeType DLL through its public API only. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ft2build.h>
#include FT_FREETYPE_H
#include FT_FONT_FORMATS_H

#define REQUIRE(condition, message) do { \
    if (!(condition)) { fprintf(stderr, "FAIL %s (line %d)\n", message, __LINE__); return 1; } \
} while (0)

int main(int argc, char **argv)
{
    FT_Library library;
    FT_Face face;
    FT_Int major, minor, patch;
    FT_UInt glyph;
    FT_ULong codepoint;
    unsigned int x, y, ink = 0;
    FT_Bitmap *bitmap;
    int mono, bitmap_font;
    const char *format;

    REQUIRE(FT_Init_FreeType(&library) == 0, "FT_Init_FreeType");
    FT_Library_Version(library, &major, &minor, &patch);
    printf("FreeType runtime %d.%d.%d; headers %d.%d.%d\n", major, minor, patch,
           FREETYPE_MAJOR, FREETYPE_MINOR, FREETYPE_PATCH);
    REQUIRE(major == 2 && minor == 14 && patch == 3, "runtime must be 2.14.3");
    if (argc == 2 && strcmp(argv[1], "version") == 0) {
        REQUIRE(FT_Done_FreeType(library) == 0, "FT_Done_FreeType");
        puts("PASS version");
        return 0;
    }
    REQUIRE(argc == 6, "usage: font codepoint format gray|mono present|missing");
    codepoint = strtoul(argv[2], NULL, 16);
    mono = strcmp(argv[4], "mono") == 0;
    bitmap_font = strcmp(argv[3], "BDF") == 0 || strcmp(argv[3], "PCF") == 0;
    REQUIRE(FT_New_Face(library, argv[1], 0, &face) == 0, "FT_New_Face");
    format = FT_Get_Font_Format(face);
    REQUIRE(format != NULL && strcmp(format, argv[3]) == 0, "font driver");
    REQUIRE(FT_Select_Charmap(face, FT_ENCODING_UNICODE) == 0, "Unicode charmap");
    glyph = FT_Get_Char_Index(face, codepoint);
    if (strcmp(argv[5], "missing") == 0)
        REQUIRE(glyph == 0, "missing character maps to .notdef");
    else
        REQUIRE(glyph > 0 && glyph < (FT_UInt)face->num_glyphs, "encoded glyph index");
    if (bitmap_font) {
        REQUIRE(face->num_fixed_sizes > 0, "bitmap strikes available");
        REQUIRE(FT_Select_Size(face, 0) == 0, "FT_Select_Size");
    } else {
        REQUIRE(FT_IS_SCALABLE(face), "scalable outlines");
        REQUIRE(FT_Set_Pixel_Sizes(face, 0, 32) == 0, "FT_Set_Pixel_Sizes");
    }
    REQUIRE(FT_Load_Glyph(face, glyph, FT_LOAD_DEFAULT) == 0, "FT_Load_Glyph");
    REQUIRE(face->glyph->advance.x > 0, "positive glyph advance");
    REQUIRE(FT_Render_Glyph(face->glyph, mono ? FT_RENDER_MODE_MONO : FT_RENDER_MODE_NORMAL) == 0,
            "FT_Render_Glyph");
    bitmap = &face->glyph->bitmap;
    REQUIRE(bitmap->buffer && bitmap->width > 0 && bitmap->rows > 0, "nonempty bitmap");
    REQUIRE(bitmap->pixel_mode == (mono ? FT_PIXEL_MODE_MONO : FT_PIXEL_MODE_GRAY), "pixel mode");
    for (y = 0; y < bitmap->rows; ++y) {
        const unsigned char *row = bitmap->buffer + (ptrdiff_t)y * bitmap->pitch;
        for (x = 0; x < bitmap->width; ++x)
            ink += mono ? !!(row[x / 8] & (0x80 >> (x % 8))) : !!row[x];
    }
    REQUIRE(ink > 0, "visible rasterized pixels");
    printf("PASS render family=%s format=%s U+%04lX glyph=%u bitmap=%ux%u ink=%u mode=%s\n",
           face->family_name, format, codepoint, glyph, bitmap->width, bitmap->rows, ink, argv[4]);
    REQUIRE(FT_Done_Face(face) == 0, "FT_Done_Face");
    REQUIRE(FT_Done_FreeType(library) == 0, "FT_Done_FreeType");
    return 0;
}
