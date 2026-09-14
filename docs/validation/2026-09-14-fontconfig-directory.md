# Fontconfig Windows 目录枚举验证

状态：本地修复及候选自动验证完成，等待新目录的实际使用反馈；未合入 master、未 push。370 项测试通过、0 跳过，缓存创建及重载均为 2 条记录，独立运行检查 PASS。构建曾中断并留下损坏中间产物，已按阶段重建恢复，经过与失败记录见下文。

## 问题与修正

R4 正常字体测试发现两字体目录产生三条缓存记录。`FcCompatReaddirWin32` 原先先令返回名字指向 `fdata.cFileName`，再调用 `FindNextFile` 覆盖该缓冲；调用者收到的名字已是下一项，类型却仍来自当前项，最后一项重复。

修复在每个 DIR 内记录首次读取状态，第一次返回 FindFirstFileEx 的条目，后续调用开始时才推进 FindNextFile。当前条目的名字和类型保持对应；结束状态保留，重复读取 EOF 仍返回 NULL。

同组普通路径测试还发现 `FcCompatOpendirWin32` 错用空指针判断失败。根据 [Microsoft FindFirstFileExA 文档](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-findfirstfileexa)，失败返回 INVALID_HANDLE_VALUE。现改为正确判断，在释放内存前记录系统错误，释放分配并直接返回 NULL；文件或路径不存在映射 ENOENT，其他错误保留 EACCES 通用映射。

只修改 `third_party/fonts/fontconfig/src/fccompat.c` 一个生产文件，Fontconfig 仍为继承的 2.16.0；这是依据本地复现和平台 API 契约编写的修正，没有导入或冒充上游 patch。来源见 [JSON](../dependencies/SOURCES.json) 的本地兼容修正记录。

基线 `1bb897d4a368521e5aaab9e11c686c9c3ccebc20`；修复提交 `cd444aa641d50355c0d7b47f4a7167b78e313e45`。工作区 `D:/File/Program/GitHub/zzxsrv-fontconfig-20260914`，计划见 [检查项](../plans/2026-09-14-fontconfig-directory.md)。

## 定向回归

`test_fontconfig_directory.py` 从生产 fccompat.c 抽取完整 DIR 结构及三个函数原文，使用真实 fcwindows.h 类型和 Windows 文件系统，不重写枚举算法、不模拟 FindFirst/FindNext。编译器为本机 x64 MSVC，开启 /W4 /WX；未声称 ASan 插桩。

| 阶段 | 结果 |
| --- | --- |
| 同组测试、旧生产源码 | 7 项中 5 项失败：重复文件及打开失败返回错误 |
| 同组测试、修复源码 | 7 项通过，0 跳过 |

命令为 `.local-validation/fontconfig-20260914/run-target.ps1 -Pattern test_fontconfig_directory.py`。旧源码通过测试专用环境变量 VCXSRV_TEST_FC_SOURCE 指向固定基线副本，不切换 HEAD 或污染生产构建。原始日志为 `directory-final-red.log`、`directory-final-green.log`。早期测试对“文件当作目录”的 errno 预期过窄；核实现有通用映射后修正测试预期，再用同一最终测试分别确认旧代码失败、新代码通过。

原 R4 Fontconfig 公共 API 测试恢复严格数量断言：缓存 2 条、列表 2 条，每个目标字体恰好 1 条。已使用新构建的真实库验证磁盘缓存创建、另一个进程重载与字体匹配，两阶段均为 `cache-patterns=2 list-patterns=2 unique-files=2`；R4 的同一正常场景曾为 3/2/2。

## 独立审查

独立审查覆盖基线至修复提交的 4 个文件及 fcdir/fcxml/fccache 调用者，未发现功能、内存或句柄生命周期的阻塞缺陷。另核对旧测试副本与基线 Git blob 一致：`4414cb60560bd3aa498ad8ac062ab4cc9afbc8e4`。完整报告保存在证据目录 `review.md`。

测试范围保留两点：计数断言排除 `.`/`..`，不单独保证点条目次数；普通文件只断言不为目录，兼容带 ARCHIVE 属性时既有 DT_UNKNOWN 行为。单文件和混合目录用例能检出本次重复及名字/目录属性错配。未将这些用例称为完整目录 API 契约测试。

## 完整验证

完整构建固定生产提交 `cd444aa641d50355c0d7b47f4a7167b78e313e45`：

```powershell
.\scripts\build\buildall.ps1 -Jobs 30 -EnvironmentReport .local-validation/fontconfig-20260914/environment.json
```

首次构建会话在 OpenSSL 阶段中断：23:08 检查时会话 ID 已失效、没有构建进程或最终结果文件，日志尾部含 NUL；原因未确定，不能计为构建通过。原始记录保留为 `build-interrupted.log`、`environment-interrupted.json` 和 `build-interrupted.json`。HEAD 保持不变，随后重新执行同一 All 命令。

第一次重跑在 23:09 以退出码 1 结束，OpenSSL 编译器报 C1033，无法打开此前留下的 `release64/app.pdb`。记录为 `build-pdb-failure.log/json`。核对该目录没有受 Git 跟踪的源码且路径位于本候选工作区后，将整批中间产物保留到证据目录 `openssl-interrupted-release64`，重新生成 OpenSSL 构建目录再执行 All；没有改动生产源码或旧 R4 产物。

