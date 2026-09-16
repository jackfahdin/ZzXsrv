#include <pixman.h>
#include <stdio.h>
#include <string.h>

#define CHECK(x) do { if (!(x)) { fprintf(stderr, "line %d: %s\n", __LINE__, #x); return 1; } } while (0)

static int over_or_mask(int mask_mode)
{
    uint32_t source[40], dest[40], alpha[10];
    unsigned char *mask_bytes = (unsigned char *)alpha;
    pixman_image_t *src, *dst, *mask = NULL;
    int i, y, x;
    for (i = 0; i < 40; ++i) { source[i] = mask_mode ? 0xffff0000 : 0x80800000; dest[i] = 0xff0000ff; }
    memset(alpha, 128, sizeof(alpha));
    src = pixman_image_create_bits(PIXMAN_a8r8g8b8, 17, 2, source, 80);
    dst = pixman_image_create_bits(PIXMAN_a8r8g8b8, 17, 2, dest, 80);
    CHECK(src && dst);
    if (mask_mode) {
        mask_bytes[0] = 0; mask_bytes[1] = 255;
        mask = pixman_image_create_bits(PIXMAN_a8, 17, 2, alpha, 20);
        CHECK(mask);
    }
    pixman_image_composite32(PIXMAN_OP_OVER, src, mask, dst, 0, 0, 0, 0, 0, 0, 17, 2);
    for (y = 0; y < 2; ++y) for (x = 0; x < 20; ++x) {
        uint32_t want = x < 17 ? 0xff80007f : 0xff0000ff;
        if (mask_mode && y == 0 && x == 0) want = 0xff0000ff;
        if (mask_mode && y == 0 && x == 1) want = 0xffff0000;
        CHECK(dest[y * 20 + x] == want);
    }
    if (mask) pixman_image_unref(mask);
    pixman_image_unref(src); pixman_image_unref(dst);
    return 0;
}

static int image_case(const char *mode)
{
    uint32_t source[4] = {0xffff0000, 0xff00ff00, 0xff0000ff, 0xffffffff};
    uint32_t dest[16] = {0};
    pixman_image_t *src, *dst;
    pixman_transform_t transform;
    pixman_region32_t clip;
    int negative = strcmp(mode, "negative-stride") == 0;
    int scaled = strcmp(mode, "transform") == 0;
    int clipped = strcmp(mode, "clip") == 0;
    int size = scaled ? 4 : 2, x, y;
    src = pixman_image_create_bits(PIXMAN_a8r8g8b8, 2, 2,
                                   negative ? source + 2 : source, negative ? -8 : 8);
    dst = pixman_image_create_bits(PIXMAN_a8r8g8b8, size, size, dest, size * 4);
    CHECK(src && dst);
    if (scaled) {
        pixman_transform_init_scale(&transform, pixman_fixed_1 / 2, pixman_fixed_1 / 2);
        CHECK(pixman_image_set_transform(src, &transform));
        CHECK(pixman_image_set_filter(src, PIXMAN_FILTER_NEAREST, NULL, 0));
    }
    if (clipped) {
        pixman_region32_init_rect(&clip, 1, 0, 1, 2);
        CHECK(pixman_image_set_clip_region32(dst, &clip));
        pixman_region32_fini(&clip);
    }
    pixman_image_composite32(PIXMAN_OP_SRC, src, NULL, dst, 0, 0, 0, 0, 0, 0, size, size);
    for (y = 0; y < size; ++y) for (x = 0; x < size; ++x) {
        int row = negative ? 1 - y : (scaled ? y / 2 : y);
        uint32_t want = clipped && x == 0 ? 0 : source[row * 2 + (scaled ? x / 2 : x)];
        CHECK(dest[y * size + x] == want);
    }
    pixman_image_unref(src); pixman_image_unref(dst);
    return 0;
}

static int region_case(void)
{
    pixman_region32_t outer, hole, result;
    pixman_box32_t *box;
    pixman_region32_init_rect(&outer, 0, 0, 6, 6);
    pixman_region32_init_rect(&hole, 2, 2, 2, 2);
    pixman_region32_init(&result);
    CHECK(pixman_region32_subtract(&result, &outer, &hole));
    CHECK(pixman_region32_n_rects(&result) == 4);
    CHECK(pixman_region32_contains_point(&result, 1, 3, NULL));
    CHECK(!pixman_region32_contains_point(&result, 2, 2, NULL));
    CHECK(!pixman_region32_contains_point(&result, 6, 3, NULL));
    pixman_region32_translate(&result, -2, 3);
    box = pixman_region32_extents(&result);
    CHECK(box->x1 == -2 && box->y1 == 3 && box->x2 == 4 && box->y2 == 9);
    pixman_region32_fini(&outer); pixman_region32_fini(&hole); pixman_region32_fini(&result);
    return 0;
}

static int fractional_case(void)
{
#if PIXMAN_VERSION >= PIXMAN_VERSION_ENCODE(0, 46, 2)
    pixman_region64f_t region;
    pixman_box64f_t *box;
    pixman_region64f_init_rectf(&region, 0.25, 0.5, 2.5, 3.25);
    CHECK(pixman_region64f_contains_pointf(&region, 0.25, 0.5, NULL));
    CHECK(!pixman_region64f_contains_pointf(&region, 2.75, 0.5, NULL));
    pixman_region64f_translatef(&region, -0.5, 0.25);
    box = pixman_region64f_extents(&region);
    CHECK(box->x1 == -0.25 && box->y1 == 0.75 && box->x2 == 2.25 && box->y2 == 4.0);
    pixman_region64f_fini(&region);
    return 0;
#else
    fprintf(stderr, "public header does not expose the 0.46.2 fractional API\n");
    return 1;
#endif
}

int main(int argc, char **argv)
{
    int result;
    CHECK(argc == 3);
    if (!strcmp(argv[1], "version")) {
        printf("library=%s header=%s source=%s\n", pixman_version_string(), PIXMAN_VERSION_STRING, argv[2]);
        CHECK(!strcmp(pixman_version_string(), argv[2]));
        CHECK(!strcmp(PIXMAN_VERSION_STRING, argv[2]));
        CHECK(pixman_version() == PIXMAN_VERSION);
        result = 0;
    } else if (!strcmp(argv[1], "over")) result = over_or_mask(0);
    else if (!strcmp(argv[1], "mask")) result = over_or_mask(1);
    else if (!strcmp(argv[1], "region")) result = region_case();
    else if (!strcmp(argv[1], "fractional")) result = fractional_case();
    else result = image_case(argv[1]);
    if (!result) printf("PASS %s\n", argv[1]);
    return result;
}
