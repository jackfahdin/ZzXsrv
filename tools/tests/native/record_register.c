/* Real RECORD validation with small local buffers, no server or network. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>
#include "../../../src/xorg-server/record/record.c"

#define CHECK(c) do { if (!(c)) { fprintf(stderr, "FAIL %d: %s\n", __LINE__, #c); exit(1); } } while (0)
int LimitClients = 256;
ClientPtr clients[MAXCLIENTS];
CallbackListPtr ReplyCallback, FlushCallback, EventCallback, DeviceEventCallback, ClientStateCallback;
int currentMaxClients;
InputInfo inputInfo;
EventSwapPtr EventSwapVector[128];
Bool noPanoramiXExtension;
ScreenInfo screenInfo;

int dixLookupResourceByClass(void **out, XID id, RESTYPE type, ClientPtr client, Mask access) { abort(); }

int main(int argc, char **argv)
{
    ClientRec client = {0};
    RecordContextRec context = {0};
    /* Largest real body is 2048 client selectors plus one range (8 KiB). */
    unsigned char *buffer = calloc(1, sz_xRecordRegisterClientsReq + 2048 * 4 + sz_xRecordRange);
    xRecordRegisterClientsReq *req = (void *)buffer;
    XID *selectors = (void *)(req + 1);
    CHECK(argc == 2 && buffer);
    client.req_len = bytes_to_int32(sz_xRecordRegisterClientsReq);
    if (!strcmp(argv[1], "client-limit")) {
        req->nClients = LimitClients + 1;
        CHECK(RecordSanityCheckRegisterClients(&context, &client, req) == BadValue);
    } else if (!strcmp(argv[1], "range-limit")) {
        req->nRanges = INT_MAX / sz_xRecordRange + 1;
        CHECK(RecordSanityCheckRegisterClients(&context, &client, req) == BadValue);
    } else if (!strcmp(argv[1], "combined-limit")) {
        req->nClients = LimitClients;
        req->nRanges = (INT_MAX - 4 * LimitClients) / sz_xRecordRange + 1;
        CHECK(RecordSanityCheckRegisterClients(&context, &client, req) == BadValue);
    } else if (!strcmp(argv[1], "range-boundary")) {
        req->nClients = LimitClients;
        req->nRanges = (INT_MAX - 4 * LimitClients) / sz_xRecordRange;
        CHECK(RecordSanityCheckRegisterClients(&context, &client, req) == BadLength);
    } else if (!strcmp(argv[1], "valid-empty")) {
        CHECK(RecordSanityCheckRegisterClients(&context, &client, req) == Success);
    } else if (!strcmp(argv[1], "valid-normal") || !strcmp(argv[1], "valid-limit")) {
        if (!strcmp(argv[1], "valid-limit")) LimitClients = 2048;
        req->nClients = !strcmp(argv[1], "valid-limit") ? LimitClients : 1;
        req->nRanges = 1;
        req->elementHeader = XRecordFromClientTime | XRecordFromServerTime;
        for (unsigned i = 0; i < req->nClients; i++) selectors[i] = XRecordAllClients;
        xRecordRange *range = (void *)(selectors + req->nClients);
        range->coreRequestsFirst = 1;
        range->coreRequestsLast = 127;
        range->clientStarted = xTrue;
        client.req_len += req->nClients + bytes_to_int32(sz_xRecordRange);
        CHECK(RecordSanityCheckRegisterClients(&context, &client, req) == Success);
    } else if (!strcmp(argv[1], "bad-header")) {
        req->elementHeader = 0x80;
        CHECK(RecordSanityCheckRegisterClients(&context, &client, req) == BadValue && client.errorValue == 0x80);
    } else if (!strcmp(argv[1], "bad-range")) {
        req->nRanges = 1;
        client.req_len += bytes_to_int32(sz_xRecordRange);
        xRecordRange *range = (void *)(req + 1);
        range->coreRequestsFirst = 2;
        range->coreRequestsLast = 1;
        CHECK(RecordSanityCheckRegisterClients(&context, &client, req) == BadValue && client.errorValue == 2);
    } else if (!strcmp(argv[1], "bad-length")) {
        req->nClients = 1;
        CHECK(RecordSanityCheckRegisterClients(&context, &client, req) == BadLength);
    } else if (!strcmp(argv[1], "swapped-short-clients") || !strcmp(argv[1], "swapped-short-ranges")) {
        if (!strcmp(argv[1], "swapped-short-clients")) req->nClients = 1;
        else req->nRanges = 1;
        swapl(&req->nClients);
        swapl(&req->nRanges);
        CHECK(SwapCreateRegister(&client, req) == BadLength);
    } else if (!strcmp(argv[1], "swapped-valid")) {
        req->context = 123;
        req->nClients = 1;
        req->nRanges = 1;
        selectors[0] = XRecordAllClients;
        xRecordRange *range = (void *)(selectors + 1);
        range->extRequestsMajorFirst = range->extRequestsMajorLast = 128;
        range->extRequestsMinorFirst = 0x1234;
        range->extRequestsMinorLast = 0x5678;
        swapl(&req->context); swapl(&req->nClients); swapl(&req->nRanges); swapl(&selectors[0]);
        swaps(&range->extRequestsMinorFirst); swaps(&range->extRequestsMinorLast);
        client.req_len += 1 + bytes_to_int32(sz_xRecordRange);
        CHECK(SwapCreateRegister(&client, req) == Success);
        CHECK(req->context == 123 && selectors[0] == XRecordAllClients);
        CHECK(range->extRequestsMinorFirst == 0x1234 && range->extRequestsMinorLast == 0x5678);
        CHECK(RecordSanityCheckRegisterClients(&context, &client, req) == Success);
    } else { CHECK(0); }
    free(buffer);
    printf("PASS %s\n", argv[1]);
    return 0;
}

