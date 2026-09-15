/* Exercise the public Xlib/XKB API against the shipped Windows DLL. */
#include <stdio.h>
#include <string.h>
#include <X11/Xlib.h>
#include <X11/XKBlib.h>
#include <X11/keysym.h>

#define CHECK(condition) do { if (!(condition)) { \
    fprintf(stderr, "line %d: %s\n", __LINE__, #condition); result = 1; goto done; \
} } while (0)

int main(int argc, char **argv)
{
    XkbDescPtr keyboard = NULL;
    XkbKeyTypePtr type;
    int result = 0;
    int virtual_modifier;
    if (argc != 2) return 2;
    if (!strcmp(argv[1], "keysyms")) {
        CHECK(XStringToKeysym("Greek_alpha") == XK_Greek_alpha);
        CHECK(!strcmp(XKeysymToString(XK_Greek_alpha), "Greek_alpha"));
        CHECK(XStringToKeysym("U4E2D") == 0x01004e2d);
        CHECK(!strcmp(XKeysymToString(0x01004e2d), "U4E2D"));
        goto done;
    }
    virtual_modifier = !strcmp(argv[1], "virtual") ? 3 : XkbNoModifier;
    keyboard = XkbAllocKeyboard();
    CHECK(keyboard != NULL);
    keyboard->min_key_code = 8;
    keyboard->max_key_code = 8;
    CHECK(XkbInitCanonicalKeyTypes(keyboard, XkbAllRequiredTypes,
                                   virtual_modifier) == Success);
    CHECK(keyboard->map->size_types >= XkbNumRequiredTypes);
    if (!strcmp(argv[1], "keypad") || !strcmp(argv[1], "virtual")) {
        type = &keyboard->map->types[XkbKeypadIndex];
        CHECK(type->num_levels == 2 && type->map_count == 2);
        CHECK(type->map[0].level == 1 && type->map[0].mods.mask == ShiftMask);
        CHECK(type->map[1].level == 1 && type->map[1].mods.mask == 0);
        CHECK(type->map[1].mods.vmods == (virtual_modifier == 3 ? 8 : 0));
    } else {
        CHECK(!strcmp(argv[1], "caps") || !strcmp(argv[1], "shift"));
        unsigned int entry = !strcmp(argv[1], "caps") ? 1 : 0;
        unsigned int modifier = entry ? LockMask : ShiftMask;
        type = &keyboard->map->types[XkbAlphabeticIndex];
        CHECK(type->num_levels == 2 && type->map_count == 2);
        CHECK(type->map[entry].active);
        CHECK(type->map[entry].level == 1);
        CHECK(type->map[entry].mods.mask == modifier);
        CHECK(type->map[entry].mods.real_mods == modifier);
    }
done:
    /* The product exports allocation but not XkbFreeKeyboard. Each invocation
       owns one small description for its process lifetime; no handles escape. */
    if (!result) puts("X11 consumer PASS");
    return result;
}
