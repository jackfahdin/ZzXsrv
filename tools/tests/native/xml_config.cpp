#include "config.h"

#include <windows.h>

#include <iostream>
#include <string>
#include <vector>

// CConfig::Load/Save hand the filename to libxml2, which opens it with
// _wfopen after a CP_UTF8 conversion, so filenames must be passed as UTF-8.
// wmain keeps the command line in wide form: narrow argv is converted to the
// ANSI code page by the CRT and loses any character outside it (a Chinese
// file name on an English-locale machine becomes "??" before main runs).
static std::string utf8(const wchar_t *text) {
    int count = WideCharToMultiByte(CP_UTF8, 0, text, -1, nullptr, 0, nullptr, nullptr);
    if (count <= 1)
        return {};
    std::string result(static_cast<size_t>(count - 1), '\0');
    if (!WideCharToMultiByte(CP_UTF8, 0, text, -1, &result[0], count, nullptr, nullptr))
        return {};
    return result;
}

int wmain(int argc, wchar_t **argv) {
    std::vector<std::string> args;
    for (int i = 0; i < argc; i++)
        args.push_back(utf8(argv[i]));

    bool populated = argc >= 2 && args[1] == "--populated";
    int sourceArg = populated ? 2 : 1;
    if (argc <= sourceArg || argc > sourceArg + 2)
        return 2;

    CConfig config;
    if (populated) {
        config.display = ":88";
        config.localprogram = "keep-local";
        config.remoteprogram = "keep-remote";
        config.clipboard = false;
    }
    config.Load(args[sourceArg].c_str());
    std::cout << config.display << "\n"
              << config.localprogram << "\n"
              << config.remoteprogram << "\n"
              << (config.clipboard ? "True" : "False") << "\n";

    if (argc == sourceArg + 2) {
        config.Save(args[sourceArg + 1].c_str());
        CConfig saved;
        saved.Load(args[sourceArg + 1].c_str());
        if (saved.display != config.display ||
            saved.localprogram != config.localprogram ||
            saved.remoteprogram != config.remoteprogram ||
            saved.clipboard != config.clipboard)
            return 3;
    }
    return 0;
}
