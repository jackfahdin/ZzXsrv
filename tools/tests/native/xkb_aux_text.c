#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../../../src/xorg-server/xkb/xkbtext.c"

#define CHECK(c) do { if (!(c)) { fprintf(stderr, "FAIL %d: %s\n", __LINE__, #c); exit(1); } } while (0)
void *XNFalloc(unsigned long size) { void *p = malloc(size); CHECK(p); return p; }

int main(int argc, char **argv)
{
    const char *result;
    CHECK(argc == 2);
    if (!strcmp(argv[1], "normal-name")) {
        result = XkbVModIndexText(NULL, 1, XkbCFile);
        CHECK(!strcmp(result, "vmod_1"));
    } else if (!strcmp(argv[1], "boundary-index")) {
        result = XkbVModIndexText(NULL, XkbNumVirtualMods - 1, XkbCFile);
        CHECK(!strcmp(result, "vmod_15"));
    } else CHECK(0);
    printf("PASS %s\n", argv[1]);
    return 0;
}

__declspec(noreturn) void xkb_text_unexpected(void) { abort(); }
#pragma comment(linker, "/alternatename:NameForAtom=xkb_text_unexpected")
