/* Exercise real XKB parsers using bounded in-process fixtures, no network. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>
#include "../../../src/xorg-server/xkb/xkb.c"

#define CHECK(c) do { if (!(c)) { fprintf(stderr, "FAIL %d: %s\n", __LINE__, #c); exit(1); } } while (0)
static XkbGeometryRec fixture_geom;
static XkbColorRec fixture_colors[2];
static XkbShapeRec fixture_shape;
static XkbOutlineRec fixture_outline;
static XkbOverlayRec fixture_overlay;
static XkbOverlayRowRec fixture_row;
static XkbKeyAliasRec fixture_alias;
static int fail_overlay, fail_row, alias_calls;
KeybdCtrl defaultKeyboardControl;
InputInfo inputInfo;

Bool ValidAtom(Atom atom) { return atom == 1; }
void *reallocarray(void *p, size_t n, size_t size) {
    CHECK(n <= USHRT_MAX && size <= 128);
    if (n == 0) return NULL;
    return realloc(p, n * size);
}
void ErrorF(const char *format, ...) { (void)format; }
XkbOverlayPtr XkbAddGeomOverlay(XkbSectionPtr section, Atom name, int rows) {
    CHECK(section && name == 1 && rows == 1);
    return fail_overlay ? NULL : &fixture_overlay;
}
XkbOverlayRowPtr XkbAddGeomOverlayRow(XkbOverlayPtr overlay, int under, int keys) {
    CHECK(overlay == &fixture_overlay && under >= 0 && keys == 0);
    return fail_row ? NULL : &fixture_row;
}
XkbShapePtr XkbAddGeomShape(XkbGeometryPtr geom, Atom name, int outlines) {
    CHECK(geom && name == 1 && outlines == 1);
    geom->num_shapes++;
    fixture_shape.outlines = &fixture_outline;
    return &fixture_shape;
}
XkbOutlinePtr XkbAddGeomOutline(XkbShapePtr shape, int points) {
    CHECK(shape == &fixture_shape && points == 0);
    return &fixture_outline;
}
XkbColorPtr XkbAddGeomColor(XkbGeometryPtr geom, char *name, unsigned pixel) {
    CHECK(geom && name && geom->num_colors < 2);
    geom->colors = fixture_colors;
    return &fixture_colors[geom->num_colors++];
}
XkbKeyAliasPtr XkbAddGeomKeyAlias(XkbGeometryPtr geom, char *alias, char *real) {
    CHECK(geom && alias && real);
    memcpy(fixture_alias.alias, alias, 4);
    memcpy(fixture_alias.real, real, 4);
    alias_calls++;
    return &fixture_alias;
}

static void map_case(const char *name)
{
    unsigned char buffer[4096] = {0};
    xkbSetMapReq *req = (void *)buffer;
    ClientRec client = {0};
    XkbDescRec xkb = {0};
    XkbClientMapRec map = {0};
    XkbServerMapRec server = {0};
    XkbKeyTypeRec types[256] = {0};
    XkbSymMapRec symmap[256] = {0};
    CARD8 widths[256] = {0};
    CARD16 syms[256] = {0};
    char *body = (char *)(req + 1);
    int value = 0, result;
    xkb.map = &map; xkb.server = &server; xkb.min_key_code = 8; xkb.max_key_code = 9;
    map.types = types; map.num_types = 5; map.key_sym_map = symmap;
    types[0].num_levels = 1;
    for (int i = 1; i < 256; i++) types[i].num_levels = 2;
    req->minKeyCode = 8; req->maxKeyCode = 9;
    client.req_len = sizeof(*req) / 4;
    if (!strncmp(name, "type-", 5)) {
        xkbKeyTypeWireDesc *wire = (void *)body;
        req->present = XkbKeyTypesMask; req->firstType = 4; req->nTypes = 1;
        wire->numLevels = 2;
        client.req_len += sizeof(*wire) / 4;
        if (!strcmp(name,"type-level-max")) wire->numLevels = XkbMaxShiftLevel;
        if (!strcmp(name,"type-level-over")) wire->numLevels = XkbMaxShiftLevel + 1;
        if (!strncmp(name,"type-count-",11)) {
            map.num_types = 255; req->firstType = 255; req->flags = XkbSetMapResizeTypes;
            req->nTypes = !strcmp(name,"type-count-max") ? 1 : 2;
            wire[1].numLevels = 2; client.req_len += sizeof(*wire) / 4;
        }
        if (strstr(name,"short")) {
            if (strstr(name,"map") || strstr(name,"preserve")) {
                wire->nMapEntries = 1;
                if (strstr(name,"preserve")) { wire->preserve = 1; client.req_len += sizeof(xkbKTSetMapEntryWireDesc) / 4; }
            } else client.req_len = sizeof(*req) / 4;
        }
        if (strstr(name,"swapped")) {
            client.swapped = TRUE; wire->virtualMods = 0x1234; swaps(&wire->virtualMods);
        }
        result = CheckKeyTypes(&client, &xkb, req, &wire, &value, widths, TRUE);
        if (strstr(name,"short") || strstr(name,"over")) CHECK(result == 0);
        else { CHECK(result == 1); CHECK(value == (strstr(name,"count") ? 256 : 5)); CHECK(widths[req->firstType] == ((xkbKeyTypeWireDesc *)body)->numLevels); }
        if (!strcmp(name,"type-valid-swapped")) CHECK(((xkbKeyTypeWireDesc *)body)->virtualMods == 0x1234);
    } else if (!strncmp(name,"sym-",4)) {
        xkbSymMapWireDesc *wire = (void *)body;
        req->present = XkbKeySymsMask; req->firstKeySym = 8; req->nKeySyms = 1;
        widths[0] = 1;
        if (strcmp(name,"sym-short")) client.req_len += sizeof(*wire) / 4;
        if (strcmp(name,"sym-empty") && strcmp(name,"sym-short")) { wire->groupInfo = 1; wire->width = 1; wire->nSyms = 1; }
        if (!strcmp(name,"sym-valid")) client.req_len += sizeof(KeySym) / 4;
        result = CheckKeySyms(&client, &xkb, req, 5, widths, syms, &wire, &value, TRUE);
        CHECK(result == (strstr(name,"short") ? 0 : 1));
    } else if (!strncmp(name,"modifier-",9)) {
        CARD8 *wire = (void *)body;
        req->present = XkbModifierMapMask; req->firstModMapKey = 8; req->nModMapKeys = 1; req->totalModMapKeys = 1;
        wire[0] = 8; wire[1] = ShiftMask;
        if (strstr(name,"valid")) client.req_len++;
        result = CheckModifierMap(&client, &xkb, req, &wire, &value);
        CHECK(result == (strstr(name,"short") ? 0 : 1));
    } else if (!strncmp(name,"action-",7)) {
        CARD8 *wire = (void *)body;
        req->present = XkbKeyActionsMask; req->firstKeyAct = 8; req->nKeyActs = 1;
        syms[8] = 1; wire[0] = strstr(name,"zero") ? 0 : 1;
        if (!strstr(name,"count-short")) client.req_len++;
        if (strstr(name,"valid")) client.req_len += sizeof(XkbAnyAction) / 4;
        result = CheckKeyActions(&client, &xkb, req, 5, widths, syms, &wire, &value);
        CHECK(result == (strstr(name,"short") ? 0 : 1));
        if (result) CHECK(value == (strstr(name,"zero") ? 0 : 1));
    } else if (!strncmp(name,"behavior-",9)) {
        xkbBehaviorWireDesc *wire = (void *)body;
        req->present = XkbKeyBehaviorsMask; req->firstKeyBehavior = 8; req->nKeyBehaviors = 1; req->totalKeyBehaviors = 1; wire->key = 8;
        if (strstr(name,"valid")) client.req_len += sizeof(*wire) / 4;
        result = CheckKeyBehaviors(&client, &xkb, req, &wire, &value);
        CHECK(result == (strstr(name,"short") ? 0 : 1));
    } else if (!strncmp(name,"vmods-",6)) {
        CARD8 *wire = (void *)body;
        req->present = XkbVirtualModsMask; req->virtualMods = 1;
        if (strstr(name,"valid")) client.req_len++;
        result = CheckVirtualMods(&client, &xkb, req, &wire, &value);
        CHECK(result == (strstr(name,"short") ? 0 : 1));
    } else if (!strncmp(name,"explicit-",9)) {
        CARD8 *wire = (void *)body;
        req->present = XkbExplicitComponentsMask; req->firstKeyExplicit = 8; req->nKeyExplicit = 1; req->totalKeyExplicit = 1; wire[0] = 8;
        if (strstr(name,"valid")) client.req_len++;
        result = CheckKeyExplicit(&client, &xkb, req, &wire, &value);
        CHECK(result == (strstr(name,"short") ? 0 : 1));
    } else if (!strncmp(name,"vmodmap-",8)) {
        xkbVModMapWireDesc *wire = (void *)body;
        req->present = XkbVirtualModMapMask; req->firstVModMapKey = 8; req->nVModMapKeys = 1; req->totalVModMapKeys = 1; wire->key = 8;
        if (strstr(name,"valid")) client.req_len += sizeof(*wire) / 4;
        result = CheckVirtualModMap(&client, &xkb, req, &wire, &value);
        CHECK(result == (strstr(name,"short") ? 0 : 1));
    } else CHECK(0);
}

static void compat_case(const char *name)
{
    unsigned char buffer[128] = {0};
    xkbSetCompatMapReq *req = (void *)buffer;
    xkbSymInterpretWireDesc *wire = (void *)(req + 1);
    ClientRec client = {0}; DeviceIntRec dev = {0}; KeyClassRec key = {0};
    XkbSrvInfoRec info = {0}; XkbDescRec desc = {0}; XkbCompatMapRec compat = {0};
    dev.key = &key; key.xkbInfo = &info; info.desc = &desc; desc.compat = &compat;
    compat.num_si = 1; compat.size_si = 4; compat.sym_interpret = calloc(4, sizeof(XkbSymInterpretRec));
    CHECK(compat.sym_interpret);
    req->firstSI = 1; req->nSI = 2; wire[0].sym = 65; wire[1].sym = 66;
    if (strstr(name,"overflow")) { compat.num_si = compat.size_si = USHRT_MAX; req->firstSI = USHRT_MAX; req->nSI = 1; }
    if (strstr(name,"truncate")) { compat.num_si = 4; req->truncateSI = TRUE; }
    if (strstr(name,"grow")) compat.size_si = 1;
    if (strstr(name,"skipped")) { wire[0].sym = NoSymbol; wire[0].match = XkbSI_AnyOfOrNone; wire[0].mods = 0xff; wire[0].act.type = XkbSA_XFree86Private; }
    if (strstr(name,"tail")) { compat.num_si = 4; compat.sym_interpret[3].sym = 99; }
    req->length = (sizeof(*req) + req->nSI * sizeof(*wire)) / 4;
    int result = _XkbSetCompatMap(&client, &dev, req, (char *)(req + 1), FALSE);
    if (strstr(name,"overflow")) CHECK(result == BadValue && compat.num_si == USHRT_MAX);
    else {
        CHECK(result == Success);
        CHECK(compat.num_si == (strstr(name,"skipped") && !strstr(name,"tail") ? 2 : 3));
        CHECK(compat.sym_interpret[1].sym == (strstr(name,"skipped") ? 66 : 65));
        if (strstr(name,"tail")) CHECK(compat.sym_interpret[2].sym == 99 && compat.size_si == 4);
    }
    free(compat.sym_interpret);
}

static void geometry_case(const char *name)
{
    unsigned char buffer[512] = {0};
    xkbSetGeometryReq *req = (void *)buffer;
    ClientRec client = {0};
    char *wire = (char *)(req + 1);
    int result;
    client.requestBuffer = req;
    client.req_len = sizeof(*req) / 4;
    if (!strncmp(name,"overlay-",8)) {
        XkbSectionRec section = {0};
        xkbOverlayWireDesc *overlay = (void *)wire;
        xkbOverlayRowWireDesc *row = (void *)(overlay + 1);
        section.num_rows = 1; overlay->name = 1; overlay->nRows = 1;
        row->rowUnder = strstr(name,"index") ? 1 : 0;
        fail_overlay = !strcmp(name,"overlay-alloc"); fail_row = !strcmp(name,"overlay-row-alloc");
        client.req_len += (sizeof(*overlay) + sizeof(*row)) / 4;
        result = _CheckSetOverlay(&wire, req, &fixture_geom, &section, &client);
        CHECK(result == (strstr(name,"alloc") ? BadAlloc : strstr(name,"index") ? BadMatch : Success));
    } else if (!strncmp(name,"shape-",6)) {
        xkbShapeWireDesc *shape = (void *)wire;
        req->nShapes = 1; shape->name = 1; shape->nOutlines = 1;
        if (strstr(name,"primary")) shape->primaryNdx = 1;
        if (strstr(name,"approx")) shape->approxNdx = 1;
        if (strstr(name,"sentinel")) shape->primaryNdx = shape->approxNdx = XkbNoShape;
        client.req_len += (sizeof(*shape) + sizeof(xkbOutlineWireDesc)) / 4;
        result = _CheckSetShapes(&fixture_geom, req, &wire, &client);
        CHECK(result == ((strstr(name,"primary") || strstr(name,"approx")) ? BadValue : Success));
        if (strstr(name,"valid")) CHECK(fixture_shape.primary == &fixture_outline && fixture_shape.approx == &fixture_outline);
        if (strstr(name,"sentinel")) CHECK(!fixture_shape.primary && !fixture_shape.approx);
    } else {
        req->nColors = 2; req->baseColorNdx = 0; req->labelColorNdx = 1;
        if (strstr(name,"color-base")) req->baseColorNdx = 2;
        if (strstr(name,"color-label")) req->labelColorNdx = 2;
        /* Empty counted label font and two empty counted color names, padded. */
        wire += 12;
        xkbShapeWireDesc *shape = (void *)wire;
        req->nShapes = 1; shape->name = 1; shape->nOutlines = 1;
        wire += sizeof(*shape) + sizeof(xkbOutlineWireDesc);
        req->nKeyAliases = 1; memcpy(wire, "REALALIA", 8);
        client.req_len = (wire - (char *)req + (strstr(name,"alias-short") ? 4 : 8)) / 4;
        result = _CheckSetGeom(&fixture_geom, req, &client);
        CHECK(result == (strstr(name,"color-") ? BadMatch : strstr(name,"short") ? BadLength : Success));
        CHECK(alias_calls == (!strcmp(name,"alias-valid") ? 1 : 0));
        if (alias_calls) CHECK(!memcmp(fixture_alias.alias,"ALIA",4) && !memcmp(fixture_alias.real,"REAL",4));
        free(fixture_geom.label_font);
    }
}

