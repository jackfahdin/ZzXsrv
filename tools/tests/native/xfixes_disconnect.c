/* CVE-2025-49177: exercise actual handlers and request macros under ASAN.
 * Only private-key registration and the reply sink are server fixtures. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../../../src/xorg-server/xfixes/disconnect.c"

int (*ProcXFixesVector[XFixesNumberRequests])(ClientPtr);
char dispatchExceptionAtReset;
static xXFixesGetClientDisconnectModeReply last_reply;
static unsigned int replies;

Bool dixRegisterPrivateKey(DevPrivateKey key, DevPrivateType type, unsigned size)
{
    if (key != ClientDisconnectPrivateKey || type != PRIVATE_CLIENT ||
        size != sizeof(ClientDisconnectRec))
        abort();
    key->initialized = TRUE;
    key->offset = 0;
    key->size = size;
    key->type = type;
    return TRUE;
}

int WriteToClient(ClientPtr client, int count, const void *buffer)
{
    if (count != sizeof(last_reply))
        abort();
    memcpy(&last_reply, buffer, sizeof(last_reply));
    replies++;
    return count;
}

#define CHECK(condition) do { if (!(condition)) { \
    fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #condition); \
    return 1; } } while (0)

int main(int argc, char **argv)
{
    ClientRec client = {0};
    ClientDisconnectRec private_data = {0};
    xXFixesSetClientDisconnectModeReq request = {0};
    xXFixesGetClientDisconnectModeReq get = {0};
    unsigned char *buffer;
    size_t bytes;
    CARD32 expected = 0x01020304;
    int result, short_request, long_request, exact_allocation, swapped;
    CHECK(argc == 2);
    swapped = strstr(argv[1], "swapped") != NULL;
    short_request = strstr(argv[1], "short") != NULL;
    long_request = strstr(argv[1], "long") != NULL;
    exact_allocation = strstr(argv[1], "bounds") != NULL;
    CHECK(XFixesClientDisconnectInit());
    client.devPrivates = (PrivatePtr)&private_data;
    client.swapped = swapped;
    client.sequence = 0x1234;
    private_data.disconnect_mode = expected;
    ProcXFixesVector[X_XFixesSetClientDisconnectMode] = ProcXFixesSetClientDisconnectMode;
    ProcXFixesVector[X_XFixesGetClientDisconnectMode] = ProcXFixesGetClientDisconnectMode;
    client.req_len = short_request ? 1 : long_request ? 3 : 2;
    request.length = client.req_len;
    request.xfixesReqType = X_XFixesSetClientDisconnectMode;
    request.disconnect_mode = 0x11223344;
    if (swapped)
        swapl(&request.disconnect_mode);
    /* The transport has already decoded client.req_len. Padding simulates
     * leftover request-buffer data; exact allocation proves the read bound. */
    bytes = exact_allocation ? 4 : 12;
    buffer = calloc(1, bytes);
    CHECK(buffer != NULL);
    memcpy(buffer, &request, bytes < sizeof(request) ? bytes : sizeof(request));
    client.requestBuffer = buffer;
    result = swapped ? SProcXFixesSetClientDisconnectMode(&client)
                     : ProcXFixesSetClientDisconnectMode(&client);
    if (short_request || long_request) {
        CHECK(result == BadLength);
        CHECK(private_data.disconnect_mode == expected);
        CHECK(memcmp(buffer, &request, bytes < sizeof(request) ? bytes : sizeof(request)) == 0);
    } else {
        CHECK(result == Success);
        expected = 0x11223344;
        CHECK(private_data.disconnect_mode == expected);
    }
    free(buffer);
    CHECK(replies == 0);
    get.xfixesReqType = X_XFixesGetClientDisconnectMode;
    client.requestBuffer = &get;
    client.req_len = sizeof(get) / 4;
    result = swapped ? SProcXFixesGetClientDisconnectMode(&client)
                     : ProcXFixesGetClientDisconnectMode(&client);
    CHECK(result == Success && replies == 1);
    if (swapped) {
        swapl(&last_reply.disconnect_mode);
        swaps(&last_reply.sequenceNumber);
    }
    CHECK(last_reply.type == X_Reply && last_reply.length == 0);
    CHECK(last_reply.disconnect_mode == expected);
    CHECK(last_reply.sequenceNumber == client.sequence);
    printf("PASS %s\n", argv[1]);
    return 0;
}
