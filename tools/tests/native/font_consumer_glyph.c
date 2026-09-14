/* Execute all three production consumers with signed metrics; downstream
 * rendering fixtures record geometry instead of writing device pixels. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "../../../src/xorg-server/fb/fbglyph.c"
#include "../../../src/xorg-server/mi/miglblt.c"
#define CHECK(c) do { if (!(c)) { fprintf(stderr, "FAIL %d: %s\n", __LINE__, #c); exit(1); } } while (0)
PaddingInfo PixmapWidthPaddingInfo[33];
static DevPrivateKeyRec screen_key;
static FbScreenPrivRec screen_private;
static FbGCPrivRec gc_private;
static ScreenRec screen;
static GC scratch;
static PixmapRec pixmap;
static int pushes, image_calls, last_x, last_width, last_height, destroys, scratch_frees;
DevPrivateKey fbGetScreenPrivateKey(void) { return &screen_key; }
static void record(int x, int w, int h) { pushes++; last_x=x; last_width=w; last_height=h; }
void fbPushImage(DrawablePtr d, GCPtr g, FbStip *s, FbStride stride, int sx, int x, int y, int w, int h) { record(x,w,h); }
void fbPutXYImage(DrawablePtr d, RegionPtr clip, FbBits fg, FbBits bg, FbBits pm, int alu, Bool opaque,
                  int x, int y, int w, int h, FbStip *s, FbStride stride, int sx) { record(x,w,h); }
void fbSolidBoxClipped(DrawablePtr d, RegionPtr clip, int x, int y, int xx, int yy, FbBits and, FbBits xor) {}
void fbGlyph8(FbBits *dst, FbStride stride, int bpp, FbStip *s, FbBits fg, int h, int shift) { CHECK(0); }
void fbGlyph16(FbBits *dst, FbStride stride, int bpp, FbStip *s, FbBits fg, int h, int shift) { CHECK(0); }
void fbGlyph32(FbBits *dst, FbStride stride, int bpp, FbStip *s, FbBits fg, int h, int shift) { CHECK(0); }
pixman_region_overlap_t pixman_region_contains_rectangle(const pixman_region16_t *r, const pixman_box16_t *b) { CHECK(0); return 0; }
static PixmapPtr create_pixmap(ScreenPtr s, int w, int h, int depth, unsigned usage) {
    CHECK(w == 8 && h == 8 && depth == 1); pixmap.drawable.depth = 1; return &pixmap;
}
int dixDestroyPixmap(void *p, XID unused) { CHECK(p == &pixmap && unused == 0); destroys++; return Success; }
GCPtr GetScratchGC(unsigned depth, ScreenPtr s) { CHECK(depth == 1); return &scratch; }
void FreeScratchGC(GCPtr g) { CHECK(g == &scratch); scratch_frees++; }
int ChangeGC(ClientPtr client, GCPtr gc, BITS32 mask, ChangeGCVal *values) { return Success; }
void ValidateGC(DrawablePtr d, GCPtr gc) { gc->serialNumber = d->serialNumber; }
void *xreallocarray(void *old, size_t n, size_t s) { return calloc(n, s); }
static void put_image(DrawablePtr d, GCPtr gc, int depth, int x, int y, int w, int h,
                      int leftpad, int format, char *bits) { image_calls++; CHECK(w > 0 && h > 0); }
static void push_pixels(GCPtr gc, PixmapPtr p, DrawablePtr d, int w, int h, int x, int y) { record(x,w,h); }
int main(int argc, char **argv) {
    DrawableRec drawable = {0}; GC gc = {0}; FontRec font = {0};
    GCOps ops = {0}; CharInfoRec chars[2] = {0}; CharInfoPtr glyphs[2] = {&chars[0], &chars[1]};
    unsigned char bits[32] = {0};
    CHECK(argc == 3);
    screen_key.initialized = TRUE; screen_key.size = sizeof(screen_private);
    screen_private.gcPrivateKeyRec.initialized = TRUE;
    screen_private.gcPrivateKeyRec.size = sizeof(gc_private);
    screen.devPrivates = (PrivatePtr)&screen_private; screen.CreatePixmap = create_pixmap;
    gc.devPrivates = (PrivatePtr)&gc_private; gc.pScreen = &screen; gc.font = &font;
    gc_private.and = 1; /* Exercise the fallback that consumes both dimensions. */
    drawable.pScreen = &screen; drawable.bitsPerPixel = 32;
    font.info.maxbounds.rightSideBearing = 8; font.info.maxbounds.ascent = 8;
    font.info.fontAscent = 8;
    ops.PutImage = put_image; ops.PushPixels = push_pixels; gc.ops = &ops; scratch.ops = &ops;
    for (int i=0; i<2; i++) {
        chars[i].metrics.rightSideBearing = 4; chars[i].metrics.ascent = 2;
        chars[i].metrics.characterWidth = 7; chars[i].bits = bits;
    }
    if (!strcmp(argv[2], "negative-width")) chars[0].metrics.rightSideBearing = -1;
    else if (!strcmp(argv[2], "negative-height")) chars[0].metrics.ascent = -1;
    else if (!strcmp(argv[2], "zero-width")) chars[0].metrics.rightSideBearing = 0;
    else if (!strcmp(argv[2], "zero-height")) chars[0].metrics.ascent = 0;
    else CHECK(!strcmp(argv[2], "positive"));
    if (!strcmp(argv[1], "fb-poly")) fbPolyGlyphBlt(&drawable, &gc, 10, 10, 2, glyphs, NULL);
    else if (!strcmp(argv[1], "fb-image")) fbImageGlyphBlt(&drawable, &gc, 10, 10, 2, glyphs, NULL);
    else { CHECK(!strcmp(argv[1], "mi-poly")); miPolyGlyphBlt(&drawable, &gc, 10, 10, 2, glyphs, NULL); CHECK(destroys == 1 && scratch_frees == 1); }
    CHECK(pushes == (!strcmp(argv[2], "positive") ? 2 : 1));
    CHECK(last_x == 17 && last_width == 4 && last_height == 2);
    if (!strcmp(argv[1], "mi-poly")) CHECK(image_calls == pushes);
    printf("PASS %s %s\n", argv[1], argv[2]); return 0;
}

void xfont2_query_glyph_extents(FontPtr font, CharInfoPtr *chars, unsigned long n, ExtentInfoRec *info) { CHECK(0); }