int main(int argc, char **argv)
{
    CHECK(argc == 2);
    if (!strncmp(argv[1],"compat-",7)) compat_case(argv[1]);
    else if (!strncmp(argv[1],"overlay-",8) || !strncmp(argv[1],"shape-",6) || !strncmp(argv[1],"color-",6) || !strncmp(argv[1],"alias-",6)) geometry_case(argv[1]);
    else map_case(argv[1]);
    printf("PASS %s\n",argv[1]);
    return 0;
}

__declspec(noreturn) void xkb_unexpected_service(void) { abort(); }
#pragma comment(linker, "/alternatename:AccessXCancelRepeatKey=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:AccessXComputeCurveFactor=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:AddExtension=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:AddResource=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:CreateNewResourceType=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:FakeClientID=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:GetMaster=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:IsMaster=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:NameForAtom=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:SProcXkbDispatch=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:SrvXkbAddGeomDoodad=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:SrvXkbAddGeomKey=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:SrvXkbAddGeomOverlayKey=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:SrvXkbAddGeomProperty=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:SrvXkbAddGeomRow=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:SrvXkbAddGeomSection=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:SrvXkbAllocClientMap=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:SrvXkbAllocGeometry=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:SrvXkbAllocNames=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:SrvXkbChangeKeycodeRange=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:SrvXkbFreeGeometry=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:SrvXkbFreeKeyboard=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:SrvXkbLatchGroup=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:SrvXkbLatchModifiers=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:SrvXkbResizeKeyActions=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:SrvXkbResizeKeySyms=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:SrvXkbResizeKeyType=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:StandardMinorOpcode=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:WriteToClient=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XaceHookDeviceAccess=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XaceHookServerAccess=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbAddClientResource=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbAllocSrvLedInfo=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbApplyLedMapChanges=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbApplyLedNameChanges=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbApplyLedStateChanges=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbCheckSecondaryEffects=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbClearAllLatchesAndLocks=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbComputeControlsNotify=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbComputeDerivedState=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbCopyControls=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbDDXChangeControls=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbDDXLoadKeymapByNames=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbDeviceApplyKeymap=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbFindClientResource=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbFindSrvLedInfo=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbFlushLedEvents=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbFreeComponentNames=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbFreeSrvLedInfo=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbHandleBell=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbIndicatorsToUpdate=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbInitPrivates=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbLookupNamedGeometry=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbMaskForVMask=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbRemoveResourceClient=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbSendCompatMapNotify=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbSendControlsNotify=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbSendExtensionDeviceNotify=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbSendNamesNotify=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbSendNewKeyboardNotify=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbSendNotification=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbSendStateNotify=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbSetActionKeyMods=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbStateChangedFlags=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbUpdateActions=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbUpdateAllDeviceIndicators=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbUpdateDescActions=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:XkbUpdateIndicators=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:Xstrdup=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:_XkbLookupAnyDevice=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:_XkbLookupBellDevice=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:_XkbLookupKeyboard=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:_XkbLookupLedDevice=xkb_unexpected_service")
#pragma comment(linker, "/alternatename:dixLookupWindow=xkb_unexpected_service")
