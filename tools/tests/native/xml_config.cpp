#include "config.h"

#include <iostream>
#include <string>

int main(int argc, char **argv) {
    bool populated = argc >= 2 && std::string(argv[1]) == "--populated";
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
    config.Load(argv[sourceArg]);
    std::cout << config.display << "\n"
              << config.localprogram << "\n"
              << config.remoteprogram << "\n"
              << (config.clipboard ? "True" : "False") << "\n";

    if (argc == sourceArg + 2) {
        config.Save(argv[sourceArg + 1]);
        CConfig saved;
        saved.Load(argv[sourceArg + 1]);
        if (saved.display != config.display ||
            saved.localprogram != config.localprogram ||
            saved.remoteprogram != config.remoteprogram ||
            saved.clipboard != config.clipboard)
            return 3;
    }
    return 0;
}
