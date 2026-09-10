/* Compile the real protocol handler and public cursor constructor.
 * Server resources, timers and private storage are bounded test fixtures. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "../../../src/xorg-server/render/animcur.c"
#include "../../../src/xorg-server/render/render.c"

#define CHECK(c) do { if (!(c)) { fprintf(stderr, "FAIL %d: %s\n", __LINE__, #c); exit(1); } } while (0)

ScreenInfo screenInfo;
ClientPtr serverClient;
PaddingInfo PixmapWidthPaddingInfo[33];
Bool noPanoramiXExtension;
char *ConnectionInfo;
DevPrivateKeyRec PictureScreenPrivateKeyRec;
RESTYPE PictureType, PictFormatType, GlyphSetType, XRC_DRAWABLE, XRT_WINDOW;
int PanoramiXNumScreens;
static ClientRec test_client;
static CursorRec source_cursor;
static CursorBits source_bits;
static CursorPtr registered_cursor;
static unsigned allocations, lookups, registrations, timers;
static int allocation_failure, lookup_error, security_error;
static int timer_token;
CursorPtr RefCursor(CursorPtr cursor) { cursor->refcnt++; return cursor; }

int dixPrivatesSize(DevPrivateType type) { CHECK(type == PRIVATE_CURSOR); return 0; }
void _dixInitPrivates(PrivatePtr *p, void *addr, DevPrivateType type)
{ CHECK(type == PRIVATE_CURSOR); *p = addr; }
void _dixFiniPrivates(PrivatePtr p, DevPrivateType type) { CHECK(type == PRIVATE_CURSOR); }
Bool LegalNewID(XID id, ClientPtr client) { return id == 123; }
void *xreallocarray(void *old, size_t n, size_t size)
{ CHECK(!old); allocations++; return allocation_failure ? NULL : calloc(n ? n : 1, size); }
int dixLookupResourceByType(void **out, XID id, RESTYPE type, ClientPtr client, Mask access)
{
    CHECK(type == X11_RESTYPE_CURSOR && access == DixReadAccess);
    lookups++;
    if (lookup_error) return lookup_error;
    CHECK(id == 456);
    *out = &source_cursor;
    return Success;
}
Bool AddResource(XID id, RESTYPE type, void *value)
{ CHECK(id == 123 && type == X11_RESTYPE_CURSOR); registrations++; registered_cursor = value; return TRUE; }
OsTimerPtr TimerSet(OsTimerPtr timer, int flags, CARD32 millis, OsTimerCallback callback, void *arg)
{ CHECK(!timer && !flags && !millis && callback && !arg); timers++; return (OsTimerPtr)&timer_token; }
void TimerFree(OsTimerPtr timer) { CHECK(timer == (OsTimerPtr)&timer_token); timers--; }
int XaceHookResourceAccess(ClientPtr client, XID id, RESTYPE type, void *value, RESTYPE parent_type, void *parent, Mask access)
{ CHECK(id == 123 && type == X11_RESTYPE_CURSOR && access == DixCreateAccess); return security_error; }

static void release_cursor(CursorPtr cursor, int n)
{
    AnimCurPtr ac = GetAnimCur(cursor);
    CHECK(ac->nelt == n && cursor->id == 123);
    CHECK(cursor->foreRed == 17 && cursor->backBlue == 29);
    for (int i = 0; i < n; i++) {
        CHECK(ac->elts[i].pCursor == &source_cursor && ac->elts[i].delay == (CARD32)(10 + i));
        source_cursor.refcnt--;
    }
    TimerFree(ac->timer);
    animCursorBits.refcnt--;
    free(cursor);
    CHECK(source_cursor.refcnt == 1 && timers == 0);
}

static int protocol(int n)
{
    struct { xRenderCreateAnimCursorReq header; xAnimCursorElt elts[2]; } req = {0};
    req.header.cid = 123;
    for (int i = 0; i < n; i++) { req.elts[i].cursor = 456; req.elts[i].delay = 10 + i; }
    test_client.requestBuffer = &req;
    test_client.req_len = bytes_to_int32(sizeof(req.header)) + 2 * n;
    return ProcRenderCreateAnimCursor(&test_client);
}

int main(int argc, char **argv)
{
    CHECK(argc == 2);
    source_cursor.bits = &source_bits;
    source_cursor.refcnt = 1;
    source_cursor.foreRed = 17;
    source_cursor.backBlue = 29;
    if (!strcmp(argv[1], "empty-protocol")) {
        allocation_failure = 1;
        CHECK(protocol(0) == BadValue);
        CHECK(allocations == 0 && lookups == 0 && registrations == 0);
    } else if (!strcmp(argv[1], "zero-public") || !strcmp(argv[1], "negative-public")) {
        CursorPtr cursors[1] = {&source_cursor}, result = NULL;
        CARD32 delays[1] = {10};
        /* Backing storage stays valid even on the old implementation. The
         * regression is acceptance of a nonpositive count, not a fixture fault. */
        CHECK(AnimCursorCreate(cursors, delays, argv[1][0] == 'z' ? 0 : -1, &result, &test_client, 123) == BadValue);
        CHECK(result == NULL);
        CHECK(timers == 0);
    } else if (!strcmp(argv[1], "one-public") || !strcmp(argv[1], "two-public")) {
        int n = argv[1][0] == 'o' ? 1 : 2;
        CursorPtr cursors[2] = {&source_cursor, &source_cursor}, result = NULL;
        CARD32 delays[2] = {10, 11};
        CHECK(AnimCursorCreate(cursors, delays, n, &result, &test_client, 123) == Success);
        CHECK(source_cursor.refcnt == 1 + n);
        release_cursor(result, n);
    } else if (!strcmp(argv[1], "valid-protocol")) {
        CHECK(protocol(2) == Success);
        CHECK(allocations == 1 && lookups == 2 && registrations == 1);
        release_cursor(registered_cursor, 2);
    } else if (!strcmp(argv[1], "allocation-error")) {
        allocation_failure = 1;
        CHECK(protocol(1) == BadAlloc && lookups == 0 && registrations == 0);
    } else if (!strcmp(argv[1], "lookup-error")) {
        lookup_error = BadCursor;
        CHECK(protocol(1) == BadCursor && lookups == 1 && registrations == 0 && timers == 0);
    } else if (!strcmp(argv[1], "security-error")) {
        security_error = BadAccess;
        CHECK(protocol(1) == BadAccess && registrations == 0 && timers == 0 && source_cursor.refcnt == 1);
    } else if (!strcmp(argv[1], "bad-length")) {
        xRenderCreateAnimCursorReq req = {0};
        req.cid = 123;
        test_client.requestBuffer = &req;
        test_client.req_len = bytes_to_int32(sizeof(req)) - 1;
        CHECK(ProcRenderCreateAnimCursor(&test_client) == BadLength);
        test_client.req_len = bytes_to_int32(sizeof(req)) + 1;
        CHECK(ProcRenderCreateAnimCursor(&test_client) == BadLength);
        CHECK(allocations == 0 && lookups == 0);
    } else { CHECK(0); }
    printf("PASS %s\n", argv[1]);
    return 0;
}