/* Unrelated server services retained by production dispatch tables. */
__declspec(noreturn) void record_unexpected_service(void) { abort(); }
#pragma comment(linker, "/alternatename:AddCallback=record_unexpected_service")
#pragma comment(linker, "/alternatename:AddExtension=record_unexpected_service")
#pragma comment(linker, "/alternatename:AddResource=record_unexpected_service")
#pragma comment(linker, "/alternatename:AttendClient=record_unexpected_service")
#pragma comment(linker, "/alternatename:CreateNewResourceType=record_unexpected_service")
#pragma comment(linker, "/alternatename:DeleteCallback=record_unexpected_service")
#pragma comment(linker, "/alternatename:dixLookupResourceByType=record_unexpected_service")
#pragma comment(linker, "/alternatename:dixRegisterPrivateKey=record_unexpected_service")
#pragma comment(linker, "/alternatename:EventToCore=record_unexpected_service")
#pragma comment(linker, "/alternatename:EventToXI=record_unexpected_service")
#pragma comment(linker, "/alternatename:GetTimeInMillis=record_unexpected_service")
#pragma comment(linker, "/alternatename:IgnoreClient=record_unexpected_service")
#pragma comment(linker, "/alternatename:IsMaster=record_unexpected_service")
#pragma comment(linker, "/alternatename:LegalNewID=record_unexpected_service")
#pragma comment(linker, "/alternatename:RecordCreateSet=record_unexpected_service")
#pragma comment(linker, "/alternatename:RecordSetMemoryRequirements=record_unexpected_service")
#pragma comment(linker, "/alternatename:ResourceClientBits=record_unexpected_service")
#pragma comment(linker, "/alternatename:SetCriticalOutputPending=record_unexpected_service")
#pragma comment(linker, "/alternatename:SetResourceTypeErrorValue=record_unexpected_service")
#pragma comment(linker, "/alternatename:StandardMinorOpcode=record_unexpected_service")
#pragma comment(linker, "/alternatename:SwapConnSetupInfo=record_unexpected_service")
#pragma comment(linker, "/alternatename:SwapConnSetupPrefix=record_unexpected_service")
#pragma comment(linker, "/alternatename:SwapLongs=record_unexpected_service")
#pragma comment(linker, "/alternatename:WriteToClient=record_unexpected_service")
#pragma comment(linker, "/alternatename:xreallocarray=record_unexpected_service")
