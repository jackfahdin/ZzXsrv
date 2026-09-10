# ZzXsrv 仓库整理记录

> 目录迁移说明（2026-09-10）：文档链接已更新，正文中的旧命令与文件路径仍表示当时状态；当前入口见[文档导航](../README.md)。

日期：2026-09-10。本次范围是迁移到维护者提供的 GitHub 空仓库、整理线性主线和依赖来源文档。组件版本、程序源码及候选验收范围保持原状。

## 仓库与历史

- 新仓库：[jackfahdin/ZzXsrv](https://github.com/jackfahdin/ZzXsrv)，origin 为 `git@github.com:jackfahdin/ZzXsrv.git`。首次检查 `ls-remote` 成功且无引用；只推送 master，不推送旧标签或镜像全部 refs。原 GitCode 远程内容未修改。
- 整理前 master：`a296b1553668878b21857f19fa3a0c2c8615d4a7`；线性化后的对应提交：`b8be16d052c1665a0f5fe7c497d5b1a5e783c3ca`。两者文件树均为 `35dfec0f3c75b2112e11b957b252fdc705087972`。
- 保留原 master 第一父链的 23 个步骤，每一步新旧 Git tree 完全一致；前 18 个提交无需重建，最后 5 个因父关系变化重新编号。合并侧支的最终文件内容包含于相应步骤中，不承诺保留每个侧支提交的独立身份。随后增加本次文档提交。
- master 只有一个根，零 merge commit。清理 109 个旧本地分支、旧远程跟踪和标签引用；只留下 master。Codex 管理的树对象引用不是开发分支，保留这些应用内部引用。首次推送会新增 origin/master 跟踪引用，它指向同一条主线。
- 不再维护 upstream、released 或原作者整合源码快照分支。已设置本机 `pull.ff=only`、`merge.ff=only`、`fetch.prune=true`；后续维护以[规则](../maintenance/UPSTREAM.md)为准。

完整 23 步映射见[线性提交映射 JSON](../history/2026-09-10-linear-commit-mapping.json)。发生重编号的提交如下：

| 原提交 | 线性提交 |
| --- | --- |
| `2fa811ae2db5f066a362743171ffbdab6a71771d` | `6446747e3e8b6521599399ba14df81cdc8046687` |
| `a770cb3ff34efa043face0d56c31928b73683d3a` | `5a909fc5bbc5a37417b8b5eb264f028bffb67bc3` |
| `dd555fe9febd00dc2880553a55e82a27dace284f` | `6c1f87f4407e22b11625c2935c1279ad0f02f9c8` |
| `9c472a0334215de000d5cda7ed87dc1f058388d3` | `1e10cb858f8060bb1da2f72a8d530d46a9475bf1` |
| `a296b1553668878b21857f19fa3a0c2c8615d4a7` | `b8be16d052c1665a0f5fe7c497d5b1a5e783c3ca` |

## 工作目录与恢复材料

整理前 12 个登记工作区均无未提交改动。主仓库继续作为 Git 工作区；其余 11 个目录解除 worktree 登记，保留源码、构建产物和日志。仅移动这些目录的 `.git` 链接文件并清理对应登记，没有删除源码目录。旧目录现在是普通目录；尤其位于主仓库下的旧目录不能再用 `git -C` 当作原候选仓库操作，因为 Git 会向上发现主仓库。

本机恢复材料不纳入新仓库，也不建立归档分支：

| 材料 | 位置及校验 |
| --- | --- |
| 整理前开发 bundle | `.local-validation/reorganize-20260910/current-development.bundle`；SHA-256 `474dbaf20784305e18d138a8b1c35d652303b0be2e90035d41df304d81c7bc86` |
| 既有完整旧历史 bundle | `D:/File/Program/GitHub/vcxsrv-history-archive-20260909-141737/vcxsrv-before-restructure.bundle`；SHA-256 `8a2eda174a63d76248bb68ea3e708eab7d661490cfbf14aed1b4ee0836953d66` |
| 整理前引用、目录与运行哈希 | `.local-validation/reorganize-20260910/before.json` |
| 旧工作区登记 | 同目录 `worktree-registration-backup/`、`worktree-gitlinks/` 及 `preserved-checkouts.json` |
| 输入候选的源码和测试补丁 | 同目录 `pending-input-source.patch`；SHA-256 `ca165f3dc56dd7ac9b37358cbf9ca3f65886426f6961394333031f7448461d1d` |

两个 bundle 均已执行 `git bundle verify` 并复核 SHA-256；删除的用户可见引用在相应 bundle 中有直接引用或祖先可达关系。需要查看旧对象时，在独立恢复目录初始化仓库，从 bundle 获取指定旧引用即可；不要把全部历史引用重新导回日常工作仓库。

输入处理候选固定源码仍为 `c06e0db1669afaee649bdaf407c7c76c9fa3ae56`，原候选末端为 `b971e28afa08f90e8bcc01999aed65d47127e1e7`。它的 71 项自动测试和运行验证属于旧候选记录，实际使用确认仍待完成，未合入本次 master。运行目录继续位于 `D:/File/Program/GitHub/vcxsrv-input-20260909-2110/dist/x64/Release`。恢复开发优先在当前主线的新临时工作区应用上述 source patch；另存的 `pending-input.patch` 含旧维护文档，只作归档，不能整体应用以免恢复旧规则。

## 来源与文档

[依赖来源文档](../dependencies/SOURCES.md)与 schema 2 [JSON 清单](../dependencies/SOURCES.json)按组件记录原始上游、commit/tag/版本证据及实际继承链接。首次继承来自原作者固定提交 `d0a1eaf7ee15fcdf4f683388a88fec49078e6408`；后续 GLX 与 XFIXES 补丁分别记录原提交和实际取得差异的镜像。

共 196 条来源或构建声明，含 40 个字体包；外部工具和可选 wrap 下载声明单独列出。缺失精确提交、版本冲突、混合头文件以及 libxml2 预编译库来源不明等情况保留明确说明。schema 1 的旧快照清单仅存为[历史材料](../history/2026-09-09-dependency-snapshot.json)，不再用于定义当前依赖分支。

README、FORK、维护规则、计划状态和验证入口采用同一现行规则；日期明确的旧报告和计划增加历史说明，原测试数字、来源 SHA 及用户确认不改写。

## 验证

本次验证检查历史与数据不变性，不重复运行产品构建：生产源码、构建脚本及测试文件相对整理前 master 没有差异。新增变更仅为 README、FORK 与 docs。

- 逐项复核 23 对提交的 tree，全部一致；master 单根且无合并节点。
- 210 个既有 EXE/DLL 的 SHA-256 与整理前一致；11 个旧目录保留，主工作区登记唯一。
- `pending-input-source.patch` 在当前主线执行 `git apply --check` 成功，未实际应用。
- 核对 JSON 必要字段、实际继承路径、40 项字体清单覆盖、Markdown 相对链接及 `git diff --check`。
- 独立只读审查未发现阻断项，复核范围为来源证据、文档状态、Git 结构及候选恢复边界。没有执行产品构建或扩大功能范围。
- 普通首次 `git push -u origin master` 已成功；`ls-remote --symref` 确认默认 HEAD 指向 `refs/heads/master`，两者均为线性化提交 `b8be16d052c1665a0f5fe7c497d5b1a5e783c3ca`。本次文档随后作为第 24 个线性提交追加并普通快进推送，最终 HEAD 比对结果保存在本机验证输出。

本机命令结果保存在 `.local-validation/reorganize-20260910/`。本记录描述本次整理的检查项；最终提交号及远程同步结果以 Git 引用和最终验证输出为准。
