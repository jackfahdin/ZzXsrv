#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../../../src/xorg-server/xkb/XKBGAlloc.c"

#define CHECK(c) do { if (!(c)) { fprintf(stderr, "FAIL %d: %s\n", __LINE__, #c); exit(1); } } while (0)
void *xreallocarray(void *old, size_t count, size_t size)
{
    if (size && count > SIZE_MAX / size) return NULL;
    return realloc(old, count * size);
}

int main(int argc, char **argv)
{
    XkbGeometryRec geom = {0};
    XkbSectionRec section = {0};
    XkbDoodadPtr result;
    CHECK(argc == 2);
    if (!strcmp(argv[1], "section-capacity")) {
        geom.sz_doodads = 8;
        section.sz_doodads = section.num_doodads = 1;
        section.doodads = calloc(1, sizeof(*section.doodads));
        CHECK(section.doodads);
        section.doodads[0].any.name = 11;
        result = XkbAddGeomDoodad(&geom, &section, 12);
        CHECK(result && section.sz_doodads > 1 && section.num_doodads == 2);
        CHECK(section.doodads[0].any.name == 11 && section.doodads[1].any.name == 12);
        free(section.doodads);
    } else if (!strcmp(argv[1], "global-capacity")) {
        geom.sz_doodads = geom.num_doodads = 1;
        geom.doodads = calloc(1, sizeof(*geom.doodads));
        CHECK(geom.doodads);
        geom.doodads[0].any.name = 21;
        result = XkbAddGeomDoodad(&geom, NULL, 22);
        CHECK(result && geom.sz_doodads > 1 && geom.num_doodads == 2);
        CHECK(geom.doodads[0].any.name == 21 && geom.doodads[1].any.name == 22);
        free(geom.doodads);
    } else CHECK(0);
    printf("PASS %s\n", argv[1]);
    return 0;
}
