/* Real XKB interest lifetime with a typed local resource table fixture. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "../../../src/xorg-server/xkb/xkbEvents.c"

#define CHECK(c) do { if (!(c)) { fprintf(stderr, "FAIL %d: %s\n", __LINE__, #c); exit(1); } } while (0)
RESTYPE RT_XKBCLIENT = 7;
int XkbEventBase, XkbReqCode;
CARD32 xkbDebugFlags;
int DeviceKeyPress, DeviceKeyRelease, DeviceMotionNotify, DeviceMappingNotify;
const Mask DeviceMappingNotifyMask = 0;
int currentMaxClients;
ClientPtr clients[MAXCLIENTS];
InputInfo inputInfo;
static DeviceIntPtr fixture_device;
static int live[3], free_calls, controls_calls;

void FreeResource(XID id, RESTYPE skip) {
    CHECK(id >= 1 && id <= 2 && skip == RT_XKBCLIENT);
    free_calls++;
    /* DIX removes the resource before calling its callback; device teardown
     * removes it here. skip prevents recursive XkbClientGone in both cases. */
    live[id] = 0;
    for (XkbInterestPtr p = fixture_device->xkb_interest; p; p = p->next)
        CHECK(p->resource != id);
}
Bool XkbEnableDisableControls(XkbSrvInfoPtr info, unsigned long change,
    unsigned long values, XkbChangesPtr changes, XkbEventCausePtr cause) {
    CHECK(info && change == 3 && values == 1 && !changes && cause);
    controls_calls++;
    return TRUE;
}

int main(int argc, char **argv)
{
    DeviceIntRec dev = {0}; KeyClassRec key = {0}; XkbSrvInfoRec info = {0};
    ClientRec first = {0}, second = {0};
    CHECK(argc == 2); fixture_device = &dev;
    dev.key = &key; key.xkbInfo = &info;
    if (!strcmp(argv[1],"no-key")) { dev.key = NULL; CHECK(!XkbRemoveResourceClient((DevicePtr)&dev, 1)); }
    else {
        XkbInterestPtr tail = XkbAddClientResource((DevicePtr)&dev, &first, 1);
        XkbInterestPtr head = XkbAddClientResource((DevicePtr)&dev, &second, 2);
        CHECK(tail && head && head->next == tail); live[1] = live[2] = 1;
        XID id = !strcmp(argv[1],"tail") ? 1 : 2;
        if (!strcmp(argv[1],"absent")) { CHECK(!XkbRemoveResourceClient((DevicePtr)&dev,3)); CHECK(free_calls == 0 && dev.xkb_interest == head); }
        else {
            if (!strcmp(argv[1],"callback")) live[id] = 0;
            if (!strcmp(argv[1],"controls")) { head->autoCtrls = 3; head->autoCtrlValues = 1; }
            CHECK(XkbRemoveResourceClient((DevicePtr)&dev,id));
            CHECK(!live[id] && free_calls == 1);
            CHECK(dev.xkb_interest == (id == 1 ? head : tail) && !dev.xkb_interest->next);
            CHECK(controls_calls == (!strcmp(argv[1],"controls") ? 1 : 0));
            CHECK(!XkbRemoveResourceClient((DevicePtr)&dev,id) && free_calls == 1);
        }
        while (dev.xkb_interest) {
            XkbInterestPtr next = dev.xkb_interest->next;
            free(dev.xkb_interest); dev.xkb_interest = next;
        }
    }
    printf("PASS %s\n",argv[1]);
    return 0;
}
__declspec(noreturn) void xkb_unexpected_service(void) { abort(); }
#pragma comment(linker, "/alternatename:GetTimeInMillis=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:PickKeyboard=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:SendEventToAllWindows=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:WriteEventsToClient=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:WriteToClient=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XIGetDevice=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XIShouldNotify=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbAdjustGroup=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbFindSrvLedInfo=xkb_unexpected_service")
