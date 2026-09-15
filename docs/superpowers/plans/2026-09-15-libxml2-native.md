# libxml2 原生替换实现计划

> **面向 AI 代理的工作者：** 使用 subagent-driven-development 逐任务实现，依赖导入与构建、配置读取各自审查，最后整体审查。

**目标：** 从固定源码构建 libxml2 2.15.4 与 GNU libiconv 1.19，保留现有编码、gzip 和 HTTP 配置加载，交付独立 x64 Release 候选。

**架构：** 保持现有 Windows 原生构建入口和 Portable 流程；CMake 仅用于 XML 依赖子构建。XLaunch 使用解析上下文局部资源加载器和 WinHTTP 读取 HTTP 资源，本地文件走 libxml2 默认加载并启用解压。

**技术栈：** MSVC v143、Windows SDK、CMake、Python unittest、libxml2/iconv/zlib、WinHTTP。

**规格：** [兼容性报告](../../validation/2026-09-15-libxml2-compatibility.md)及其正式实施方案。

## 全局约束

- 独立目录 `D:/File/Program/GitHub/zzxsrv-libxml2-20260915`，不修改已验收运行目录，不推送。
- 保留 libxml2 SAX1/PUSH/TREE/OUTPUT/线程、ICONV/ZLIB 功能。
- 本地源码不下载构建依赖；源码导入记录版本、固定来源、许可证、补丁及文件摘要。
- 支持构建入口已有的 x64/Win32、Release/Debug 参数；本轮完整产品验收只针对 x64 Release。
- 先用真实消费者验证新版未适配时 gzip/HTTP 失败，再实现和验证；正常编码与缓存也纳入回归。
- 不删除既有 R3 工作区或重试已被自动审批拒绝的 libXfont2 异常输入任务。

## 任务 1：固定源代码与原生构建

文件：`third_party/libxml2/`、`third_party/libiconv/`、`include/iconv.h`、`scripts/build/`、消费者 makefile、installer manifests、依赖文档与 `tools/tests/test_xml_build.py`，更新现有依赖路径测试。

- [x] 导入官方 libxml2 2.15.4 源码到 `third_party/libxml2/source/`，官方 libiconv 1.19 加逐项记录的 Winlibs MSVC 适配到 `third_party/libiconv/source/`。原旧文件待引用切换并检查后清除。
- [x] 定义固定输出：`third_party/libxml2/build/<Architecture>/<Configuration>/libxml2.{dll,lib}` 和 `third_party/libiconv/build/<Architecture>/<Configuration>/libiconv.{dll,lib}`；生成 XML 头文件目录由 CMake 构建路径明确提供。
- [x] 先增加构建/打包契约测试，确认旧规则失败；实现依赖子构建及消费者/打包切换，确认通过。
- [x] 编码库以本机原生 CRT 编译，修正 MSVC 工程输出和地址随机化设置，不复用 Winlibs 清理/打包脚本。
- [x] 原生依赖构建与运行编码验证通过，记录来源清单并审查导入完整性。

## 任务 2：配置兼容与持久回归

文件：`src/xorg-server/hw/xwin/xlaunch/config.cc`、新增局部 XML 输入模块、对应 makefile、`tools/tests/test_xml_config.py` 与 `tools/tests/native/xml_config.cpp`。

- [x] 用原有实际 CConfig 与新库建立 UTF-8/UTF-16/GBK/GB18030 等正常编码、gzip、HTTP 基线；gzip/HTTP 必须因缺少适配而失败。
- [x] 实现局部解析上下文加载、gzip 文件读取、WinHTTP HTTP 读取；处理句柄寿命、失败状态、重定向、响应字符集及压缩响应。避免全局加载器副作用和隐式认证。
- [x] 回归普通文件及中文路径、编码往返、gzip、直连/重定向 HTTP、响应字符集、压缩响应和正常 HTTP 错误状态；服务只绑定回环地址并自动关闭。
- [x] 保留现有 Save/Load 设置语义，独立审查实际消费者代码和回归结果。

## 任务 3：完整集成与候选

文件：验证报告、计划状态、测试指南。

- [x] 执行完整 x64 Release 构建，重新编译全部消费者，验证 Portable 文件和 DLL 依赖闭包。
- [x] 在新工作区运行全部本地自动测试与独立运行检查，修复新失败后按需重测。
- [x] 整体代码审查、记录版本/来源/测试范围/人工未测项，提交候选并给出新目录及最少人工验证步骤。
- [x] 2026-09-15 取得“R5 正常 ，合入吧”的反馈后快进整合主线；保留所有既有候选目录，整合验证见 [报告](../../validation/2026-09-15-libxml2-native.md)。
