# 输入处理修复主线整合验证

日期：2026-09-10。状态：完整构建、73 项测试、独立运行验证和代码审查通过，输入处理修复已整合至线性 master。

## 范围与来源

从主线 `3d1b6c9478c4e5225e29000e47cb2f96dc612b66` 开始，将维护者已实际使用的候选 `c06e0db1669afaee649bdaf407c7c76c9fa3ae56` 恢复到当前源码布局。普通保留目录为 `D:/File/Program/GitHub/vcxsrv-input-20260909-2110`，恢复材料为主仓库 `.local-validation/reorganize-20260910/pending-input-source.patch`。

生产改动仅限 `src/xorg-server/os/io.c`：两条请求长度转换前检查，以及未完成丢弃数据时的接收缓冲区共享条件。不可表示的请求长度调用 `YieldControlDeath()` 后返回 `-1`，沿用原有客户端终止约定；`dix/dispatch.c` 不变。不改变菜单、多显示器、剪贴板、OpenGL 或其他组件的实现。

恢复 `tools/tests/native/xserver_input.c` 和 `tools/tests/test_xserver_input.py`；Python 测试仅将 include 搜索目录适配为当前 `src/`、`third_party/`、`include/` 布局。原生测试直接编译生产解析器，在 MSVC AddressSanitizer 下执行，无网络连接。

原始上游三笔修复、实际下载链接、下载日期、补丁 SHA-256、作者以及本地适配分别记录于[来源文档](../dependencies/SOURCES.md)及[来源 JSON](../dependencies/SOURCES.json)。本次复用已经归档的原始资料，三份补丁重新计算的 SHA-256 均与历史导入记录相同，不创建上游源码分支，也不把本地适配声称为原始上游代码。

## 本次验证

- 固定构建源码提交：`e356623330a568afd254aa8804d6fafdfef29d95`。后续提交仅更新来源、状态和验证文档，不改变已构建的产品源码与测试。
- 新构建目录：`D:/File/Program/GitHub/zzxsrv-input-20260910`。
- 新运行目录：`D:/File/Program/GitHub/zzxsrv-input-20260910/dist/x64/Release`。
- 原始证据：该目录 `.local-validation/input-integration-20260910/`；收尾时同步至主仓库相同相对位置。

| 检查 | 结果 |
| --- | --- |
| 未修复源码上的 12 项输入测试 | 7 通过、5 项预期失败；失败来自异常长度和未完成丢弃的断言 |
| 恢复修复后的相同测试 | 12 项通过、0 跳过；MSVC AddressSanitizer |
| 与已实测候选的源码对应 | `io.c` 与候选一致；`dispatch.c` 保持不变；原生 C 测试不变，Python 仅更新 include 路径 |
| 完整 x64 Release All 构建 | PASS，退出码 0；14:26:03–14:37:01（UTC+08:00），新目录无旧构建缓存 |
| 全部项目测试，启用本地工具及真实运行 | PASS：73 项，0 失败、0 跳过，23.618 秒；即当前 61 项加恢复的 12 项输入测试 |
| 独立运行依赖、认证启动、根窗口查询及清理 | PASS；35 个 EXE/DLL 依赖检查通过；独立 display 97，使用临时认证，不关闭访问控制 |
| 旧运行文件、便携文件集合及字体 | PASS：280 个既有 EXE/DLL 的 SHA-256 不变；5,129 个唯一便携文件，集合与源码分层构建一致；4,297 个压缩字体完整解压且 PCF 文件头正确 |
| 独立代码审查 | 无阻断问题；核对失败返回与调用方契约、候选等价性、测试及补丁来源；边界见下文 |

完整构建命令：

```powershell
.\scripts\build\buildall.ps1 -Jobs 30 `
  -EnvironmentReport .local-validation/input-integration-20260910/environment.json
```

All 阶段仍使用继承的 libxml2 预编译文件，不代表完成了该依赖的源码重建。

全部测试命令为 `python -B -m unittest discover -s tools/tests -p 'test*.py' -v`，通过记录在证据目录的 `run-tests.ps1 -Runtime -Log tests.log` 初始化 x64 MSVC 环境；设置 `VCXSRV_TEST_LOCAL_TOOLS=1`、`VCXSRV_TEST_RUNTIME=1`，运行目录为本次新目录，`VCXSRV_SOURCE_COMMIT` 为上述固定源码。工具路径与版本见 `environment.json`；MSVC 14.44、Windows SDK 10.0.26100.0、Python 3.14.2。构建、完整测试和独立运行结果分别在 `build-result.json`、`tests.log`、`runtime/result.json`。

原生测试源码明确使用 `/fsanitize=address`，本次运行通过；没有另外保留临时插桩二进制或完整编译命令作为脱离源码的独立插桩证明。解析器测试不动态覆盖完整 `Dispatch()` 生命周期或真实 socket 的所有异常请求状态，不能据此声称整台服务器已获得全面安全验证。调用方负值关闭客户端的契约由限定范围源码审查确认。

## 人工反馈与保留问题

维护者明确确认本次实测的是 `vcxsrv-input-20260909-2110`。程序打开、关闭、再次打开，窗口基本操作、键盘输入和多窗口使用正常。双向文本剪贴板、OpenGL、中文专项及 SSH 断开重连未验证。

GUI-001（已展开的 gitk 菜单在主窗口跨屏后停留原屏）按维护者要求暂缓排查；尚未独立复现，也未确认是否属于回归。本次不修改菜单实现，不将其描述为已修复。详见[兼容性记录](../maintenance/COMPATIBILITY.md)。新布局下的自动验证与历史候选的人工反馈分别记录，不声称新构建已做全部人工场景验收。

## 整合与回退

以快进方式整合至线性 master，不生成 merge commit；临时工作区解除登记，临时分支清理，源码、运行目录及验证材料保留。原候选和已有运行目录不覆盖；主仓库此前编译的 `dist/x64/Release` 不会因源码快进而自动更新，要运行本次新程序应使用上述新目录，或在主仓库重新执行构建命令。

输入代码回退点为本次起点 `3d1b6c9478c4e5225e29000e47cb2f96dc612b66`；需要回退时可对输入代码提交进行普通 revert 并同步来源和状态文档，不重写共享历史。既有 XFIXES 与原输入候选运行目录继续保留。输入修复之外的 R3 分组继续保留为后续任务，下一组为 RENDER/RECORD。
