# libxml2 编码依赖与文件读取兼容性调查

日期：2026-09-15。接续[来源与重建评估](2026-09-15-libxml2-assessment.md)，本轮完成隔离构建和正常配置兼容性调查，未替换生产依赖，也未产生可交付的整包候选。

## 结论

官方 libxml2 2.15.4 加原生 GNU libiconv 1.19、现有 zlib 1.3 的组合可以构建，恢复了上一轮缺失的 GBK/GB18030 编码能力。9 组正常编码用例在旧库和新组合中均能正确读取属性、保存为 UTF-8；实际 XLaunch 配置往返及 Fontconfig 缓存消费者也通过。

文件读取仍有两个需要在正式迁移中处理的真实差异：旧 2.9.1 能以默认选项读取 gzip 文件和 HTTP 地址；新 2.15.4 默认均失败。gzip 在加入 `XML_PARSE_UNZIP` 后通过；HTTP 需要应用层读取适配，不能靠打开 libxml2 的历史 HTTP 构建选项恢复。

推荐采用固定官方源码加明确记录的 MSVC 适配，正式替换时同时保留压缩配置和 HTTP 配置读取能力。不能仅用本轮 DLL 覆盖现有运行目录。

## 编码库来源与差异

下载 [GNU libiconv 1.19 官方源码包](https://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.19.tar.gz)，本地计算：

- SHA-256：`88dd96a8c0464eca144fc791ae60cd31cd8ee78321e67397e25fc095c4a19aa6`。
- SHA-512：`1e8150f9bca907579330cd9c44ebbee46a260271fbe8f50d5ee24a39ef29c8d254505e85c3409324f7440596da711a8bd49e89f848a6be0cb3238a58c24aaecd`。

这些是下载包的本地计算值。本轮没有取得可核对的官方发布摘要，也没有验证发布签名，不表述为已通过官方校验。

MSVC 适配取自 [Winlibs libiconv 固定提交](https://github.com/winlibs/libiconv/tree/accac417318a3eef7402685a268cab8037e62ba1)，提交 `accac417318a3eef7402685a268cab8037e62ba1`。对应 codeload ZIP 的本地 SHA-256 为 `f1fed410a2a93570f1f669148664cecebbf816e2856e30e57926009b4286e101`。这是第三方 Windows 适配来源，与 GNU 官方发布分别记录。

将该提交的 `source/` 与官方包逐文件比较，仅统一 CRLF/LF 后：

| 类别 | 结果 |
| --- | --- |
| 相同文件 | 1104 个，包括编码转换表、`localcharset.c`、`compat.c` 和许可证文件 |
| 修改文件 | `lib/aliases.h`、`lib/canonical.h`、`lib/canonical_dos.h`、`lib/canonical_local.h`、`lib/iconv.c` |
| 新增文件 | `config.h`、`include/iconv.h`、`lib/aliases.h.orig`、`lib/localcharset.h` |
| 官方文件缺失 | 0 个 |

主要编译差异为 Windows 指针整数类型转换、相关平台声明及 `ICONV_CONST` 定义；生成头文件和配置另外保留。完整差异见本地 `compiled-source.diff`，不能以仓库中旧的 `libiconv.diff` 代替此次实际比较。现有项目公共 `include/iconv.h` 的 1.9 版本声明仍属于旧组件，不当作新库头文件使用。

## 构建与依赖

直接构建已检查的 `MSVC17/libiconv_dll/libiconv_dll.vcxproj`，未运行包含清理操作的 `winlibs.mak`。使用 VS2022 MSVC 19.44.35227、Release x64、动态 CRT；将项目硬编码的 SDK 10.0.20348.0 覆盖为本机 10.0.26100.0。构建退出 0，实际生成 `MSVC17/x64/bin/libiconv.dll` 和 `MSVC17/x64/lib/libiconv.lib`。DLL 导出的 `_libiconv_version` 为 `0x0113`，即 1.19。

试验构建仍有整数宽度、const 限定和 MSB8012 输出名称不一致警告。上游适配项目还显式关闭 `RandomizedBaseAddress`。正式集成应提供与本仓库一致的构建定义，校正输出属性并启用地址随机化；本轮不将这个试验项目原样作为产品构建规则。

libxml2 使用上一轮经官方摘要核对的 2.15.4 源包与 VS 自带 CMake 3.31.6-msvc6，明确指定新 iconv 头文件和导入库、现有 zlib 头文件及已验收工作区的 x64 `zlib1.lib`。配置为 shared、ICONV/ZLIB 开启、TESTS/PYTHON 关闭；配置和构建均退出 0，运行版本为 `21504`。

新 DLL 的实际导入表包含 `libiconv.dll`、`zlib1.dll`、`bcrypt.dll` 和 Windows/MSVC CRT；新 iconv DLL 仅依赖 Windows/MSVC CRT。此结果限于两个新 DLL，不构成删掉整包 GCC/pthread DLL 的依据。

## 正常场景结果

旧库为现有 x64 2.9.1，新库为上述 2.15.4 + iconv 1.19 + zlib 组合。两者在独立进程加载。输入均为自建正常 XML，不读取用户配置。

| 编码场景 | 旧库 | 新组合 |
| --- | --- | --- |
| UTF-8、UTF-16 中文及转义属性 | 2 组通过 | 2 组通过 |
| GBK、GB18030 常用中文 | 2 组通过 | 2 组通过 |
| GB18030 扩展汉字 `𠀀` | 通过 | 通过 |
| BIG5 繁体中文 | 通过 | 通过 |
| SHIFT_JIS 日文、EUC-KR 韩文、WINDOWS-1251 俄文 | 3 组通过 | 3 组通过 |

每组均检查解析成功、属性值一致、保存后 UTF-8 文件内容正确。此为 9 组正常兼容用例，不代表覆盖所有字符或所有历史编码别名。

| `xmlReadFile` 文件读取场景 | 旧库 | 新组合 |
| --- | --- | --- |
| 普通 XML，选项 0 | 通过 | 通过 |
| gzip XML，选项 0 | 通过 | 失败 |
| gzip XML，显式 `XML_PARSE_UNZIP` | 通过；旧头文件未定义该选项位 | 通过 |
| 本地 HTTP 服务上的普通 XML，选项 0 | 通过 | 失败 |

HTTP 服务仅监听 `127.0.0.1` 临时端口，返回自建 XML，测试结束关闭。未测试代理、重定向、HTTP Content-Encoding、字符集响应头、认证或 HTTPS；不从这一条直接请求结果推断完整网络行为兼容。

另外，按新头文件重编实际 `xlaunch/config.cc`，原代码不改动，中文/转义属性、窗口模式、显示号和剪贴板设置保存/加载通过。既有 `libfontconfig.lib` 重新链接新 libxml2 后，字体缓存创建、另一个进程重载、列举与 CFF 匹配通过，两阶段均为 `cache-patterns=2 list-patterns=2 unique-files=2`。这仍不是 Fontconfig 全部源文件按新头文件重编的结果。

## 正式实施方案与验收边界

1. 以官方 libiconv 1.19 为基础导入所需库源码、许可证、配置头和可逐项解释的 MSVC 适配；来源清单分别记录 GNU 包与 Winlibs 固定提交。同步公共头文件、原生构建、导入库名和打包规则，避免混用旧头文件及 DLL。
2. 将 libxml2 2.15.4 接入现有构建，显式开启 ICONV/ZLIB，保持本仓库正常使用的 SAX1/PUSH/TREE/OUTPUT/线程功能。重新编译 Fontconfig、XLaunch 和 xclock，并检查完整 DLL 依赖闭包。
3. XLaunch 当前 `config.cc` 使用 `xmlReadFile(filename, NULL, 0)`。本地配置加载增加 `XML_PARSE_UNZIP`，使旧的 gzip 使用方式继续有效。用原代码失败、适配后通过的对照验证实际 CConfig 路径。
4. HTTP 建议使用 Windows WinHTTP 提供传输，通过新版 libxml2 的解析上下文资源加载接口接入，避免修改全局加载器。保留原 URL 作为解析基址，对本地文件继续使用库的默认加载方式。此为待实施方案，本轮没有编写或验证 WinHTTP 适配；实现时需对照旧行为明确重定向、响应字符集、gzip 响应、错误状态和代理处理，不把简单直连用例当作完整兼容。
5. 将正常编码、压缩配置及 HTTP 兼容用例纳入持久回归，再执行完整构建、全部自动回归、独立运行检查，最后在新目录进行实际使用验收。

本轮没有执行整包构建、370 项完整回归、上游完整测试或 GUI 验收。已验收 Fontconfig 运行目录的 5129 个文件与原记录逐一核对 SHA-256，全部保持不变。生产依赖清单未改动，旧二进制来源未知项也未借此次新库调查标记为已解决。

## 本地证据

忽略目录 `.local-validation/libxml2-compat-20260915/` 保存两份源码归档和来源 JSON、`source-comparison.json`、`compiled-source.diff`、`build-iconv.log`、`build-results.json`、libxml2 构建日志、`compat-results.json`、`consumer-results.json`、`native-dependents.txt` 及 `verification.json`。其中源码副本、构建产物、驱动脚本与配置均为一次性调查材料。
