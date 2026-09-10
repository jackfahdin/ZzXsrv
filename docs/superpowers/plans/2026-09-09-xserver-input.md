# X Server 请求读取修复实施计划

> 2026-09-10 历史说明：本文保留当时的方案、提交号与验证结果。旧分支、标签和工作区登记已清理，源码及运行目录保留为普通目录；旧命令不应直接照搬执行。现行规则见[维护规则](../../UPSTREAM.md)，对应关系与恢复材料见[整理记录](../../validation/2026-09-10-repository-reorganization.md)。旧依赖快照清单见[历史 JSON](../../history/2026-09-09-dependency-snapshot.json)；当前不再维护上游源码分支。

> 面向执行者：使用 executing-plans 逐项执行，以实际命令结果更新状态。

**目标：** 回补 CVE-2025-49176（含补充修复）与 CVE-2025-49178，保留 Windows 适配，并生成独立可验收候选。

**架构：** 将三笔公开 X.Org 补丁映射至依赖快照的 `xorg-server/`，再普通三方合并到 `codex/update-xserver-input`。原始补丁与本地测试、清单和文档分开提交。其他扩展只做适用性盘点，不混入本批代码。

**技术栈：** C、MSVC x64、AddressSanitizer、Python unittest、PowerShell 原生构建。

**依据：** X.Org 21.1.24 正式源码包及 ChangeLog；本次适用性报告。源码包 SHA-256 为 `1a4eb36ca65cc3b1b936566d677a9786e13c11cd5806e951ac55f3f5ce3984af`。

## 边界和文件

- 上游源码：`xorg-server/os/io.c` 两个长度转换前检查和缓冲区共享条件；`xorg-server/dix/dispatch.c` 对读取返回值的分类。
- 回归测试：`tools/tests/native/xserver_input.c` 直接编译实际 `os/io.c`，使用内存传输替身；`tools/tests/test_xserver_input.py` 调用原生测试。
- 来源与状态：`docs/DEPENDENCIES.json`、`docs/PLAN_STATUS.md`、`docs/UPSTREAM.md`、`docs/validation/`。
- 初始 master 为 `dd555fe9febd00dc2880553a55e82a27dace284f`，初始 upstream 为 `9971201a65e6f8ec2d34f9c8d4fbc45479cf9578`。不覆盖旧运行目录，不推送远程。

## 当前检查点

本轮已在 `c06e0db1669afaee649bdaf407c7c76c9fa3ae56` 完成本地终止适配：两条不可表示的长度均先执行 `YieldControlDeath()` 再返回 `-1`，调用方恢复为主线原有代码。原始上游来源保持不变。12 项测试在适配前 4 项预期失败、适配后全部通过；新适配的限定范围静态审查无阻断问题。在新的 `vcxsrv-input-20260909-2110` 目录完成全量构建、71 项测试（0 跳过）和运行验证，175 个旧产物不变，目前待新版本实际使用确认，之前 XFIXES 的使用确认仍只适用于旧版本。

初版 `75c0c8ea7` 的审查中止与未构建状态是历史检查点，保留在验证报告。不得把新适配的静态审查描述为补做了旧动态调查，也不得将当前候选的自动验证等同于实际图形使用确认。

## 执行步骤

- [x] 从正式源码包核对修复，并固定原始 master 提交 `03731b326a80b582e48d939fe62cb1e2b10400d9`、`4fc4d76b2c7aaed61ed2653f997783a3714c4fe1`、`d55c54cecb5e83eaa2d56bed5cc4461f9ba318c2`。通过同 SHA 镜像取得逐文件补丁，交叉检查正式包代码和 ChangeLog。
- [x] 先运行未修改源码的原生测试，确认正常请求通过、两条超长请求路径和未完成丢弃缓冲区测试失败。测试不连接网络。
- [x] 将三笔原始补丁顺序应用到 upstream 的独立子提交；更新引用时检查旧值。普通合并至候选，逐项保留 Windows 改动，更新来源清单。
- [x] 原生回归全部通过；记录未修改源码的失败与修复后通过证据。
- [x] 固定源码提交，在新的独立目录完成 x64 Release All 构建，启用全部本机与运行测试，要求无跳过；验证依赖、认证启动、根窗口查询和子进程清理。
- [x] 完成新适配与最终差异的限定范围独立静态审查；原始来源和本地适配分开。
- [x] 核对完整构建后的旧运行文件哈希和产物清单；同步最终文档。
- [ ] 取得本候选实际图形使用确认后合入 master；若尚未确认，交付明确路径和验证结果，保留“候选待验收”，不沿用旧 GLX/XFIXES 反馈。

## 回归场景

分别测试正常/交换字节序的普通请求、合法 BigRequest、长度超过有符号字节计数范围的已缓冲头、通过内存传输新读入的头，以及还有 ignoreBytes 时保留缓冲区所有权、丢弃完成后恢复共享。测试直接执行生产解析器并在 MSVC AddressSanitizer 下运行。
