/* Exercise the production Mesa configuration object without linking Expat. */
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include "util/xmlconfig.h"

int main(int argc, char **argv) {
    if (argc != 2) return 2;
    const driOptionDescription options[] = {
        { .desc = "test", .info = { .type = DRI_SECTION } },
        { .desc = "count", .info = { .name = "zzxsrv_r6_count", .type = DRI_INT,
            .range = { .start._int = 0, .end._int = 100 } }, .value._int = 7 }
    };
    driOptionCache info = {0}, cache = {0};
    driInjectExecName("zzxsrv-r6-test");
    driParseOptionInfo(&info, options, 2);
    driParseConfigFiles(&cache, &info, 0, "zzxsrv_r6_test", NULL, NULL,
                        "zzxsrv-r6-test", 1, "zzxsrv-r6-test", 1);
    int value = driQueryOptioni(&cache, "zzxsrv_r6_count");
    printf("VALUE %d\n", value);
    driDestroyOptionCache(&cache);
    driDestroyOptionInfo(&info);
    return value == atoi(argv[1]) ? 0 : 3;
}
