#include <pixman.h>
#include <stdio.h>
#include <stdlib.h>

#define CHECK(x) do { if (!(x)) { fprintf(stderr, "line %d: %s\n", __LINE__, #x); return 1; } } while (0)

int main(void)
{
    int count = 0, i;
    uint32_t pixels[4] = {0xff804020, 0xff804020, 0xff804020, 0xff804020};
    uint32_t output[4] = {0};
    pixman_image_t *src, *dst;
    pixman_fixed_t *params = pixman_filter_create_separable_convolution(
        &count, pixman_fixed_1, pixman_fixed_1, PIXMAN_KERNEL_LINEAR,
        PIXMAN_KERNEL_LINEAR, PIXMAN_KERNEL_BOX, PIXMAN_KERNEL_BOX, 2, 2);
    CHECK(params && count > 4);
    src = pixman_image_create_bits(PIXMAN_a8r8g8b8, 2, 2, pixels, 8);
    dst = pixman_image_create_bits(PIXMAN_a8r8g8b8, 2, 2, output, 8);
    CHECK(src && dst);
    pixman_image_set_repeat(src, PIXMAN_REPEAT_PAD);
    CHECK(pixman_image_set_filter(src, PIXMAN_FILTER_SEPARABLE_CONVOLUTION, params, count));
    free(params);
    pixman_image_composite32(PIXMAN_OP_SRC, src, NULL, dst, 0, 0, 0, 0, 0, 0, 2, 2);
    for (i = 0; i < 4; ++i) CHECK(output[i] == 0xff804020);
    pixman_image_unref(src); pixman_image_unref(dst);
    puts("PASS convolution");
    return 0;
}
