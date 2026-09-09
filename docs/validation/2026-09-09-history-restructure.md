# 本地历史重组记录

日期：2026-09-09。维护者已确认旧历史归档、upstream 原作者快照和 master 开发的结构。本次迁移只改变 Git 提交关系与维护文档，没有升级组件或修改程序源码。

## 来源与归档

- 原作者仓库：`https://github.com/marchaesen/vcxsrv`。
- 原作者来源：`d0a1eaf7ee15fcdf4f683388a88fec49078e6408`，原提交日期 2025-10-20。
- 重组前本地 master：`db1d2b2659ffa576b43693790dfe759fdce4a6bf`。
- 新的无父导入提交：`e13a9d52d43c447d402932e89fcb3db9e177093b`。
- 归档目录：`D:\File\Program\GitHub\vcxsrv-history-archive-20260909-141737`。
- Git bundle：上述目录的 `vcxsrv-before-restructure.bundle`。
- bundle SHA-256：`8a2eda174a63d76248bb68ea3e708eab7d661490cfbf14aed1b4ee0836953d66`。
- 恢复镜像：上述目录的 `restored.git`。
- 归档引用清单：`refs-before.txt`；新旧提交与 tree 清单：`migration.json`。
- 执行日志：`D:\File\Program\GitHub\vcxsrv\.local-validation\history-restructure\operations.log`。

归档命令为 `git bundle create <bundle> --all`。`git bundle verify` 成功后，从这个本地 bundle 执行 `git clone --mirror <bundle> <restore-path>`。恢复镜像的 106 个 `git show-ref` 条目与归档前集合完全一致，`git fsck --connectivity-only` 退出 0。bundle 和恢复镜像均保留；同一硬盘上的副本不代替异地备份。

归档包含当时 Git 引用可达的已提交对象，不包含 ignored 构建产物、工作树原始日志或 Git 用户配置；这些材料继续保留在原路径。没有执行远程 fetch、pull、push 或依赖下载。

## 提交对应关系

| 内容 | 旧提交 | 新提交 |
| --- | --- | --- |
| 原作者源码快照 | `d0a1eaf7ee15fcdf4f683388a88fec49078e6408` | `e13a9d52d43c447d402932e89fcb3db9e177093b` |
| 原生 Windows 构建及运行目录 | `bc77b1521aaf5ccf199d1cdb58a6ac0746dc8d5d` | `a648da25db4fe479970a9d84d1deea51ae9268fc` |
| 维护路线与基线计划 | `2179eddd7d1d06fdd9735a14311aff75207af2c8` | `42d10e37d606a5cbea624d7f28e4c7fbd07635a9` |
| 本地维护与提交约定 | `3fc1d97776b88be421483726e3d09570c6dcb903` | `5884f6150423d5009ca480ed4c5d2a75bd01ab77` |
| 环境报告 | `5d2aa36fd60f5dcb62670ee762f32070a964b457` | `21f21ab2f241c01b5adcb4bcd58c5f3f1e1edb47` |
| 运行验证 | `a4adc3dc3f2158c2308133cecee19a71cf62bcc8` | `f6c98c39e4f18183d5886d427377f12e13727230` |
| 基线结果文档 | `db1d2b2659ffa576b43693790dfe759fdce4a6bf` | `acf73afca2a389f63738508c3717b7eff8c4657e` |

每行新旧提交的 `^{tree}` 均相同，包含 Git 跟踪的路径、内容和文件模式。六个维护提交保留原作者姓名、邮箱和作者日期，使用中文标题/正文，并加入旧 SHA。新提交的提交者时间为迁移时间。

迁移文档加入之前，新主线共七个提交、一个根。`upstream` 指向第一行的新提交，后续维护文档只提交到开发分支。历史主线通过 `git log master` 查看；`git log --all` 仍能看到旧标签、历史分支和远程引用可达的旧历史。没有清理旧对象，因此不宣称 Git 数据目录已缩小。

## 验证边界

旧基线标签 `local-baseline-20260909-a4adc3dc` 保持指向 `a4adc3dc3f2158c2308133cecee19a71cf62bcc8`，此前的 [完整编译及 43 项测试报告](2026-09-09-baseline.md) 仍有效地描述那次旧源码构建。迁移得到的 f6c98c39 与其 tree 相等，但本次没有重新编译，不能改写报告中的二进制来源。

本次针对新提交执行 `buildall.ps1 -CheckOnly -EnvironmentReport ...`，确认实际工具可用、报告来源属于新提交；它不生成程序。报告保存在原工作区 `.local-validation/history-restructure/environment-new-history.json`。最终交付只增加或修改维护文档，程序源码与旧 master 一致。

实际 CheckOnly 的 `source_commit` 为 `acf73afca2a389f63738508c3717b7eff8c4657e`，命令退出 0。新增维护文档共 21 个本地 Markdown 链接检查通过，Git 差异格式检查通过。独立审查核对了 tree、作者元数据、归档引用、bundle SHA-256 和对象连接；两处关于二进制来源范围及合并祖先的文档问题修正后，定向复查通过。

原运行目录 `D:\File\Program\GitHub\vcxsrv\dist\x64\Release` 和此前新构建目录 `D:\File\Program\GitHub\vcxsrv-baseline-20260909-121720\dist\x64\Release` 均保留。历史 worktree 不清理，不覆盖认证测试及构建记录。

## 主目录切换与后续恢复

主目录继续使用 `master`。旧 HEAD 保存在 `archive/pre-restructure-20260909`，切换前先确认主目录状态干净且其 HEAD 未被其他操作改变。新 master 取消旧 `origin/master` 的跟踪关联，原 GitCode 远程地址保持不变。后续远程仓库由维护者另行安排。

主目录已成功切换到维护文档提交 `38e804e2d90a3bc5c9fba0dad31e7c5d35cea0be`，随后追加本核验记录。切换后状态干净，upstream 只有一个根提交，新 master 的唯一根与之相同，旧 master 归档指向正确，全部旧标签未移动。切换前后两个运行目录共 70 个 EXE/DLL 的大小和 SHA-256 全部相同，检查退出 0。机器记录保存在 `.local-validation/history-restructure/integration.log` 和 `runtime-before-switch.json`。

需要恢复旧源码时，可在新的独立 worktree 检出 `archive/pre-restructure-20260909`。也可以从保存的 bundle 克隆到一个尚不存在的新目录；不需要覆盖当前主目录或强制重置当前工作。本文和其他新增维护文档不在重组前 bundle 中，属于新的开发历史。

上游快照同步、直接组件修复、优先级和验收门槛见 [上游更新规则](../UPSTREAM.md)。本次只建立规则，没有启动自动更新或引入新组件版本。
