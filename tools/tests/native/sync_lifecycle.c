/* Real counter/fence traversal and FreeAwait, no server or network. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "../../../src/xorg-server/Xext/sync.c"
#include "../../../src/xorg-server/miext/sync/misync.c"
#define CHECK(c) do { if (!(c)) { fprintf(stderr,"FAIL %d: %s\n",__LINE__,#c); exit(1); } } while (0)
static SyncAwaitUnion *group;
static int fired, destroyed, screen_destroyed, object_freed;
static Bool keep_alarm, should_fire=TRUE;
static int64_t expected_old;
ScreenInfo screenInfo;
ClientPtr serverClient;
volatile char isItTimeToYield;
volatile char dispatchException;
TimeStamp currentTime;
EventSwapPtr EventSwapVector[128];
static Bool check_trigger(SyncTrigger *trigger,int64_t old) { CHECK(trigger && old==expected_old); return should_fire; }
static void fired_trigger(SyncTrigger *trigger) {
    CHECK(++fired<=3);
    if(group && trigger==&(group+1)->await.trigger) { SyncAwaitUnion *saved=group; group=NULL; CHECK(FreeAwait(saved,0)==Success); }
    else if(!keep_alarm) SyncDeleteTriggerFromSyncObject(trigger);
}
static void destroyed_trigger(SyncTrigger *trigger) {
    CHECK(trigger && trigger->pSync->beingDestroyed); CHECK(++destroyed<=3);
    if(group && trigger==&(group+1)->await.trigger) { SyncAwaitUnion *saved=group; group=NULL; CHECK(FreeAwait(saved,0)==Success); }
}
static void screen_destroy(ScreenPtr screen,SyncFence *fence) { CHECK(screen && fence->sync.beingDestroyed && !fence->sync.pTriglist); screen_destroyed++; }
void _dixFreeObjectWithPrivates(void *object,PrivatePtr privates,DevPrivateType type) { CHECK(type==PRIVATE_SYNC_FENCE && !privates); object_freed++; free(object); }
static void add_trigger(SyncObject *obj,SyncTrigger *trigger) {
    trigger->pSync=obj; trigger->CheckTrigger=check_trigger; trigger->TriggerFired=fired_trigger; trigger->CounterDestroyed=destroyed_trigger;
    SyncTriggerList **tail=&obj->pTriglist;
    while(*tail) tail=&(*tail)->next;
    *tail=calloc(1,sizeof(**tail)); CHECK(*tail); (*tail)->pTrigger=trigger;
}
int main(int argc,char **argv) {
    CHECK(argc==2);
    Bool is_fence=strstr(argv[1],"fence")!=NULL;
    SyncCounter *counter=NULL; SyncFence *fence=NULL; SyncObject *obj;
    ScreenRec screen={0}; SyncScreenPrivRec private={0}; ClientRec client={0};
    SyncTrigger single={0};
    if(is_fence) {
        fence=calloc(1,sizeof(*fence)); CHECK(fence); obj=&fence->sync; obj->type=SYNC_FENCE;
        fence->pScreen=&screen; fence->funcs.SetTriggered=miSyncFenceSetTriggered; fence->funcs.DeleteTrigger=miSyncFenceDeleteTrigger;
        miSyncScreenPrivateKey.initialized=TRUE; miSyncScreenPrivateKey.size=sizeof(private); screen.devPrivates=(void*)&private; private.funcs.DestroyFence=screen_destroy;
    } else { counter=calloc(1,sizeof(*counter)); CHECK(counter); obj=&counter->sync; obj->type=SYNC_COUNTER; counter->value=41; expected_old=41; }
    obj->initialized=TRUE; obj->client=&client;
    if(strstr(argv[1],"shared") || strstr(argv[1],"await-")) {
        group=calloc(3,sizeof(*group)); CHECK(group); group->header.num_waitconditions=2;
        add_trigger(obj,&(group+1)->await.trigger); add_trigger(obj,&(group+2)->await.trigger);
    }
    if(strstr(argv[1],"await-")) {
        if(strstr(argv[1],"destroying")) obj->beingDestroyed=TRUE;
        if(strstr(argv[1],"null")) { SyncDeleteTriggerFromSyncObject(&(group+2)->await.trigger); (group+2)->await.trigger.pSync=NULL; }
        CHECK(FreeAwait(group,0)==Success); group=NULL;
        if(obj->beingDestroyed) { CHECK(obj->pTriglist && !obj->pTriglist->pTrigger && obj->pTriglist->next && !obj->pTriglist->next->pTrigger); }
        else CHECK(!obj->pTriglist);
    } else {
        if(!strstr(argv[1],"empty")) add_trigger(obj,&single);
        if(strstr(argv[1],"destroy-")) {
            if(is_fence) { miSyncDestroyFence(fence); CHECK(screen_destroyed==1 && object_freed==1); }
            else CHECK(FreeCounter(counter,0)==Success);
            CHECK(destroyed==(strstr(argv[1],"shared")?2:1));
            obj=NULL;
        } else {
            keep_alarm=strstr(argv[1],"alarm")!=NULL; should_fire=strstr(argv[1],"no-fire")==NULL;
            if(is_fence) { miSyncTriggerFence(fence); CHECK(fence->triggered); }
            else { SyncChangeCounter(counter,42); CHECK(counter->value==42); }
            CHECK(fired==(strstr(argv[1],"empty") || !should_fire ? 0 : strstr(argv[1],"shared")?2:1));
            if(keep_alarm || !should_fire) CHECK(obj->pTriglist && !obj->pTriglist->next && obj->pTriglist->pTrigger==&single);
            else CHECK(!obj->pTriglist);
        }
    }
    if(obj) { while(obj->pTriglist) { SyncTriggerList *next=obj->pTriglist->next; free(obj->pTriglist); obj->pTriglist=next; } free(obj); }
    CHECK(!group); printf("PASS %s\n",argv[1]); return 0;
}
__declspec(noreturn) void sync_unexpected_service(void) { abort(); }
#pragma comment(linker, "/alternatename:AddExtension=sync_unexpected_service")
#pragma comment(linker, "/alternatename:AddResource=sync_unexpected_service")
#pragma comment(linker, "/alternatename:AdjustWaitForDelay=sync_unexpected_service")
#pragma comment(linker, "/alternatename:AttendClient=sync_unexpected_service")
#pragma comment(linker, "/alternatename:CreateNewResourceType=sync_unexpected_service")
#pragma comment(linker, "/alternatename:ErrorF=sync_unexpected_service")
#pragma comment(linker, "/alternatename:FakeClientID=sync_unexpected_service")
#pragma comment(linker, "/alternatename:FatalError=sync_unexpected_service")
#pragma comment(linker, "/alternatename:GetTimeInMillis=sync_unexpected_service")
#pragma comment(linker, "/alternatename:IgnoreClient=sync_unexpected_service")
#pragma comment(linker, "/alternatename:LastEventTime=sync_unexpected_service")
#pragma comment(linker, "/alternatename:LastEventTimeToggleResetAll=sync_unexpected_service")
#pragma comment(linker, "/alternatename:LastEventTimeToggleResetFlag=sync_unexpected_service")
#pragma comment(linker, "/alternatename:LastEventTimeWasReset=sync_unexpected_service")
#pragma comment(linker, "/alternatename:LegalNewID=sync_unexpected_service")
#pragma comment(linker, "/alternatename:RegisterBlockAndWakeupHandlers=sync_unexpected_service")
#pragma comment(linker, "/alternatename:RemoveBlockAndWakeupHandlers=sync_unexpected_service")
#pragma comment(linker, "/alternatename:SetResourceTypeErrorValue=sync_unexpected_service")
#pragma comment(linker, "/alternatename:StandardMinorOpcode=sync_unexpected_service")
#pragma comment(linker, "/alternatename:SwapLongs=sync_unexpected_service")
#pragma comment(linker, "/alternatename:UpdateCurrentTime=sync_unexpected_service")
#pragma comment(linker, "/alternatename:WriteEventsToClient=sync_unexpected_service")
#pragma comment(linker, "/alternatename:WriteToClient=sync_unexpected_service")
#pragma comment(linker, "/alternatename:XNFalloc=sync_unexpected_service")
#pragma comment(linker, "/alternatename:_dixAllocateObjectWithPrivates=sync_unexpected_service")
#pragma comment(linker, "/alternatename:dixLookupClient=sync_unexpected_service")
#pragma comment(linker, "/alternatename:dixLookupDrawable=sync_unexpected_service")
#pragma comment(linker, "/alternatename:dixLookupResourceByType=sync_unexpected_service")
#pragma comment(linker, "/alternatename:dixRegisterPrivateKey=sync_unexpected_service")
#pragma comment(linker, "/alternatename:xorg_backtrace=sync_unexpected_service")
#pragma comment(linker, "/alternatename:xreallocarray=sync_unexpected_service")
