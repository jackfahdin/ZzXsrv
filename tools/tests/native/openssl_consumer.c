/* Exercise the production xsha1.obj and the actual OpenSSL runtime DLL. */
#include <stdio.h>
#include <string.h>
#include <openssl/crypto.h>
#include "os/xsha1.h"

int main(int argc, char **argv)
{
    unsigned char digest[20];
    char buffer[4096];
    FILE *input;
    void *context;
    size_t count;
    unsigned int i;
    if (argc != 2 && argc != 3) return 2;
    if (strcmp(argv[1], "version") == 0) {
        puts(OpenSSL_version(OPENSSL_VERSION));
        return 0;
    }
    input = fopen(argv[1], "rb");
    if (!input) return 3;
    context = x_sha1_init();
    if (!context) { fclose(input); return 4; }
    if (argc == 3 && !x_sha1_update(context, buffer, 0)) {
        fclose(input);
        return 5;
    }
    while ((count = fread(buffer, 1, sizeof(buffer), input)) != 0) {
        if (!x_sha1_update(context, buffer, (int)count)) {
            fclose(input);
            return 5;
        }
    }
    if (ferror(input)) {
        x_sha1_final(context, digest);
        fclose(input);
        return 6;
    }
    fclose(input);
    if (!x_sha1_final(context, digest)) return 7;
    for (i = 0; i < sizeof(digest); ++i) printf("%02x", digest[i]);
    putchar('\n');
    return 0;
}
