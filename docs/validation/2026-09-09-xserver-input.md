# X Server 输入处理候选记录

日期：2026-09-09。状态：**开发草稿，错误处理审查未闭合，未完成完整构建，未合入 master**。

## 已做的工作

从 master `dd555fe9febd00dc2880553a55e82a27dace284f` 创建 `codex/update-xserver-input`，补回两个请求长度转换前检查和输入缓冲区共享条件。测试提交 `1c50e7686`；普通合并提交 `8a970b1c9`；固定候选源码和来源清单提交 `75c0c8ea7`。

本批来源是公开 X.Org 补丁，按 `xorg-server/` 映射导入依赖快照；保留原作者信息与许可证，无其他组件变化。

| 事项 | 官方 master 提交 | 官方稳定分支提交 | 本地 upstream 提交 |
| --- | --- | --- | --- |
| CVE-2025-49176 第一条长度路径及 Dispatch 返回值处理 | `03731b326a80b582e48d939fe62cb1e2b10400d9` | `f7dcf2d0d46d31735208c3270dc3457ea3093635` | `43ca24d52d5299387b6f600922a3dc93c355363c` |
| 49176 补充长度路径 | `4fc4d76b2c7aaed61ed2653f997783a3714c4fe1` | `a659519ffa3eae4c94218b03e704a2b6d26adf6f` | `71005c564bbd15f6abab469c048b8fa7f01971cc` |
| CVE-2025-49178 缓冲区共享条件 | `d55c54cecb5e83eaa2d56bed5cc4461f9ba318c2` | `7996ac60d81d665a87f4f736bcfe17e22a375b5c` | `7f89508366689e38246b8aec8926fef51b09b083` |

正式源码包、摘要与核对边界见 [适用性报告](2026-09-09-xserver-applicability.md)。逐文件补丁由 `https://api.github.com/repos/LizardByte-infrastructure/xserver/commits/<完整SHA>` 取得，返回 SHA、补丁内容与正式 21.1.24 ChangeLog 和源码交叉核对。候选的 `DEPENDENCIES.json` 保存来源、补丁 SHA-256、映射与全部根目录对象。

upstream 从 `9971201a6` 正常前移到 `7f8950836`，master 尚未整合它。主线 `DEPENDENCIES.json` 仍固定已整合的 `9971201a6`，候选清单固定新的快照；二者不同是待整合状态，不是遗漏更新。合并未使用 ours/空合并；唯一冲突在 `dispatch.c` 返回值分支的括号风格，保留本地格式。生产差异限于 `os/io.c` 和 `dix/dispatch.c`，共 12 行增加、5 行删除。

## 已执行验证

使用 MSVC x64 和 AddressSanitizer 直接编译实际 `os/io.c`；内存传输替身，无网络连接。10 项覆盖普通/交换字节序的普通请求、合法 BigRequest、已缓冲/新读入头的超长请求，以及丢弃未完成/完成时的缓冲区状态。

| 检查 | 结果 | 范围 |
| --- | --- | --- |
| 未修改生产源码的回归测试 | 预期失败：10 项中 5 通过、5 失败 | 两条超长路径各含两种字节序，另有未完成丢弃时所有权失败 |
| 原始上游补丁合并后的同一测试 | PASS：10 项通过，0 跳过 | 仅解析器单元场景；不覆盖完整调度器错误响应及后续状态 |
| 独立代码审查 | 未完成 | 代理被平台安全检测中止，没有通过结论；调用方契约是本次静态阅读发现的待核实疑点 |
| x64 Release All 干净构建 | NOT_RUN | 新检出目录已创建，构建未启动 |
| 全部现有测试、运行依赖、认证启动、根窗口查询 | NOT_RUN（本候选） | 不能用此前 XFIXES 的 59 项通过代替 |
| 实际图形使用 | NOT_RUN | 本草稿尚不交付用户验收，不沿用旧版本反馈 |

本机原始记录：主仓库 `.local-validation/xserver-audit-20260909/red.log`、`green.log`、`source-import.json` 和 `patches/`。早期测试框架编译错误只用于接入夹具，不记作生产代码的预期失败证据。

文档和来源校验另有 225 项断言通过，包含 38 个本地链接、175 个旧运行文件 SHA-256 不变、两套清单与其固定 Git 树一致、upstream 仅修改两个目标文件及候选合并关系。原始结果为 `document-verification.json`。这组检查不计为产品功能测试。独立文档核对确认 CVE 计数和分组一致，指出的审查状态措辞已修正；该文档核对不替代被中止的代码审查。

## 未闭合事项

上游两处 `-BadLength` 提前返回发生在 `ReadRequestFromClient` 尾部更新请求缓冲区状态之前，而 `Dispatch` 在判断该错误前仍读取 `client->requestBuffer`。现有 10 项测试只证明解析器返回值和所列局部状态，尚不能证明整个错误响应和后续调度正确；不能凭单元测试通过就放行。

需要先核对这一契约，决定是否在开发分支增加保守的异常连接终止适配或完整的状态处理，再运行相应回归。原始来源快照与本地适配必须继续分开记录。尚未作出的技术选择不能记成已修复结论。

审查代理返回原文：`This content was flagged for possible cybersecurity risk.`。该审查没有成功完成，也没有产生通过报告；该独立代码审查未完成且未重试。后续先完成代码审查检查点，再按 [实施计划](../superpowers/plans/2026-09-09-xserver-input.md) 继续构建与验收。

## 目录与回退边界

- 开发工作区：`D:/File/Program/GitHub/vcxsrv/.worktrees/xserver-input`。
- 为固定源码创建的干净检出：`D:/File/Program/GitHub/vcxsrv-input-20260909-2130`，来源 `75c0c8ea7`。这里只是源码检出，没有新建可验收运行产物。
- master 保持已验收的 GLX/XFIXES 生产代码；旧运行目录没有被构建覆盖。没有新基线标签，也没有远程推送。
