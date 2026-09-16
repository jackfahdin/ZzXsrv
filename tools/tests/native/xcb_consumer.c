/* Normal authenticated XCB connections and Xlib interoperability. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <xcb/xcb.h>
#include <X11/Xlib.h>

#define CHECK(expr) do { if (!(expr)) { \
    fprintf(stderr, "line %d: %s\n", __LINE__, #expr); result = 1; goto done; \
} } while (0)

int main(int argc, char **argv)
{
    xcb_connection_t *connection = NULL;
    xcb_generic_error_t *error = NULL;
    xcb_get_geometry_reply_t *geometry = NULL;
    xcb_intern_atom_reply_t *atom = NULL;
    xcb_screen_iterator_t screens;
    Display *display = NULL;
    int result = 0, screen_number = 0;
    if (argc != 3) return 2;
    connection = xcb_connect(argv[1], &screen_number);
    CHECK(connection && !xcb_connection_has_error(connection));
    screens = xcb_setup_roots_iterator(xcb_get_setup(connection));
    CHECK(screen_number == 0 && screens.rem > 0);
    if (!strcmp(argv[2], "nodelay") || !strcmp(argv[2], "keepalive")) {
        int value = 0, length = sizeof(value);
        int tcp = !strcmp(argv[2], "nodelay");
        SOCKET socket = (SOCKET)(uintptr_t)xcb_get_file_descriptor(connection);
        CHECK(getsockopt(socket, tcp ? IPPROTO_TCP : SOL_SOCKET,
              tcp ? TCP_NODELAY : SO_KEEPALIVE, (char *)&value, &length) == 0);
        printf("%s=%d\n", argv[2], value);
        CHECK(value != 0);
    } else if (!strcmp(argv[2], "geometry")) {
        geometry = xcb_get_geometry_reply(connection,
            xcb_get_geometry(connection, screens.data->root), &error);
        CHECK(!error && geometry);
        CHECK(geometry->root == screens.data->root);
        CHECK(geometry->width > 0 && geometry->height > 0);
    } else if (!strcmp(argv[2], "xlib")) {
        const char name[] = "ZZ_XCB_R9_2_INTEROP";
        Atom xlib_atom;
        display = XOpenDisplay(argv[1]);
        CHECK(display != NULL);
        CHECK(DefaultRootWindow(display) == screens.data->root);
        xlib_atom = XInternAtom(display, name, False);
        CHECK(xlib_atom != None);
        atom = xcb_intern_atom_reply(connection,
            xcb_intern_atom(connection, 1, sizeof(name) - 1, name), &error);
        CHECK(!error && atom && atom->atom == xlib_atom);
    } else {
        unsigned int i, j;
        uint32_t ids[64];
        CHECK(!strcmp(argv[2], "ids"));
        for (i = 0; i < 64; ++i) {
            ids[i] = xcb_generate_id(connection);
            CHECK(ids[i] && ids[i] != UINT32_MAX);
            for (j = 0; j < i; ++j) CHECK(ids[i] != ids[j]);
        }
    }
done:
    free(error);
    free(geometry);
    free(atom);
    if (display) XCloseDisplay(display);
    if (connection) xcb_disconnect(connection);
    if (!result) puts("XCB consumer PASS");
    return result;
}
