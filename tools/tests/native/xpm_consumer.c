/* Normal XPM data through the installed header and production static library. */
#include <stdio.h>
#include <string.h>
#include <X11/xpm.h>

static int check(const XpmImage *image)
{
    const unsigned int pixels[] = {0, 1, 2, 3, 4, 0};
    unsigned int i;
    if (image->width != 3 || image->height != 2 || image->cpp != 3 ||
        image->ncolors != 5) return 1;
    for (i = 0; i < 6; ++i) if (image->data[i] != pixels[i]) return 2;
    if (strcmp(image->colorTable[0].c_color, "None") ||
        strcmp(image->colorTable[1].c_color, "#ff0000")) return 3;
    return 0;
}

int main(void)
{
    char *data[] = {"3 2 5 3", "aaa c None", "bbb c #ff0000", "ccc c #00ff00",
                    "ddd c #0000ff", "eee c #ffffff", "aaabbbccc", "dddeeeaaa"};
    XpmImage first = {0}, second = {0}, third = {0};
    char **serialized = NULL;
    char *buffer = NULL;
    int status = 1;
    if (XpmCreateXpmImageFromData(data, &first, NULL) != XpmSuccess || check(&first)) goto done;
    status = 2;
    if (XpmCreateDataFromXpmImage(&serialized, &first, NULL) != XpmSuccess) goto done;
    status = 3;
    if (XpmCreateXpmImageFromData(serialized, &second, NULL) != XpmSuccess || check(&second)) goto done;
    status = 4;
    if (XpmWriteFileFromXpmImage("normal.xpm", &second, NULL) != XpmSuccess) goto done;
    status = 5;
    if (XpmReadFileToXpmImage("normal.xpm", &third, NULL) != XpmSuccess || check(&third)) goto done;
    status = 6;
    if (XpmReadFileToBuffer("normal.xpm", &buffer) != XpmSuccess || !strstr(buffer, "XPM")) goto done;
    puts("XPM pixels and file roundtrip PASS");
    status = 0;
done:
    if (status) fprintf(stderr, "XPM consumer failed at stage %d\n", status);
    XpmFree(buffer);
    XpmFree(serialized);
    XpmFreeXpmImage(&third);
    XpmFreeXpmImage(&second);
    XpmFreeXpmImage(&first);
    return status;
}
