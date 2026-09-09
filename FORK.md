# 项目来源与本地维护

本项目从 [marchaesen/vcxsrv](https://github.com/marchaesen/vcxsrv) 派生，原作者已整合 X.Org、Mesa 等组件并完成 Windows / Visual Studio 适配。我们在此基础上维护原生 Windows 构建、运行验证和实际使用问题。

## 首次导入

- 来源分支：原作者 `master`。
- 来源提交：`d0a1eaf7ee15fcdf4f683388a88fec49078e6408`，原提交日期 2025-10-20。
- 导入日期：2026-09-09。
- 本地导入提交：`e13a9d52d43c447d402932e89fcb3db9e177093b`。
- 产品文件版本：21.1.16.1；导入快照包含该发布标签之后的上游提交，不能将它等同于标签快照。

导入提交没有父提交，其 Git 文件树与来源提交完全一致。压缩 Git 历史不改变源码归属，原版权、许可证和第三方材料均保留。项目原有许可证入口为 [COPYING](COPYING)，组件目录中的许可材料同样保留。

## 分支职责

| 分支或标签 | 职责 |
| --- | --- |
| `upstream` | 原作者 VcXsrv 源码快照；后续导入提交连接在这个分支上，不加入我们的功能修改 |
| `master` | 我们的开发主线；从 `upstream` 派生，包含原生构建、修复、验证与维护文档 |
| `codex/*` | 独立实现或更新工作分支；验证后整合到 `master` |
| `archive/pre-restructure-20260909` | 重组前的本地 `master`，保留完整旧历史以便定位和回退 |
| 原有版本标签与旧基线标签 | 历史证据，保留原指向，不改名成新历史的测试结果 |

原作者的 `released` 保存各组件原始源码，与我们的 `upstream` 含义不同。历史远程引用 `origin/released` 仅供追溯；当前 `origin` 仍是原 GitCode 镜像，不能把它当成我们可推送的开发仓库。

## 历史与验证

重组前完整历史已归档，并从 Git bundle 恢复为本地镜像核对。归档位置、摘要及六个本地提交的新旧对应关系见 [历史重组记录](docs/validation/2026-09-09-history-restructure.md)。

已验证基线目录 `D:\File\Program\GitHub\vcxsrv-baseline-20260909-121720\dist\x64\Release` 的二进制来自旧提交 `a4adc3dc3f2158c2308133cecee19a71cf62bcc8`，对应新历史中内容完全相同的 `f6c98c39e4f18183d5886d427377f12e13727230`。后者没有重新编译，原验证报告保留旧提交号。主目录中更早的 `dist\x64\Release` 未覆盖，不能将其来源归为该基线。首次从新历史构建时必须产生新的环境报告和验证记录。

维护流程见 [上游更新规则](docs/UPSTREAM.md)，阶段目标见 [维护路线](docs/MAINTENANCE.md)。提交使用中文简短标题，空一行后以中文说明内容、原因和验证结果。
