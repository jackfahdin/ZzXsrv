/* Exercise the actual RANDR provider implementation. Only allocation is
 * bounded: requests over 64 bytes fail instead of allocating gigabytes.
 * Removing the MAXINT guard must change overflow results to BadAlloc.
 * Small success cases retain real malloc/memcpy/free and property storage. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>

static unsigned allocation_calls;
static size_t allocation_size;
static void *created_property;
static unsigned property_frees;
static void *tracked_calloc(size_t count, size_t size)
{
    created_property = calloc(count, size);
    return created_property;
}
static void tracked_free(void *ptr)
{
    if (ptr && ptr == created_property)
        property_frees++;
    free(ptr);
}
static void *bounded_malloc(size_t size)
{
    allocation_calls++;
    allocation_size = size;
    return size > 64 ? NULL : malloc(size ? size : 1);
}

#define malloc bounded_malloc
#define calloc tracked_calloc
#define free tracked_free
#include "../../../src/xorg-server/randr/rrproviderproperty.c"
#undef malloc
#undef calloc
#undef free

#define CHECK(c) do { if (!(c)) { fprintf(stderr, "FAIL %d: %s\n", __LINE__, #c); exit(1); } } while (0)

DevPrivateKeyRec rrPrivKeyRec;
int RREventBase;
RESTYPE RREventType;
RESTYPE RRProviderType;
ClientPtr serverClient;
TimeStamp currentTime;
volatile char dispatchException;

/* None of these services should be reached with sendevent=FALSE. */
__declspec(noreturn) void randr_unexpected_service(void) { abort(); }
#pragma comment(linker, "/alternatename:WalkTree=randr_unexpected_service")
#pragma comment(linker, "/alternatename:dixLookupResourceByType=randr_unexpected_service")
#pragma comment(linker, "/alternatename:WriteEventsToClient=randr_unexpected_service")
#pragma comment(linker, "/alternatename:WriteToClient=randr_unexpected_service")
#pragma comment(linker, "/alternatename:xreallocarray=randr_unexpected_service")
#pragma comment(linker, "/alternatename:SwapLongs=randr_unexpected_service")
#pragma comment(linker, "/alternatename:SwapShorts=randr_unexpected_service")
#pragma comment(linker, "/alternatename:UpdateCurrentTime=randr_unexpected_service")
#pragma comment(linker, "/alternatename:ValidAtom=randr_unexpected_service")
#pragma comment(linker, "/alternatename:Swap32Write=randr_unexpected_service")

int main(int argc, char **argv)
{
    ScreenRec screen = {0};
    rrScrPrivRec screen_private = {0};
    rrScrPrivPtr private_pointer = &screen_private;
    RRProviderRec provider = {0};
    RRPropertyRec property = {0};
    RRPropertyRec snapshot;
    const unsigned char input[8] = {0x51, 0x52, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58};
    const unsigned char original[8] = {0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18};
    RRPropertyValuePtr selected;
    unsigned long len;
    int format, mode, result;
    Bool pending;
    CHECK(argc == 5);
    format = atoi(argv[2]);
    CHECK(format == 8 || format == 16 || format == 32);
    mode = atoi(argv[3]);
    CHECK(mode == PropModeReplace || mode == PropModeAppend || mode == PropModePrepend);
    pending = atoi(argv[4]);
    rrPrivKeyRec.initialized = TRUE;
    screen.devPrivates = (void *)&private_pointer;
    provider.pScreen = &screen;
    provider.properties = &property;
    property.propertyName = 41;
    property.is_pending = TRUE;
    property.current.type = property.pending.type = 42;
    property.current.format = property.pending.format = (short)format;
    property.current.size = property.pending.size = 2;
    property.current.data = malloc(8);
    property.pending.data = malloc(8);
    CHECK(property.current.data && property.pending.data);
    memcpy(property.current.data, original, 8);
    memcpy(property.pending.data, original, 8);
    selected = pending ? &property.pending : &property.current;

    /* Literal limits are independently derived from signed 32-bit bytes. */
    unsigned long limit = format == 8 ? 2147483647UL :
                          format == 16 ? 1073741823UL : 536870911UL;
    if (!strcmp(argv[1], "new_overflow")) {
        result = RRChangeProviderProperty(&provider, 99, 42, format, mode,
                                          limit + 1, (void *)input, FALSE, pending);
        CHECK(result == BadValue);
        CHECK(created_property != NULL && property_frees == 1);
        CHECK(allocation_calls == 0);
        CHECK(provider.properties == &property && property.next == NULL);
        CHECK(!provider.pendingProperties);
        CHECK(!memcmp(property.current.data, original, 8));
        CHECK(!memcmp(property.pending.data, original, 8));
        free(property.current.data);
        free(property.pending.data);
        printf("PASS %s format=%d mode=%d pending=%d\n", argv[1], format, mode, pending);
        return 0;
    }
    if (!strcmp(argv[1], "overflow")) {
        len = mode == PropModeReplace ? limit + 1 : limit - 1;
    } else if (!strcmp(argv[1], "boundary")) {
        len = mode == PropModeReplace ? limit : limit - 2;
    } else if (!strcmp(argv[1], "valid")) {
        len = 2;
    } else if (!strcmp(argv[1], "zero")) {
        len = 0;
    } else { CHECK(0); return 1; }
    snapshot = property;
    result = RRChangeProviderProperty(&provider, 41, 42, format, mode,
                                      len, (void *)input, FALSE, pending);
    if (!strcmp(argv[1], "overflow") || !strcmp(argv[1], "boundary")) {
        if (!strcmp(argv[1], "overflow")) {
            CHECK(result == BadValue);
            CHECK(allocation_calls == 0);
        } else {
            CHECK(result == BadAlloc);
            CHECK(allocation_calls == 1);
            CHECK(allocation_size == (format == 8 ? 2147483647ULL :
                                      format == 16 ? 2147483646ULL : 2147483644ULL));
        }
        CHECK(!memcmp(&property, &snapshot, sizeof(property)));
        CHECK(!memcmp(property.current.data, original, 8));
        CHECK(!memcmp(property.pending.data, original, 8));
        CHECK(provider.properties == &property && !provider.pendingProperties);
    } else {
        CHECK(result == Success);
        CHECK(provider.properties == &property);
        CHECK(provider.pendingProperties == pending);
        CHECK(selected->format == format && selected->type == 42);
        CHECK(!memcmp(pending ? property.current.data : property.pending.data, original, 8));
        if (len) {
            size_t bytes = format / 4; /* two elements */
            CHECK(allocation_calls == 1);
            CHECK(allocation_size == (mode == PropModeReplace ? bytes : 2 * bytes));
            if (mode == PropModeReplace) {
                CHECK(!memcmp(selected->data, input, bytes));
            } else if (mode == PropModeAppend) {
                CHECK(!memcmp(selected->data, original, bytes));
                CHECK(!memcmp((char *)selected->data + bytes, input, bytes));
            } else {
                CHECK(!memcmp(selected->data, input, bytes));
                CHECK(!memcmp((char *)selected->data + bytes, original, bytes));
            }
        } else if (mode == PropModeReplace) {
            CHECK(selected->size == 0 && allocation_calls == 1 && allocation_size == 0);
        } else {
            CHECK(!memcmp(&property, &snapshot, sizeof(property)) && allocation_calls == 0);
        }
    }
    free(property.current.data);
    free(property.pending.data);
    printf("PASS %s format=%d mode=%d pending=%d\n", argv[1], format, mode, pending);
    return 0;
}