第二次重跑完成 OpenSSL 后，在 23:18 因 mhmake 的 C1051 退出 1；其 `Release64/mhmake.pdb` 文件头实测为全零，MSBuild 同时报告无效 tlog。日志为 `build-mhmake-failure.log/json`。核对路径及无受跟踪文件后，将工具生成目录保留到 `mhmake-interrupted-Release64`，重新执行 All；不删除或移动源码。

第三次 All 重跑在 23:28 完成依赖和 mhmake 后，因 XLaunch 中间 PDB 的 C1051 退出 1；保留在 `build.log`、`build-result.json`。检查候选目录内 354 个 PDB，发现 XLaunch、libX11 和 pthreads 共 7 个异常文件头，详见 `pdb-header-audit.json`。为避免逐项遇到残留损坏，在核对全部路径位于候选工作区且无受跟踪源码后，统一保留 100 个 obj64 生成目录及 pthreads 的 3 个生成文件到 `server-interrupted`，移动清单为 `server-artifact-moves.json`。

恢复采用已完成的 FreeType/OpenSSL/mhmake 构建，重新运行 `nmake /nologo VC-static`，再执行 `scripts/build/buildall.ps1 -Stage Server -Jobs 30` 重建全部服务器组件与便携目录。此阶段单独记录 `pthreads-rebuild.log`、`build-server.log`、`build-server-result.json` 和 `environment-server.json`；不将此前 All 退出 1 改写为退出 0。

首次恢复脚本漏设项目环境变量 IS64=1，生成的 pthreads 库缺少文件名后缀 64，服务器链接因找不到 `libpthreadVC364.lib` 失败。该脚本错误已修正，按正式入口设置 IS64=1、CFLAGS=-FS 后重新构建；失败证据保留为 `resume-missing-is64-*`，不将其归因于产品源码。

最终恢复在 23:31:36–23:33:36 完成，pthreads 与 Server 两阶段退出码均为 0，构建前后 HEAD 保持修复提交不变。证据目录为本工作区 `.local-validation/fontconfig-20260914/`。

| 验证 | 实际结果 | 证据 |
| --- | --- | --- |
| 完整构建流程恢复 | All 已完成依赖及构建工具，重新构建 pthreads、全部服务器组件和 Portable 后成功 | build.log、build-server-result.json |
| 字体 API 与消费者 | 10 项通过、0 跳过，0.540 秒；缓存创建/重载为 2/2/2，CFF 字体名称匹配正确 | font-consumers.log |
| 完整自动回归 | 370 项通过、0 跳过，46.094 秒；包含新增 7 项目录回归及原有运行/字体测试 | tests-final.log |
| 独立 runtime | PASS，1.548 秒；依赖、版本、显示端口、认证、启动、根窗口及清理均通过 | runtime/result.json |
| 便携目录 | 5129 个实际文件，清单与 R4 一致；4297 个压缩 PCF 字体逐一解压并核对格式头 | artifact-verification.json、portable-files.json |
| 旧运行目录 | 525 个既有 EXE/DLL 哈希不变，0 个变化 | old-runtime-comparison.json |
| 重建后的 PDB 文件头 | 检查 435 个文件，未再发现异常头；仅为文件头检查，不声称完整数据库校验 | pdb-header-final.json |
| 来源与文档 | 196 项组件来源、39 条上游补丁记录不变；本地修正记录增至 3 条，107 个本地文档链接有效 | source-docs-verification.json |

完整 suite 使用 `VCXSRV_TEST_LOCAL_TOOLS=1`、`VCXSRV_TEST_RUNTIME=1` 和修复提交 `VCXSRV_SOURCE_COMMIT`，未把依赖缺失转为跳过。runtime-suite-evidence 中保留的故意缺失 DLL 等失败记录属于相应用例的预期负向结果；独立 runtime/result.json 为本候选的整体运行结果。

## 候选人工验收

自动验证已经通过。请从 `D:/File/Program/GitHub/zzxsrv-fontconfig-20260914/dist/x64/Release/xlaunch.exe` 启动，沿用日常连接方式，检查启动、gitk 操作、中文显示及退出后重启。方便时在 gitk 设置中切换字体和字号，观察是否缺字、异常布局或退出；没有测试的项明确写“未测”。Fontconfig 缓存内部数量由本轮自动回归核对，无需维护者手工清空缓存或检查内部记录。

本候选尚无实际使用反馈，未合入 master、未 push；R4 反馈只适用于原运行目录。

## 边界

本轮验证新创建的临时字体缓存。既有磁盘缓存没有被自动批量删除或改写；需要重新扫描生成后才能获得去重后的记录。未修改用户缓存配置。

本机普通 ANSI 路径、正常文件和目录用于回归；Unicode/超长路径、网络文件系统、目录内容并发变化及其他 Win32 错误映射不属于本轮扩展范围。传统字体、OpenGL 等人工未测项和此前 libXfont2 异常输入验证缺口继续保留，GUI-001 不重新开展。
