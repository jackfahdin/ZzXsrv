/* Exercise the real input parser with an in-memory transport, without sockets. */
#include "os/io.c"

static const char *incoming;
static int incoming_size;
volatile char isItTimeToYield;
struct ospoll *server_poll;
long maxBigRequestSize = 4194303;

int _XSERVTransRead(XtransConnInfo conn, char *buffer, int size)
{
    int count = min(size, incoming_size);
    if (!count) {
        errno = EWOULDBLOCK;
        return -1;
    }
    memcpy(buffer, incoming, count);
    incoming += count;
    incoming_size -= count;
    return count;
}

void mark_client_not_ready(ClientPtr client) { }
void ospoll_reset_events(struct ospoll *poll, int fd) { }

/* Link fixtures for unrelated output/teardown entry points in the same file.
 * Abort if a parser test unexpectedly reaches any of them. */
ClientPtr serverClient;
struct xorg_list output_pending_clients;
Bool NewOutputPending;
void _CallCallbacks(CallbackListPtr *list, void *data) { abort(); }
void ErrorF(const char *format, ...) { abort(); }
void xorg_backtrace(void) { abort(); }
int in_input_thread(void) { abort(); return 0; }
void MarkClientException(ClientPtr client) { abort(); }
void mark_client_ready(ClientPtr client) { abort(); }
int _XSERVTransWritev(XtransConnInfo conn, struct iovec *vec, int count)
{ abort(); return -1; }
void CloseDownFileDescriptor(OsCommPtr connection) { abort(); }
void ospoll_listen(struct ospoll *poll, int fd, int events) { abort(); }
Bool listen_to_client(ClientPtr client) { abort(); return FALSE; }

static int check(int condition, const char *message)
{
    if (!condition) fprintf(stderr, "FAIL %s\n", message);
    return condition;
}

int main(int argc, char **argv)
{
    ClientRec client = {0};
    OsCommRec connection = {0};
    ConnectionInput input = {0};
    xBigReq request = {0};
    char storage[64] = {0};
    const char *name = argc > 1 ? argv[1] : "";
    Bool swapped = strstr(name, "swapped") != NULL;
    int result, ok = 1;

    client.osPrivate = &connection;
    client.swapped = swapped;
    client.big_requests = TRUE;
    connection.input = &input;
    connection.trans_conn = (XtransConnInfo) &connection;
    input.buffer = input.bufptr = storage;
    input.size = sizeof(storage);
    request.reqType = X_NoOperation;

    if (strncmp(name, "ignore", 6) == 0) {
        input.bufcnt = input.size;
        input.ignoreBytes = input.size + (strstr(name, "pending") ? 4 : 0);
        result = ReadRequestFromClient(&client);
        ok &= check(result == 0, "discard produces no request");
        if (strstr(name, "pending")) {
            ok &= check(input.ignoreBytes == 4, "remaining discard count");
            ok &= check(AvailableInput == NULL, "pending discard retains ownership");
        } else {
            ok &= check(input.ignoreBytes == 0, "discard complete");
            ok &= check(AvailableInput == &connection, "empty buffer reusable");
        }
    } else if (strncmp(name, "oversize", 8) == 0) {
        CARD32 words = ((CARD32) MAXINT >> 2) + 1;
        request.length = swapped ? bswap_32(words) : words;
        if (strstr(name, "read")) {
            incoming = (const char *) &request;
            incoming_size = sizeof(request);
        } else {
            memcpy(storage, &request, sizeof(request));
            input.bufcnt = sizeof(request);
        }
        timesThisConnection = 3;
        result = ReadRequestFromClient(&client);
        ok &= check(result == -1, "unrepresentable byte count terminates client");
        ok &= check(timesThisConnection == 0, "terminal return resets scheduling count");
        ok &= check(input.buffer == storage, "oversize does not reallocate");
    } else if (strncmp(name, "limit", 5) == 0) {
        CARD32 words = (CARD32) MAXINT >> 2;
        request.length = swapped ? bswap_32(words) : words;
        memcpy(storage, &request, sizeof(request));
        input.bufcnt = sizeof(request);
        result = ReadRequestFromClient(&client);
        ok &= check(result == (int) (words * 4), "representable length keeps BadLength path");
        ok &= check(input.ignoreBytes == words * 4 - sizeof(request), "excess data is discarded");
        ok &= check(input.buffer == storage, "server limit checked before allocation");
    } else if (strncmp(name, "big", 3) == 0) {
        request.length = swapped ? bswap_32(2) : 2;
        memcpy(storage, &request, sizeof(request));
        input.bufcnt = sizeof(request);
        result = ReadRequestFromClient(&client);
        ok &= check(result == sizeof(xBigReq), "valid big request accepted");
        ok &= check(client.req_len == 1, "big length excludes extended header");
        ok &= check(((xReq *) client.requestBuffer)->reqType == X_NoOperation,
                    "big opcode preserved");
    } else if (strncmp(name, "normal", 6) == 0) {
        xReq normal = {X_NoOperation, 0, 1};
        if (swapped) normal.length = bswap_16(normal.length);
        memcpy(storage, &normal, sizeof(normal));
        input.bufcnt = sizeof(normal);
        result = ReadRequestFromClient(&client);
        ok &= check(result == sizeof(normal), "normal request accepted");
        ok &= check(client.req_len == 1, "normal request word count");
        ok &= check(client.requestBuffer == storage, "normal request buffer");
    } else {
        fprintf(stderr, "unknown test case\n");
        return 2;
    }
    if (ok) printf("PASS %s\n", name);
    return ok ? 0 : 1;
}
