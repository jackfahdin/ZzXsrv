#include <stdio.h>
#include <string.h>
#include "xcbext.h"
#include "xcb_fd_contract.h"

static union { int alignment; unsigned char bytes[256]; } storage;
static size_t allocated;
static unsigned int expected_count, calls;
static int expected_checked, failures;
static const int values[] = {101, 102, 103, 104};

void *xcb_test_allocate(size_t bytes)
{
    allocated = bytes;
    memset(storage.bytes, 0xa5, sizeof(storage.bytes));
    return storage.bytes;
}

/* Transport boundary only: validate the generated request before any I/O.
   Windows does not implement Unix FD passing, so no server is used here. */
unsigned int xcb_send_request_with_fds(xcb_connection_t *c, int flags,
    struct iovec *vector, const xcb_protocol_request_t *request,
    unsigned int count, int *fds)
{
    unsigned int i;
    (void)c; (void)vector;
    ++calls;
    if (allocated < expected_count * sizeof(int)) {
        fprintf(stderr, "requested %zu bytes; need %zu for %u descriptors\n",
                allocated, expected_count * sizeof(int), expected_count);
        ++failures;
    }
    if (count != expected_count || flags != expected_checked || !request->isvoid)
        ++failures;
    for (i = 0; i < count && i < 4; ++i)
        if (fds[i] != values[i]) ++failures;
    for (i = expected_count * sizeof(int); i < sizeof(storage.bytes); ++i)
        if (storage.bytes[i] != 0xa5) ++failures;
    return 17;
}

int main(int argc, char **argv)
{
    int checked;
    if (argc != 2) return 2;
    for (checked = 0; checked < 2; ++checked) {
        xcb_void_cookie_t cookie;
        expected_checked = checked ? XCB_REQUEST_CHECKED : 0;
        if (!strcmp(argv[1], "fixed")) {
            expected_count = 1;
            cookie = checked ? xcb_fdcontract_fixed_checked(NULL, values[0])
                             : xcb_fdcontract_fixed(NULL, values[0]);
        } else if (!strcmp(argv[1], "array")) {
            expected_count = 4;
            cookie = checked ? xcb_fdcontract_array_checked(NULL, 4, values)
                             : xcb_fdcontract_array(NULL, 4, values);
        } else if (!strcmp(argv[1], "mixed")) {
            expected_count = 3;
            cookie = checked ? xcb_fdcontract_mixed_checked(NULL, 2, values[0], values + 1)
                             : xcb_fdcontract_mixed(NULL, 2, values[0], values + 1);
        } else return 2;
        if (cookie.sequence != 17) ++failures;
    }
    if (calls != 2 || failures) return 1;
    puts("XCB FD generator PASS");
    return 0;
}
