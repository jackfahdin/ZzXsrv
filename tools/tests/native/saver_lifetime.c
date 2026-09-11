/* Real screen-private release and saver-window creation with local fixtures. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "../../../src/xorg-server/Xext/saver.c"
#define CHECK(c) do { if (!(c)) { fprintf(stderr,"FAIL %d: %s\n",__LINE__,#c); exit(1); } } while (0)
ScreenInfo screenInfo;
ClientPtr serverClient;
int GrabInProgress;
int ScreenSaverBlanking, screenIsSaved, PanoramiXNumScreens;
CARD32 ScreenSaverTime;
CARD16 DPMSPowerLevel;
Bool screenSaverSuspended, noPanoramiXExtension;
TimeStamp currentTime;
EventSwapPtr EventSwapVector[128];
InputInfo inputInfo;
RESTYPE XRC_DRAWABLE, XRT_PIXMAP, XRT_COLORMAP;
static WindowRec fixture_window;
static WindowOptRec fixture_optional;
static int free_calls, create_calls, map_calls;
static Bool fail_create;
int dixDestroyPixmap(void *pixmap, XID id) { CHECK(!pixmap && !id); return Success; }
void FreeResource(XID id,RESTYPE skip) { CHECK(id==99 && skip==X11_RESTYPE_NONE); free_calls++; }
WindowPtr CreateWindow(Window wid,WindowPtr parent,int x,int y,unsigned int w,unsigned int h,unsigned int bw,unsigned int cl,Mask mask,XID *values,int depth,ClientPtr client,VisualID visual,int *error) {
    CHECK(wid==99 && client==serverClient); create_calls++;
    if(fail_create) { *error=BadAlloc; return NULL; }
    fixture_window.drawable.id=wid; fixture_window.optional=&fixture_optional; fixture_optional.colormap=None;
    return &fixture_window;
}
Bool AddResource(XID id,RESTYPE type,void *value) { CHECK(id==99 && type==X11_RESTYPE_WINDOW && value==&fixture_window); return TRUE; }
int MapWindow(WindowPtr window,ClientPtr client) { CHECK(window==&fixture_window && client==serverClient); map_calls++; return Success; }
int main(int argc,char **argv) {
    CHECK(argc==2); ScreenRec screen={0}; ClientRec client={0}; WindowRec old={0}; ScreenSaverEventRec event={0};
    ScreenPrivateKey->initialized=TRUE; screen.devPrivates=calloc(1,sizeof(void*)); CHECK(screen.devPrivates); screen.screensaver.wid=99; serverClient=&client;
    ScreenSaverScreenPrivatePtr priv=NULL;
    if(strcmp(argv[1],"no-private")) { priv=calloc(1,sizeof(*priv)); CHECK(priv); SetScreenPrivate(&screen,priv); }
    if(strstr(argv[1],"old-window")) { screen.screensaver.pWindow=&old; priv->hasWindow=TRUE; }
    if(strstr(argv[1],"events")) priv->events=&event;
    if(strstr(argv[1],"create") || strstr(argv[1],"free-attr")) { priv->attr=calloc(1,sizeof(*priv->attr)); CHECK(priv->attr); priv->attr->screen=&screen; priv->attr->client=&client; }
    if(strstr(argv[1],"free-attr")) { CHECK(ScreenSaverFreeAttr(priv->attr,0)==TRUE); CHECK(GetScreenPrivate(&screen)==NULL); }
    else {
        fail_create=strstr(argv[1],"failure")!=NULL;
        Bool result=CreateSaverWindow(&screen);
        CHECK(result==(!strcmp(argv[1],"create-success")));
        CHECK(free_calls==(strstr(argv[1],"old-window")?1:0));
        CHECK(create_calls==(strstr(argv[1],"create")?1:0));
        CHECK(map_calls==(!strcmp(argv[1],"create-success")?1:0));
        if(!strcmp(argv[1],"old-window-release") || !strcmp(argv[1],"no-private")) CHECK(GetScreenPrivate(&screen)==NULL);
        if(result) CHECK(screen.screensaver.pWindow==&fixture_window && GetScreenPrivate(&screen)->hasWindow);
    }
    priv=GetScreenPrivate(&screen); if(priv) { free(priv->attr); free(priv); }
    free(screen.devPrivates); printf("PASS %s\n",argv[1]); return 0;
}
__declspec(noreturn) void sync_unexpected_service(void) { abort(); }
#pragma comment(linker, "/alternatename:AddExtension=sync_unexpected_service")
#pragma comment(linker, "/alternatename:ChangeWindowAttributes=sync_unexpected_service")
#pragma comment(linker, "/alternatename:CheckWindowOptionalNeed=sync_unexpected_service")
#pragma comment(linker, "/alternatename:CreateNewResourceType=sync_unexpected_service")
#pragma comment(linker, "/alternatename:FakeClientID=sync_unexpected_service")
#pragma comment(linker, "/alternatename:FindWindowWithOptional=sync_unexpected_service")
#pragma comment(linker, "/alternatename:FreeCursor=sync_unexpected_service")
#pragma comment(linker, "/alternatename:FreeScreenSaverTimer=sync_unexpected_service")
#pragma comment(linker, "/alternatename:GetTimeInMillis=sync_unexpected_service")
#pragma comment(linker, "/alternatename:IsMapInstalled=sync_unexpected_service")
#pragma comment(linker, "/alternatename:LastEventTime=sync_unexpected_service")
#pragma comment(linker, "/alternatename:MakeWindowOptional=sync_unexpected_service")
#pragma comment(linker, "/alternatename:NoticeTime=sync_unexpected_service")
#pragma comment(linker, "/alternatename:PanoramiXTranslateVisualID=sync_unexpected_service")
#pragma comment(linker, "/alternatename:RefCursor=sync_unexpected_service")
#pragma comment(linker, "/alternatename:SetScreenSaverTimer=sync_unexpected_service")
#pragma comment(linker, "/alternatename:StandardMinorOpcode=sync_unexpected_service")
#pragma comment(linker, "/alternatename:SwapLongs=sync_unexpected_service")
#pragma comment(linker, "/alternatename:UpdateCurrentTime=sync_unexpected_service")
#pragma comment(linker, "/alternatename:UpdateCurrentTimeIf=sync_unexpected_service")
#pragma comment(linker, "/alternatename:WriteEventsToClient=sync_unexpected_service")
#pragma comment(linker, "/alternatename:WriteToClient=sync_unexpected_service")
#pragma comment(linker, "/alternatename:XaceHookScreensaverAccess=sync_unexpected_service")

#pragma comment(linker, "/alternatename:dixLookupDrawable=sync_unexpected_service")
#pragma comment(linker, "/alternatename:dixLookupResourceByClass=sync_unexpected_service")
#pragma comment(linker, "/alternatename:dixLookupResourceByType=sync_unexpected_service")
#pragma comment(linker, "/alternatename:dixRegisterPrivateKey=sync_unexpected_service")
#pragma comment(linker, "/alternatename:dixSaveScreens=sync_unexpected_service")
#pragma comment(linker, "/alternatename:xreallocarray=sync_unexpected_service")