/* MSVC x64 link fixtures for unrelated server entrypoints retained by the
 * complete production dispatch tables. Reaching any is an immediate failure. */
__declspec(noreturn) void render_unexpected_service(void) { abort(); }
#pragma comment(linker, "/alternatename:AddExtension=render_unexpected_service")
#pragma comment(linker, "/alternatename:AddGlyph=render_unexpected_service")
#pragma comment(linker, "/alternatename:AddTraps=render_unexpected_service")
#pragma comment(linker, "/alternatename:AllocARGBCursor=render_unexpected_service")
#pragma comment(linker, "/alternatename:AllocateGlyph=render_unexpected_service")
#pragma comment(linker, "/alternatename:AllocateGlyphSet=render_unexpected_service")
#pragma comment(linker, "/alternatename:ChangePicture=render_unexpected_service")
#pragma comment(linker, "/alternatename:CompositeGlyphs=render_unexpected_service")
#pragma comment(linker, "/alternatename:CompositePicture=render_unexpected_service")
#pragma comment(linker, "/alternatename:CompositeRects=render_unexpected_service")
#pragma comment(linker, "/alternatename:CompositeTrapezoids=render_unexpected_service")
#pragma comment(linker, "/alternatename:CompositeTriangles=render_unexpected_service")
#pragma comment(linker, "/alternatename:CompositeTriFan=render_unexpected_service")
#pragma comment(linker, "/alternatename:CompositeTriStrip=render_unexpected_service")
#pragma comment(linker, "/alternatename:CreateConicalGradientPicture=render_unexpected_service")
#pragma comment(linker, "/alternatename:CreateLinearGradientPicture=render_unexpected_service")
#pragma comment(linker, "/alternatename:CreateNewResourceType=render_unexpected_service")
#pragma comment(linker, "/alternatename:CreatePicture=render_unexpected_service")
#pragma comment(linker, "/alternatename:CreateRadialGradientPicture=render_unexpected_service")
#pragma comment(linker, "/alternatename:CreateSolidPicture=render_unexpected_service")
#pragma comment(linker, "/alternatename:DeleteGlyph=render_unexpected_service")
#pragma comment(linker, "/alternatename:dixDestroyPixmap=render_unexpected_service")
#pragma comment(linker, "/alternatename:dixLookupDrawable=render_unexpected_service")
#pragma comment(linker, "/alternatename:dixLookupResourceByClass=render_unexpected_service")
#pragma comment(linker, "/alternatename:dixRegisterPrivateKey=render_unexpected_service")
#pragma comment(linker, "/alternatename:FakeClientID=render_unexpected_service")
#pragma comment(linker, "/alternatename:FindGlyph=render_unexpected_service")
#pragma comment(linker, "/alternatename:FindGlyphByHash=render_unexpected_service")
#pragma comment(linker, "/alternatename:FreeCursor=render_unexpected_service")
#pragma comment(linker, "/alternatename:FreeGlyph=render_unexpected_service")
#pragma comment(linker, "/alternatename:FreePicture=render_unexpected_service")
#pragma comment(linker, "/alternatename:FreeScratchPixmapHeader=render_unexpected_service")
#pragma comment(linker, "/alternatename:GetScratchPixmapHeader=render_unexpected_service")
#pragma comment(linker, "/alternatename:HashGlyph=render_unexpected_service")
#pragma comment(linker, "/alternatename:IsFloating=render_unexpected_service")
#pragma comment(linker, "/alternatename:PictureFinishInit=render_unexpected_service")
#pragma comment(linker, "/alternatename:PictureMatchFormat=render_unexpected_service")
#pragma comment(linker, "/alternatename:PictureMatchVisual=render_unexpected_service")
#pragma comment(linker, "/alternatename:ResizeGlyphSet=render_unexpected_service")
#pragma comment(linker, "/alternatename:SetGlyphPicture=render_unexpected_service")
#pragma comment(linker, "/alternatename:SetPictureClipRects=render_unexpected_service")
#pragma comment(linker, "/alternatename:SetPictureFilter=render_unexpected_service")
#pragma comment(linker, "/alternatename:SetPictureTransform=render_unexpected_service")
#pragma comment(linker, "/alternatename:SetResourceTypeErrorValue=render_unexpected_service")
#pragma comment(linker, "/alternatename:StandardMinorOpcode=render_unexpected_service")
#pragma comment(linker, "/alternatename:SwapLongs=render_unexpected_service")
#pragma comment(linker, "/alternatename:SwapShorts=render_unexpected_service")
#pragma comment(linker, "/alternatename:TimerCancel=render_unexpected_service")
#pragma comment(linker, "/alternatename:WriteToClient=render_unexpected_service")
#pragma comment(linker, "/alternatename:XineramaDeleteResource=render_unexpected_service")
