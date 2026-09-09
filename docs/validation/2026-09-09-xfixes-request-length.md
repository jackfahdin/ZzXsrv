# XFIXES 断开模式请求长度修复验证

日期：2026-09-09。开发基线为已验收的 `a55ce37fd`，分支为 `codex/update-xfixes-security`。本轮只回补 CVE-2025-49177，不升级其他组件。

## 当前整合状态与历史分支检查

代码提交 `1e4a1cf5149df2b5da48d2571b08f2bc597a538b` 仍为独立候选。本文记录该候选的已完成验证，进入 master 仅用于统一证据入口，不代表候选修复已合入或已获人工验收。

原会话于 2026-09-09 17:51:39（UTC+08:00）核对原作者分支，当时没有新整合快照。这个检查只说明当时的来源状态，之后不作为移动 upstream 的依据。

现行 upstream 是依赖来源集合 `9971201a65e6f8ec2d34f9c8d4fbc45479cf9578`，master 保存继承的适配和本地开发，见 [现行规则](../UPSTREAM.md)。本候选属于分支职责调整前已经完成的修复，按规则保留原提交；后续源码快照包含等价修复时再核对重复改动。本次不另行升级依赖，不推送远程。

## 来源与适用性

- [X.Org 安全索引](https://www.x.org/Development/Security/) 将 CVE-2025-49177 列为 XFIXES 6 的 SetClientDisconnectMode 数据泄漏。
- 上游修复：[`ab02fb96b1c701c3bb47617d965522c34befa6af`](https://gitlab.freedesktop.org/xorg/xserver/-/commit/ab02fb96b1c701c3bb47617d965522c34befa6af)，作者 Olivier Fourdan，2025-04-28，父提交 `03731b326a80b582e48d939fe62cb1e2b10400d9`。
- 官方 GitLab 补丁端点返回反自动化页面，实际差异通过 [同 SHA 镜像](https://github.com/LizardByte-infrastructure/xserver/commit/ab02fb96b1c701c3bb47617d965522c34befa6af) 取得；没有将 HTML 当作补丁。原文作者和许可证保留。
- 本地 XFIXES 分发包含版本 6 的 Set/Get 处理函数；普通 Set 在读取 mode 前不检查长度，换字节序 Set 仅检查最小长度。
- 回补添加普通请求的精确长度检查，并把换字节序请求的最小长度检查改为精确匹配。生产差异严格为上游的 +2/-1；整个 `xorg-server/xfixes/disconnect.c` Git blob 为 `5b2945a4a8236c4b80a3c174cfbd9089f1c3f462`，与上游修复后的文件一致。

来源、原生测试及协议脚本证据保存在开发工作区 `D:\File\Program\GitHub\vcxsrv\.worktrees\xfixes-security\.local-validation\xfixes-security`，包括 `upstream.json`、`upstream.diff`、`vcxsrv-upstream.json`、`run-tests.ps1` 和 `check-wire.py`。

## 回归验证

新增原生 C 测试直接编译实际 `disconnect.c`，使用真实协议结构、长度宏和私有字段访问函数。仅私有存储注册、回复输出及分发指针初始化由夹具提供；编译开启 MSVC AddressSanitizer。测试驱动为 `tools/tests/test_xfixes_disconnect.py`。

| 检查 | 旧代码 | 修复后 | 证据 |
| --- | --- | --- | --- |
| 普通和换字节序正常 Set/Get | 2 项通过 | 2 项通过 | `red-tests.log`、`green-tests.log` |
| 普通/换字节序短长请求拒绝，模式与缓冲区不变 | 3 项失败、1 项通过 | 4 项通过 | 同上 |
| 精确 4 字节短请求读取边界 | 普通路径触发 ASAN 越界读取；换字节序路径原已拒绝 | 2 项通过 | 同上 |
| 汇总 | 8 项执行，4 失败 | 8 项全部通过，0 跳过 | 同上 |

原生测试的 `client.req_len` 模拟传输层已解码的长度，覆盖处理函数层；实际传输与认证另行验证。独立审查核对了生产差异、真实宏、私有存储、字节序及红绿证据，没有 Critical、Important 或 Minor 问题。

## 实际协议验证

脚本使用现有程序独立启动显示号 98，临时 MIT-MAGIC-COOKIE-1 认证，最小 PATH，仅管理自身创建的服务器进程。先 QueryExtension 并协商 XFIXES 6，再验证正常 Set/Get，发送短/长 Set 并 Get，检查 `BadLength`、序号、扩展操作码以及模式未变化。

默认服务器拒绝换字节序客户端；首次 `wire-red` 因这个前置条件而没有完成四种请求，保留为初次记录。最终脚本只对临时实例设置 `+byteswappedclients`，不更改产品默认值、访问控制或用户现有实例。

| 字节序与长度 | 旧 GLX 候选结果 | 新 XFIXES 候选结果 |
| --- | --- | --- |
| 小端短请求（1 个四字节单位） | FAIL，未返回 BadLength，Get 读回非零模式 | PASS，BadLength，模式不变 |
| 小端长请求（3 个四字节单位） | FAIL，未拒绝并改变模式 | PASS，BadLength，模式不变 |
| 大端短请求 | PASS，原有最小长度检查已拒绝 | PASS，BadLength，模式不变 |
| 大端长请求 | FAIL，未拒绝并改变模式 | PASS，BadLength，模式不变 |

最终证据分别为 `wire-red-with-swapped/result.json` 和 `wire-green/result.json`，两次清理均成功。新程序与下述固定源码构建相同。

旧程序测试使用 `vcxsrv-glx-20260909-1625/dist/x64/Release` 中的可执行文件启动自有实例，没有触碰维护者正在使用的连接。短 Set 与后续 Get 连续发送，旧普通路径把后续请求字节读作 mode，明确违反当前请求的边界。此处 FAIL 是预期的漏洞回归红灯，不是之前常用 GUI 无法使用的证据。

协议脚本的独立审查通过，覆盖了认证报文、版本协商、字节序、错误包与清理。该脚本以正常 mode 为 0 验证往返，非零模式的字节序由原生测试覆盖；没有声称测试实际 reset/terminate 行为。

## 新候选构建

固定源码为 `1e4a1cf5149df2b5da48d2571b08f2bc597a538b`。干净检出目录为 `D:\File\Program\GitHub\vcxsrv-xfixes-20260909-1800`，构建证据位于其 `.local-validation/xfixes-build-20260909-175722`。

构建开始于 17:57:23（UTC+08:00），18:08:46 编译结束，18:09:23 全流程完成，结果 **PASS**。使用现有 Windows PowerShell、VS2022/MSVC 和本机工具执行 `buildall.ps1 -Stage All -Configuration Release -Architecture x64 -Jobs 8`，OpenSSL 沿用已修正的 `/J1`。

| 验证 | 实际结果 | 干净检出中的证据 |
| --- | --- | --- |
| x64 Release All 构建 | PASS，退出 0 | `environment.json`、`build.log`、`summary.json` |
| 全部脚本、ASAN 与运行集成测试 | PASS，59 项，0 失败、0 跳过，32.706 秒 | `tests.log` |
| PE 架构、直接与延迟导入 | PASS，35 个 EXE/DLL | `runtime/dependencies.json` |
| 版本、临时认证、根窗口查询、清理 | PASS，显示号 97 | `runtime/result.json` 及各子进程日志 |
| 源码状态 | PASS，构建前 Git 状态与构建后受跟踪文件差异为空 | `initial-status.txt`、`tracked-changes.txt` 及执行器断言 |
| 旧程序保护 | PASS，三个目录共 105 个 EXE/DLL 大小与哈希不变 | `old-artifacts-before.json`、`old-artifacts-after.json` |

构建执行器保存在开发工作区的 `.local-validation/xfixes-security/validate-clean-build.ps1`；该次测试显式启用了 `VCXSRV_TEST_LOCAL_TOOLS=1` 和 `VCXSRV_TEST_RUNTIME=1`，运行目录指向新候选，来源字段为完整固定源码 SHA。

新运行目录：`D:\File\Program\GitHub\vcxsrv-xfixes-20260909-1800\dist\x64\Release`。`vcxsrv.exe` 为 3,041,792 字节，SHA-256 为 `E9A4D3A94031663B906BFD255193A2A050B841D19A1799C729B420317F659CD1`，全部产物清单见 `artifacts.json`。开发分支后续只追加文档，不改变二进制来源。

本轮保留主工作目录、旧基线和已验收 GLX 候选三个运行目录，构建执行器检查共 105 个 EXE/DLL 的大小与 SHA-256。libxml2 仍为仓库携带的预编译依赖，不把 All 构建等同于所有第三方库均从源码重建。

新候选需要维护者实际使用确认后再合入 `master`，不能借用上一个 GLX 候选的“能用”反馈。真实 Linux GUI、OpenGL、窗口和键盘具体场景本轮未执行。
