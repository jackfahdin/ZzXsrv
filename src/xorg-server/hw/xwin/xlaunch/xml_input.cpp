#include "xml_input.h"

#include <windows.h>
#include <winhttp.h>

#include <libxml/encoding.h>
#include <libxml/parser.h>
#include <libxml/parserInternals.h>
#include <libxml/xmlerror.h>

#include <algorithm>
#include <cctype>
#include <memory>
#include <string>
#include <vector>

namespace {
struct InternetCloser {
    void operator()(void *handle) const {
        if (handle)
            WinHttpCloseHandle(static_cast<HINTERNET>(handle));
    }
};
using InternetHandle = std::unique_ptr<void, InternetCloser>;

bool isHttp(const char *url) {
    return url && (_strnicmp(url, "http://", 7) == 0 ||
                   _strnicmp(url, "https://", 8) == 0);
}

std::wstring widenUtf8(const char *text) {
    int count = MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, text, -1, nullptr, 0);
    if (count <= 0)
        return {};
    std::wstring result(static_cast<size_t>(count), L'\0');
    if (!MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, text, -1, &result[0], count))
        return {};
    result.resize(static_cast<size_t>(count - 1));
    return result;
}

std::string responseCharset(HINTERNET request) {
    DWORD size = 0;
    WinHttpQueryHeaders(request, WINHTTP_QUERY_CONTENT_TYPE, WINHTTP_HEADER_NAME_BY_INDEX,
                        nullptr, &size, WINHTTP_NO_HEADER_INDEX);
    if (GetLastError() != ERROR_INSUFFICIENT_BUFFER)
        return {};
    std::wstring value(size / sizeof(wchar_t), L'\0');
    if (!WinHttpQueryHeaders(request, WINHTTP_QUERY_CONTENT_TYPE, WINHTTP_HEADER_NAME_BY_INDEX,
                             &value[0], &size, WINHTTP_NO_HEADER_INDEX))
        return {};
    value.resize(size / sizeof(wchar_t));
    while (!value.empty() && value.back() == L'\0')
        value.pop_back();
    std::string original;
    original.reserve(value.size());
    for (wchar_t ch : value)
        original.push_back(static_cast<char>(ch));
    size_t parameter = original.find(';');
    while (parameter != std::string::npos) {
        size_t next = original.find(';', parameter + 1);
        size_t equals = original.find('=', parameter + 1);
        if (equals != std::string::npos && (next == std::string::npos || equals < next)) {
            size_t nameBegin = original.find_first_not_of(" \t", parameter + 1);
            size_t nameEnd = original.find_last_not_of(" \t", equals - 1);
            std::string name = nameBegin == std::string::npos || nameEnd < nameBegin ?
                std::string() : original.substr(nameBegin, nameEnd - nameBegin + 1);
            std::transform(name.begin(), name.end(), name.begin(),
                           [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
            if (name == "charset") {
                size_t begin = original.find_first_not_of(" \t", equals + 1);
                size_t end = next == std::string::npos ? original.size() : next;
                if (begin == std::string::npos || begin >= end)
                    return {};
                while (end > begin && std::isspace(static_cast<unsigned char>(original[end - 1])))
                    --end;
                if (begin < end && (original[begin] == '"' || original[begin] == '\'') &&
                    original[end - 1] == original[begin]) {
                    ++begin;
                    --end;
                }
                return original.substr(begin, end - begin);
            }
        }
        parameter = next;
    }
    return {};
}

xmlParserErrors loadHttp(const char *url, xmlParserInputFlags flags, xmlParserInput **out) {
    *out = nullptr;
    std::wstring wideUrl = widenUtf8(url);
    if (wideUrl.empty())
        return XML_IO_EINVAL;

    URL_COMPONENTS parts{};
    parts.dwStructSize = sizeof(parts);
    parts.dwSchemeLength = static_cast<DWORD>(-1);
    parts.dwHostNameLength = static_cast<DWORD>(-1);
    parts.dwUrlPathLength = static_cast<DWORD>(-1);
    parts.dwExtraInfoLength = static_cast<DWORD>(-1);
    if (!WinHttpCrackUrl(wideUrl.c_str(), 0, 0, &parts))
        return XML_IO_EINVAL;

    InternetHandle session(WinHttpOpen(L"VcXsrv XLaunch/1.0",
                                       WINHTTP_ACCESS_TYPE_AUTOMATIC_PROXY,
                                       WINHTTP_NO_PROXY_NAME,
                                       WINHTTP_NO_PROXY_BYPASS, 0));
    if (!session)
        return XML_IO_LOAD_ERROR;
    InternetHandle connection(WinHttpConnect(session.get(),
        std::wstring(parts.lpszHostName, parts.dwHostNameLength).c_str(), parts.nPort, 0));
    if (!connection)
        return XML_IO_LOAD_ERROR;
    std::wstring target(parts.lpszUrlPath, parts.dwUrlPathLength);
    target.append(parts.lpszExtraInfo, parts.dwExtraInfoLength);
    if (target.empty())
        target = L"/";
    DWORD requestFlags = parts.nScheme == INTERNET_SCHEME_HTTPS ? WINHTTP_FLAG_SECURE : 0;
    InternetHandle request(WinHttpOpenRequest(connection.get(), L"GET", target.c_str(),
        nullptr, WINHTTP_NO_REFERER, WINHTTP_DEFAULT_ACCEPT_TYPES, requestFlags));
    if (!request)
        return XML_IO_LOAD_ERROR;
    DWORD autoLogon = WINHTTP_AUTOLOGON_SECURITY_LEVEL_HIGH;
    if (!WinHttpSetOption(request.get(), WINHTTP_OPTION_AUTOLOGON_POLICY,
                          &autoLogon, sizeof(autoLogon)))
        return XML_IO_LOAD_ERROR;
    DWORD decompression = WINHTTP_DECOMPRESSION_FLAG_GZIP | WINHTTP_DECOMPRESSION_FLAG_DEFLATE;
    WinHttpSetOption(request.get(), WINHTTP_OPTION_DECOMPRESSION,
                     &decompression, sizeof(decompression));
    // WinHTTP's default redirect handling is retained. XLaunch neither supplies nor
    // automatically sends credentials; system automatic proxy discovery is used.
    if (!WinHttpSendRequest(request.get(), WINHTTP_NO_ADDITIONAL_HEADERS, 0,
                            WINHTTP_NO_REQUEST_DATA, 0, 0, 0) ||
        !WinHttpReceiveResponse(request.get(), nullptr))
        return XML_IO_LOAD_ERROR;
    DWORD status = 0;
    DWORD statusSize = sizeof(status);
    if (!WinHttpQueryHeaders(request.get(), WINHTTP_QUERY_STATUS_CODE | WINHTTP_QUERY_FLAG_NUMBER,
                             WINHTTP_HEADER_NAME_BY_INDEX, &status, &statusSize,
                             WINHTTP_NO_HEADER_INDEX) || status < 200 || status >= 300)
        return XML_IO_LOAD_ERROR;

    std::vector<unsigned char> bytes;
    for (;;) {
        DWORD available = 0;
        if (!WinHttpQueryDataAvailable(request.get(), &available))
            return XML_IO_LOAD_ERROR;
        if (!available)
            break;
        size_t offset = bytes.size();
        bytes.resize(offset + available);
        DWORD read = 0;
        if (!WinHttpReadData(request.get(), bytes.data() + offset, available, &read))
            return XML_IO_LOAD_ERROR;
        bytes.resize(offset + read);
    }
    if (bytes.empty())
        return XML_IO_NO_INPUT;

    std::string charset = responseCharset(request.get());
    xmlParserInputFlags memoryFlags = static_cast<xmlParserInputFlags>(
        static_cast<unsigned>(flags) & ~static_cast<unsigned>(XML_INPUT_BUF_STATIC));
    xmlParserInput *input = xmlNewInputFromMemory(url, bytes.data(), bytes.size(), memoryFlags);
    if (!input)
        return XML_ERR_NO_MEMORY;
    xmlCharEncodingHandler *handler = charset.empty() ? nullptr :
        xmlFindCharEncodingHandler(charset.c_str());
    if (handler && xmlInputSetEncodingHandler(input, handler) != XML_ERR_OK) {
        xmlFreeInputStream(input);
        return XML_IO_ENCODER;
    }
    *out = input;
    return XML_ERR_OK;
}

xmlParserErrors resourceLoader(void *, const char *url, const char *, xmlResourceType,
                               xmlParserInputFlags flags, xmlParserInput **out) noexcept {
    try {
        if (isHttp(url))
            return loadHttp(url, flags, out);
        return xmlNewInputFromUrl(url, static_cast<xmlParserInputFlags>(
            static_cast<unsigned>(flags) | static_cast<unsigned>(XML_INPUT_UNZIP)), out);
    } catch (...) {
        if (out)
            *out = nullptr;
        return XML_ERR_NO_MEMORY;
    }
}
}

xmlDocPtr xlaunchReadXml(const char *location) {
    if (!location)
        return nullptr;
    xmlParserCtxtPtr context = xmlNewParserCtxt();
    if (!context)
        return nullptr;
    xmlCtxtSetResourceLoader(context, resourceLoader, nullptr);
    xmlDocPtr document = xmlCtxtReadFile(context, location, nullptr, XML_PARSE_UNZIP);
    xmlFreeParserCtxt(context);
    return document;
}
