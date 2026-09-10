/* Native regression harness for CVE-2026-56000.
 * Compile the actual dispatch and tag-mapping translation units, not copies.
 * Only the allocator and external server/vendor services are test fixtures.
 */
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

static size_t allocation_size;
static int fail_allocation;
static unsigned int moves;

/* Force realloc to move so AddressSanitizer deterministically catches stale
 * pointers. A failed realloc must preserve the original allocation. */
static void *moving_realloc(void *old, size_t size)
{
    void *fresh;
    if (fail_allocation)
        return NULL;
    fresh = malloc(size);
    if (!fresh)
        abort();
    if (old) {
        memcpy(fresh, old, allocation_size < size ? allocation_size : size);
        free(old);
        moves++;
    }
    allocation_size = size;
    return fresh;
}

#include "../../../src/xorg-server/glx/vndcmds.c"
#define realloc moving_realloc
#include "../../../src/xorg-server/glx/vndservermapping.c"
#undef realloc

static GlxClientPriv tags;
static GlxServerVendor vendor;
static ClientRec test_client;
static xGLXMakeCurrentReply last_reply;
static int lose_result = Success;
static int make_result = Success;
static unsigned int replies;

int GlxErrorBase = 128;
RESTYPE idResource = 1;

/* Unused server services are link fixtures only. Abort if a tested path
 * unexpectedly reaches one instead of silently simulating success. */
ScreenInfo screenInfo;
const GlxServerExports glxServer = {0};
ExtensionEntry *GlxExtensionEntry;
struct xorg_list GlxVendorList;
Bool AddResource(XID id, RESTYPE type, void *value) { abort(); }
void FreeResourceByType(XID id, RESTYPE type, Bool skip) { abort(); }
Bool LegalNewID(XID id, ClientPtr client) { abort(); }
GlxScreenPriv *GlxGetScreen(ScreenPtr screen) { abort(); }
HashTable ht_create(int keys, int data, HashFunc hash,
                    HashCompareFunc compare, void *opaque) { abort(); }
void ht_destroy(HashTable table) { abort(); }
void *ht_add(HashTable table, const void *key) { abort(); }
void *ht_find(HashTable table, const void *key) { abort(); }
unsigned ht_generic_hash(void *opaque, const void *value, int bits) { abort(); }
int ht_generic_compare(void *opaque, const void *a, const void *b) { abort(); }

GlxClientPriv *GlxGetClientData(ClientPtr client)
{
    return &tags;
}

int dixLookupResourceByType(void **result, XID id, RESTYPE type,
                            ClientPtr client, Mask access)
{
    *result = id == 9999 ? NULL : &vendor;
    return *result ? Success : BadValue;
}

int dixLookupResourceByClass(void **result, XID id, RESTYPE type,
                             ClientPtr client, Mask access)
{
    *result = NULL;
    return BadValue;
}

int WriteToClient(ClientPtr client, int count, const void *buffer)
{
    if (count != sizeof(last_reply))
        abort();
    memcpy(&last_reply, buffer, count);
    replies++;
    return count;
}

static int make_current(ClientPtr client, GLXContextTag old_tag,
                        GLXDrawable draw, GLXDrawable read_draw,
                        GLXContextID context, GLXContextTag new_tag)
{
    /* The real vendor releases its context but leaves mapping-slot lifetime
     * to the dispatch layer. It must not free the slot in this fixture. */
    return context == None ? lose_result : make_result;
}

#define CHECK(condition) do { \
    if (!(condition)) { \
        fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #condition); \
        exit(1); \
    } \
} while (0)

static int change(GLXContextTag old_tag, GLXContextID context)
{
    CARD32 drawable = context ? 100 : None;
    return CommonMakeCurrent(&test_client,
        GlxCheckSwap(&test_client, old_tag),
        GlxCheckSwap(&test_client, drawable),
        GlxCheckSwap(&test_client, drawable),
        GlxCheckSwap(&test_client, context));
}

static GLXContextTag reply_tag(void)
{
    CHECK(last_reply.type == X_Reply);
    CHECK(last_reply.length == 0);
    return GlxCheckSwap(&test_client, last_reply.contextTag);
}

