/* Normal XML streaming and feature checks against the production static library. */
#include <expat.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct Result { int elements; char text[4096]; size_t used; };

static void XMLCALL start(void *data, const XML_Char *name, const XML_Char **attrs) {
    struct Result *result = data;
    (void)attrs;
    ++result->elements;
    printf("ELEMENT %s\n", name);
}

static void XMLCALL chars(void *data, const XML_Char *value, int count) {
    struct Result *result = data;
    if (count < 0 || result->used + (size_t)count >= sizeof(result->text))
        exit(3);
    memcpy(result->text + result->used, value, (size_t)count);
    result->used += (size_t)count;
    result->text[result->used] = 0;
}

int main(int argc, char **argv) {
    if (argc == 2 && strcmp(argv[1], "version") == 0) {
        XML_Expat_Version version = XML_ExpatVersionInfo();
        const XML_Feature *feature = XML_GetFeatureList();
        printf("VERSION %d.%d.%d\nCHAR %zu\n", version.major, version.minor,
               version.micro, sizeof(XML_Char));
        for (; feature->feature != XML_FEATURE_END; ++feature)
            printf("FEATURE %d %ld\n", feature->feature, feature->value);
        return 0;
    }
    if (argc != 3) return 2;
    FILE *file = NULL;
    if (fopen_s(&file, argv[2], "rb") != 0) return 2;
    XML_Parser parser = strcmp(argv[1], "namespace") == 0
        ? XML_ParserCreateNS(NULL, '|') : XML_ParserCreate(NULL);
    if (!parser) { fclose(file); return 2; }
    int rounds = strcmp(argv[1], "reset") == 0 ? 2 : 1;
    for (int round = 0; round < rounds; ++round) {
        struct Result result = {0};
        if (round && !XML_ParserReset(parser, NULL)) return 3;
        rewind(file);
        XML_SetUserData(parser, &result);
        XML_SetElementHandler(parser, start, NULL);
        XML_SetCharacterDataHandler(parser, chars);
        for (;;) {
            void *buffer = XML_GetBuffer(parser, 13);
            if (!buffer) return 3;
            size_t count = fread(buffer, 1, 13, file);
            if (ferror(file)) return 3;
            if (XML_ParseBuffer(parser, (int)count, count == 0) != XML_STATUS_OK) {
                fprintf(stderr, "Parse failed: %s\n", XML_ErrorString(XML_GetErrorCode(parser)));
                XML_ParserFree(parser);
                fclose(file);
                return 3;
            }
            if (!count) break;
        }
        printf("RESULT %d %s\n", result.elements, result.text);
    }
    XML_ParserFree(parser);
    fclose(file);
    return 0;
}
