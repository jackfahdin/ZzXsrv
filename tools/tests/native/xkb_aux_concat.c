#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int fail_realloc;
static void *controlled_realloc(void *ptr, size_t size)
{
    if (fail_realloc) return NULL;
    return realloc(ptr, size);
}

__declspec(noreturn) void xkb_unexpected_service(void) { abort(); }
#pragma comment(linker, "/alternatename:Xstrdup=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:xreallocarray=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:strlcpy=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:ErrorF=xkb_unexpected_service")
#define realloc controlled_realloc
#include "../../../src/xorg-server/xkb/maprules.c"
#undef realloc

#define CHECK(c) do { if (!(c)) { fprintf(stderr, "FAIL %d: %s\n", __LINE__, #c); exit(1); } } while (0)

int main(int argc, char **argv)
{
    char *first, *result;
    CHECK(argc == 2);
    if (!strcmp(argv[1], "null-first")) {
        CHECK(_Concat(NULL, "x") == NULL);
    } else {
        first = malloc(8);
        CHECK(first);
        strcpy(first, !strcmp(argv[1], "empty") ? "" : "old");
        if (!strcmp(argv[1], "null-second")) {
            result = _Concat(first, NULL);
            CHECK(result == first && !strcmp(result, "old"));
        } else if (!strcmp(argv[1], "realloc-failure")) {
            fail_realloc = 1;
            result = _Concat(first, "new");
            CHECK(result == first && !strcmp(result, "old"));
        } else if (!strcmp(argv[1], "empty")) {
            result = _Concat(first, "tail");
            CHECK(result && !strcmp(result, "tail"));
        } else if (!strcmp(argv[1], "normal")) {
            result = _Concat(first, "new");
            CHECK(result && !strcmp(result, "oldnew"));
        } else CHECK(0);
        free(result);
    }
    printf("PASS %s\n", argv[1]);
    return 0;
}
