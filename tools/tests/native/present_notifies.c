/* Real PRESENT notify list operations, bounded local windows only. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "../../../src/xorg-server/present/present_notify.c"
#define CHECK(c) do { if (!(c)) { fprintf(stderr,"FAIL %d: %s\n",__LINE__,#c); exit(1); } } while (0)
DevPrivateKeyRec present_window_private_key;
static WindowRec windows[3];
static present_window_priv_rec privates[3];
static int lookup_fail=-1, alloc_fail=-1;
int dixLookupWindow(WindowPtr *out, XID id, ClientPtr client, Mask access) {
    CHECK(client && access==DixGetAttrAccess && id>=1 && id<=3);
    if ((int)id-1==lookup_fail) return BadWindow;
    *out=&windows[id-1]; return Success;
}
present_window_priv_ptr present_get_window_priv(WindowPtr window, Bool create) {
    int index=(int)(window-windows); CHECK(index>=0 && index<3 && create);
    return index==alloc_fail ? NULL : &privates[index];
}
int main(int argc,char **argv) {
    ClientRec client={0}; xPresentNotify wire[3]={{0}}; present_notify_ptr out=NULL;
    CHECK(argc==2); present_window_private_key.initialized=TRUE;
    for(int i=0;i<3;i++) { xorg_list_init(&privates[i].notifies); windows[i].devPrivates=calloc(1,sizeof(void*)); CHECK(windows[i].devPrivates); dixSetPrivate(&windows[i].devPrivates,&present_window_private_key,&privates[i]); wire[i].window=i+1; wire[i].serial=10+i; }
    if(strstr(argv[1],"lookup")) lookup_fail=strstr(argv[1],"first")?0:strstr(argv[1],"second")?1:2;
    if(strstr(argv[1],"alloc")) alloc_fail=strstr(argv[1],"first")?0:strstr(argv[1],"second")?1:2;
    int count=strstr(argv[1],"one")?1:3;
    int result=present_create_notifies(&client,count,wire,&out);
    if(lookup_fail>=0 || alloc_fail>=0) { CHECK(result==(lookup_fail>=0?BadWindow:BadAlloc)); CHECK(out==NULL); }
    else {
        CHECK(result==Success && out!=NULL);
        for(int i=0;i<count;i++) CHECK(out[i].window==&windows[i] && out[i].serial==10+i && !xorg_list_is_empty(&privates[i].notifies));
        if(strstr(argv[1],"clear")) { present_clear_window_notifies(&windows[0]); CHECK(out[0].window==NULL && out[1].window==&windows[1]); }
        present_destroy_notifies(out,count);
    }
    for(int i=0;i<3;i++) { CHECK(xorg_list_is_empty(&privates[i].notifies)); free(windows[i].devPrivates); }
    printf("PASS %s\n",argv[1]); return 0;
}
