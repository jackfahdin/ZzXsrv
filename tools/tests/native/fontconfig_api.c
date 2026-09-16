/* Normal public API checks for the production static Fontconfig library. */
#include <stdio.h>
#include <string.h>
#include <locale.h>
#include <fontconfig/fontconfig.h>

#define CHECK(c) do { if (!(c)) { fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #c); return 1; } } while (0)

int main(int argc, char **argv)
{
    CHECK(argc == 2);
    if (strcmp(argv[1], "version") == 0) {
        printf("Fontconfig header=%d library=%d\n", FC_VERSION, FcGetVersion());
        CHECK(FcGetVersion() == 21803);
    } else if (strcmp(argv[1], "decimal") == 0) {
        FcPattern *p;
        FcPattern *again;
        FcChar8 *name;
        double size;
        CHECK(setlocale(LC_NUMERIC, "German_Germany.1252") != NULL);
        p = FcNameParse((const FcChar8 *)"Example:size=12.5");
        CHECK(p != NULL);
        CHECK(FcPatternGetDouble(p, FC_SIZE, 0, &size) == FcResultMatch && size == 12.5);
        name = FcNameUnparse(p);
        CHECK(name && strstr((const char *)name, "12.5"));
        again = FcNameParse(name);
        CHECK(again && FcPatternGetDouble(again, FC_SIZE, 0, &size) == FcResultMatch && size == 12.5);
        FcPatternDestroy(again);
        FcStrFree(name);
        FcPatternDestroy(p);
    } else {
#if FC_VERSION >= 21803
        if (strcmp(argv[1], "constants") == 0) {
            const FcChar8 *name = FcNameGetConstantNameFrom(FC_WEIGHT, FC_WEIGHT_BOLD);
            int value;
            CHECK(name && FcNameConstant(name, &value) && value == FC_WEIGHT_BOLD);
            CHECK(FcNameGetConstantNameFrom(FC_WEIGHT, -12345) == NULL);
        } else if (strcmp(argv[1], "generic") == 0) {
            FcPattern *p = FcNameParse((const FcChar8 *)"Example:genericfamily=monospace");
            FcPattern *again;
            FcChar8 *name;
            int value;
            CHECK(p && FcPatternGetInteger(p, FC_GENERIC_FAMILY, 0, &value) == FcResultMatch);
            CHECK(value == FC_FAMILY_MONO);
            name = FcNameUnparse(p);
            CHECK(name != NULL);
            again = FcNameParse(name);
            CHECK(again && FcPatternEqual(p, again));
            FcPatternDestroy(again);
            FcStrFree(name);
            FcPatternDestroy(p);
        } else if (strcmp(argv[1], "defaults") == 0) {
            FcConfig *config = FcConfigCreate();
            FcPattern *p = FcPatternCreate();
            double size;
            CHECK(config && p);
            CHECK(FcConfigGetDefaultLangs(config) != NULL);
            CHECK(FcPatternAddDouble(p, FC_SIZE, 17.5));
            FcConfigSetDefaultSubstitute(config, p);
            CHECK(FcPatternGetDouble(p, FC_SIZE, 0, &size) == FcResultMatch && size == 17.5);
            CHECK(FcPatternGetDouble(p, FC_PIXEL_SIZE, 0, &size) == FcResultMatch && size > 0);
            FcPatternDestroy(p);
            FcConfigDestroy(config);
        } else {
            CHECK(0);
        }
#else
        CHECK(0); /* An old header/library must reject the new API checks. */
#endif
    }
    FcFini();
    printf("PASS %s\n", argv[1]);
    return 0;
}
