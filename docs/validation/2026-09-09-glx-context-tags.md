# GLX 上下文标签修复记录

本次回补 GLX 上下文标签生命周期修复；不代表已完成 X Server 全部后续公告的核对。

## 来源与范围

- 本地起点：`59cca4a6c`，工作分支：`codex/update-xserver-security`。
- 上游提交：`2779affbdb4354e894f490e56f962527d6125043`，作者 Peter Hutterer，作者日期 2026-05-31。
- [X.Org 原始提交](https://gitlab.freedesktop.org/xorg/xserver/-/commit/2779affbdb4354e894f490e56f962527d6125043)；本次从 [XQuartz 镜像的同一 Git 提交](https://github.com/XQuartz/xorg-server/commit/2779affbdb4354e894f490e56f962527d6125043) 核对差异。
- 对应 CVE-2026-56000；上游标注引入问题的提交为 `4781f2a5a8c2`。本地已存在它所描述的“延后释放旧 tag”行为，无需再导入该引入问题的提交。
- 只应用 `glx/vndcmds.c` 的生产 hunk，路径适配为 `xorg-server/glx/vndcmds.c`，内容一致（5 行增加、3 行删除）。未整包替换 X Server、修改产品版本号或升级 OpenSSL。
- 原始文件版权与许可声明完整保留。上游测试依赖本仓库没有的 `pyxtest` 框架，因此编写本地 MSVC 测试，不导入该框架。
- 原会话取得的补丁证据：`.local-validation/glx-security/upstream.patch`，SHA-256 `EB79DF6631B0444F5931280D5490B3DC47BA1F48D48DE1FA262C4E7F4B6C35BD`；元数据为同目录 `upstream.json`。本轮未下载源码包或安装工具。

## 根因与回归证据

旧 `oldTag` 指向客户端 tag 数组；分配新 tag 时数组可能搬移，随后释放旧 tag 就会写入已释放内存。修复将旧 tag 的清理移至成功解除旧 context 之后、新 tag 分配之前。解除失败时仍保留旧状态。

测试直接编译实际 `vndcmds.c` 与 `vndservermapping.c`。仅替换分配器和外围服务器服务；未使用的链接替身被调用时立即终止。每个场景使用独立进程，通过 MSVC AddressSanitizer 检查内存访问。

| 验证 | 结果 | 证据 |
| --- | --- | --- |
| 修复前回归 | 8 项中 3 项失败：正常及交换字节序的满数组切换触发 ASAN heap-use-after-free；新 context 创建失败路径残留旧 tag | `.local-validation/glx-security/red-tests.log` |
| 修复后回归 | 8 项通过，0 跳过 | `.local-validation/glx-security/green-tests.log` |
| 其他已覆盖场景 | 无旧 context 的扩容、相同 context、解除绑定、解除失败、分配失败、非法 context/tag | `tools/tests/test_glx_context_tags.py` |
| 独立代码审查 | 未发现阻断项；生产差异与上游一致，已复核测试与已有日志 | 当前接续任务的只读审查记录 |

复跑：在 x64 Visual Studio 开发环境设置 `VCXSRV_TEST_LOCAL_TOOLS=1`，执行 `python -B -m unittest discover -s tools/tests -p test_glx_context_tags.py -v`。使用 `/fsanitize=address`；缺少编译器、头文件或链接依赖会明确失败。

测试编译准备中修正了 `damage.h` 的包含路径、重复定义的函数和独立链接所需的服务替身。上述准备错误不算问题复现；红灯证据来自测试已成功编译后的 ASAN 与状态断言失败。

## 构建时发现并修复的问题

三个代码改动分开提交，便于审查和回退：

| 本地提交 | 改动 | 验证 |
| --- | --- | --- |
| `7338738b2` | GLX 上游修复及 8 项 ASAN 回归 | 上述红绿测试及独立审查 |
| `9bc552911` | Fontconfig 的 gperf 改为从标准输入读取 | 旧生成头文件 MSVC 预处理退出 2，新文件退出 0；独立比较确认生成表和查询代码相同 |
| `5f6c9a930` | OpenSSL 的 JOM 构建固定为 `/J1` | 两次并行失败、完整串行依赖构建及串行续建成功；独立审查确认其余阶段仍采用用户指定的 Jobs |

gperf 3.0.1 把文件参数中的 Windows 反斜杠原样写进 `#line`；工作区路径里的 `\xserver-security` 触发 MSVC C2153。标准输入模式省去这些路径行标记，保留输入依赖、输出位置及 `converttype.py`。实际构建已重新生成头文件并编译通过；单独预处理的红绿证据在 `.local-validation/glx-security/gperf-red.log` 与 `gperf-green.log`。

OpenSSL 的工具和测试共享 `app.pdb`，即使已有 `-FS`，本机并行构建仍两次出现 C1041。当前仅将 OpenSSL 阶段固定为串行；FreeType、mhmake 和服务器仍保留 `-Jobs` 并行，NMake 回退与失败传播不变。代价是 OpenSSL 完整编译耗时增加，源码版本保持 3.4.1。

失败与接续构建证据均位于开发 worktree 的 `.local-validation/`：

| 运行目录 | 结果 |
| --- | --- |
| `glx-build-20260909-160229` | 初次并行 All 在 OpenSSL 的 app.pdb 失败；已提取 `pdb-errors.txt` |
| `glx-build-20260909-160458` | 完整串行 Dependencies 成功；再执行并行 All 又触发相同错误，保留第二份 `pdb-errors.txt` |
| `glx-build-20260909-161554` | OpenSSL 串行续建成功；Server 暴露 gperf 路径错误 |
| `glx-build-20260909-161956` | `9bc552911` 分阶段 Server/Portable 构建、51 项测试、运行验证全部通过；旧 70 个 EXE/DLL 未变 |

分阶段结果来自中断后的接续构建。下面单独记录最终源码的新检出验收。

## 最终源码的干净构建

- 固定源码提交：`5f6c9a930af94355d4c5faca994c78b34b0137e0`。
- 新检出目录：`D:\File\Program\GitHub\vcxsrv-glx-20260909-1625`。
- 新程序目录：该检出下的 `dist\x64\Release`。
- 原始证据：该检出下的 `.local-validation\glx-build-20260909-162448`。
- 结果：**PASS**。开始于 2026-09-09 16:24:48 +08:00，结束于 16:36:43。
- 首次检出状态为空；All 构建后受跟踪文件无变化。报告在后续文档提交中更新，不改变二进制对应的源码提交。

| 验收 | 实际结果 | 证据 |
| --- | --- | --- |
| 全新检出 x64 Release All 构建 | PASS，退出 0；OpenSSL 自动 `/J1`，其他阶段 `-Jobs 8` | `environment.json`、`build.log` |
| 全部脚本与运行集成测试 | PASS，51 项，0 失败、0 跳过，31.981 秒；包含 8 项 GLX ASAN 回归 | `tests.log` |
| PE 架构与直接/延迟导入 | PASS，35 个 EXE/DLL | `runtime/dependencies.json` |
| 版本、认证、根窗口查询 | PASS，临时 Xauthority，显示号 97，根窗口 1920×1080 | `runtime/result.json` 及子进程日志 |
| 测试子进程及认证文件清理 | PASS | `runtime/result.json` 的 cleanup 步骤 |
| 旧运行目录保护 | PASS，主目录及旧基线目录共 70 个 EXE/DLL 的哈希不变 | `old-artifacts-before.json`、`old-artifacts-after.json` |
| 源码完整性 | PASS，执行器在构建前后均断言 Git 状态为空 | 开发 worktree 的 `.local-validation/glx-security/validate-clean-build.ps1` 与最终 `summary.json` |

空 Git 输出通过 PowerShell 管道写文件时未创建独立的 `initial-status.txt` 和 `tracked-changes.txt`，因此不引用这两个文件作为证据。源码状态检查由实际执行器的非空即失败断言完成，完整流程汇总为 PASS；没有事后补造构建前状态记录。

完整产物哈希见 `artifacts.json`。其中 `vcxsrv.exe` 为 3,042,304 字节，SHA-256：`82F8CCBA822A7786B997BD1EC7A7F9B1A9443A04E2A8322426C5674DAF49B128`。保留的旧运行目录为主仓库的 `dist\x64\Release` 和 `D:\File\Program\GitHub\vcxsrv-baseline-20260909-121720\dist\x64\Release`。

核心命令如下。工作目录为上面的固定源码新检出；测试前实际执行器加载了本机 `vcvars64.bat`，使 `cl.exe` 和 ASAN 运行库可用。复跑运行验证时使用新的证据目录。

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./buildall.ps1 -Stage All -Configuration Release -Architecture x64 -Jobs 8 -EnvironmentReport .local-validation/environment.json
$buildTools = Get-Content .local-validation/environment.json -Raw | ConvertFrom-Json
$testedCommit = '5f6c9a930af94355d4c5faca994c78b34b0137e0'
$env:VCXSRV_TEST_LOCAL_TOOLS = '1'
$env:VCXSRV_TEST_RUNTIME = '1'
$env:VCXSRV_RUNTIME_DIR = (Resolve-Path dist/x64/Release).Path
$env:VCXSRV_DUMPBIN = $buildTools.tools.dumpbin.path
$env:VCXSRV_SOURCE_COMMIT = $testedCommit
& $buildTools.tools.python.path -B -m unittest discover -s tools/tests -v
& $buildTools.tools.python.path -B tools/verify_runtime.py --runtime dist/x64/Release --dumpbin $buildTools.tools.dumpbin.path --source-commit $testedCommit --output .local-validation/runtime-new --display 97 --timeout 30
```

本次构建使用 Windows PowerShell 5.1、VS2022/MSVC 和现有原生工具，不下载或安装依赖。与旧基线相同，libxml2 仍使用仓库携带的预编译库，不能把完整构建称为所有第三方依赖均从源码重建。

## 实际应用验收与下一步

真实 Linux OpenGL 应用、键盘和窗口操作、GLX 客户端断开清理均为 **NOT_RUN**：尚未取得具体应用、版本与连接环境。当前单元测试使用外围 vendor 替身，不能把普通 tag 释放等同于真实客户端断开，也不能替代完整桌面回归。实际应用场景验收前，不将这项组件维护标记为全部完成。

维护者使用新程序目录，以原有连接方式复测此前通过的 GUI 应用；补测实际 OpenGL 应用的启动、切换、关闭和重新连接，同时检查窗口操作与键盘。记录应用及 Linux 版本、连接方式、操作结果和日志。确认这些必需场景后，再整合到 `master` 并决定新的基线标签。当前不移动旧标签、不覆盖旧运行目录、不推送远程。
