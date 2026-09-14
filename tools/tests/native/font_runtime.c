/* Normal core-font loading and drawing through the built X server. */
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <stdio.h>
#include <string.h>

int main(int argc, char **argv)
{
    Display *display;
    XFontStruct *font;
    Pixmap pixmap;
    GC gc;
    XImage *image;
    int x, y, ink = 0;
    const char *text = "Font 123";
    if (argc != 3) return 2;
    display = XOpenDisplay(argv[1]);
    if (!display) return 3;
    font = XLoadQueryFont(display, argv[2]);
    if (!font) { XCloseDisplay(display); return 4; }
    if (font->ascent + font->descent <= 0 ||
        XTextWidth(font, text, (int)strlen(text)) <= 0) return 5;
    pixmap = XCreatePixmap(display, DefaultRootWindow(display), 256, 64, 1);
    gc = XCreateGC(display, pixmap, 0, NULL);
    XSetForeground(display, gc, 0);
    XFillRectangle(display, pixmap, gc, 0, 0, 256, 64);
    XSetFont(display, gc, font->fid);
    XSetForeground(display, gc, 1);
    XDrawString(display, pixmap, gc, 4, 32, text, (int)strlen(text));
    image = XGetImage(display, pixmap, 0, 0, 256, 64, 1, ZPixmap);
    if (!image) return 6;
    for (y = 0; y < 64; y++)
        for (x = 0; x < 256; x++)
            ink += XGetPixel(image, x, y) != 0;
    XDestroyImage(image);
    XFreeGC(display, gc);
    XFreePixmap(display, pixmap);
    XFreeFont(display, font);
    XCloseDisplay(display);
    if (ink <= 0 || ink == 256 * 64) return 7;
    printf("PASS core font %s ink=%d\n", argv[2], ink);
    return 0;
}