static unsigned int active_tags(void)
{
    unsigned int i, active = 0;
    for (i = 0; i < tags.contextTagCount; i++)
        active += tags.contextTags[i].vendor != NULL;
    return active;
}

static void fill(GLXContextTag ids[16])
{
    unsigned int i;
    for (i = 0; i < 16; i++) {
        CHECK(change(0, i + 1) == Success);
        ids[i] = reply_tag();
        CHECK(ids[i] != 0);
    }
    CHECK(active_tags() == 16);
}

int main(int argc, char **argv)
{
    GLXContextTag ids[16], replacement;
    GlxContextTagInfo *entry;
    unsigned int i, before;
    CHECK(argc == 2);
    vendor.glxvc.makeCurrent = make_current;
    test_client.sequence = 17;
    test_client.swapped = strcmp(argv[1], "switch-swapped") == 0;

    if (!strcmp(argv[1], "switch") || !strcmp(argv[1], "switch-swapped")) {
        fill(ids);
        CHECK(change(ids[0], 17) == Success);
        replacement = reply_tag();
        entry = GlxLookupContextTag(&test_client, replacement);
        CHECK(entry && entry->context == 17);
        CHECK(active_tags() == 16);
        for (i = 1; i < 16; i++) {
            entry = GlxLookupContextTag(&test_client, ids[i]);
            CHECK(entry && entry->context == i + 1);
            CHECK(change(ids[i], None) == Success);
        }
        CHECK(change(replacement, None) == Success);
        CHECK(active_tags() == 0);
    } else if (!strcmp(argv[1], "growth")) {
        fill(ids);
        CHECK(change(0, 17) == Success);
        CHECK(active_tags() == 17);
        CHECK(moves > 0);
        for (i = 0; i < 16; i++) {
            entry = GlxLookupContextTag(&test_client, ids[i]);
            CHECK(entry && entry->context == i + 1);
        }
    } else if (!strcmp(argv[1], "same-and-release")) {
        CHECK(change(0, 1) == Success);
        replacement = reply_tag();
        CHECK(change(replacement, 1) == Success);
        CHECK(reply_tag() == replacement && active_tags() == 1);
        CHECK(change(replacement, None) == Success);
        CHECK(reply_tag() == 0 && active_tags() == 0);
        CHECK(change(0, None) == Success);
        CHECK(reply_tag() == 0);
    } else if (!strcmp(argv[1], "lose-failure")) {
        fill(ids);
        lose_result = BadAccess;
        before = replies;
        CHECK(change(ids[0], 17) == BadAccess);
        CHECK(replies == before && active_tags() == 16);
        CHECK(GlxLookupContextTag(&test_client, ids[0])->context == 1);
    } else if (!strcmp(argv[1], "make-failure")) {
        fill(ids);
        make_result = BadMatch;
        before = replies;
        CHECK(change(ids[0], 17) == BadMatch);
        CHECK(replies == before && active_tags() == 15);
        CHECK(GlxLookupContextTag(&test_client, ids[0]) == NULL);
        for (i = 1; i < 16; i++)
            CHECK(GlxLookupContextTag(&test_client, ids[i])->context == i + 1);
    } else if (!strcmp(argv[1], "allocation-failure")) {
        fill(ids);
        fail_allocation = 1;
        before = replies;
        CHECK(change(0, 17) == BadAlloc);
        CHECK(replies == before && active_tags() == 16);
        for (i = 0; i < 16; i++)
            CHECK(GlxLookupContextTag(&test_client, ids[i])->context == i + 1);
    } else if (!strcmp(argv[1], "invalid-ids")) {
        CHECK(change(888, 1) == GlxErrorBase + GLXBadContextTag);
        CHECK(change(0, 9999) == GlxErrorBase + GLXBadContext);
        CHECK(replies == 0 && active_tags() == 0);
    } else {
        CHECK(0);
    }
    free(tags.contextTags);
    printf("PASS %s\n", argv[1]);
    return 0;
}
