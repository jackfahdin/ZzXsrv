# 本地历史重组实现计划

> 2026-09-10 历史说明：本文保留当时的方案、提交号与验证结果。旧分支、标签和工作区登记已清理，源码及运行目录保留为普通目录；旧命令不应直接照搬执行。现行规则见[维护规则](../../UPSTREAM.md)，对应关系与恢复材料见[整理记录](../../validation/2026-09-10-repository-reorganization.md)。旧依赖快照清单见[历史 JSON](../../history/2026-09-09-dependency-snapshot.json)；当前不再维护上游源码分支。

> **面向 AI 代理的工作者：** 使用顺序执行与独立审查推进；用户已确认本地历史重组方案，无需重复询问已授权的分支操作。

**目标：** 历史归档可恢复，日常开发历史由一个来源导入提交及我们的维护提交组成。

**架构：** upstream 保存原作者快照，master 保存本地改动。使用 commit-tree 保持 Git 文件树，旧引用与证据保留。

**技术栈：** 本地 Git、PowerShell、Python 3.14。

**规格：** [历史重组设计](../specs/2026-09-09-history-restructure-design.md)。

## 约束

仅本地操作；不下载、不升级组件、不改程序功能；提交采用中文简短标题和中文详细正文。原运行目录、历史标签和证据 worktree 保留。

## 执行与验证

- [x] 确认来源 d0a1eaf7e、本地旧 HEAD db1d2b265、六个本地提交和干净状态。
- [x] `git bundle create <独立归档路径> --all` 后 `git bundle verify`；从 bundle `git clone --mirror` 恢复，核对 106 个 show-ref 条目并执行 `git fsck --connectivity-only`。
- [x] 从来源 tree 执行无父 `git commit-tree`；以六个原 tree 顺序连接新父提交，保留作者信息并记录新旧 SHA。逐项 tree 相等，计数七个且只有一个根。
- [x] 建立 upstream 和 codex/history-restructure，在独立 worktree 编写来源说明、规则、组件清单、迁移记录、规格与计划，并更新 README 和维护路线。
- [x] 独立审查；检查 Markdown 本地链接、路径及 `git diff --check`。排除新增维护文档后，与旧 HEAD 的源码必须无差异。
- [x] 新历史下执行 Windows PowerShell CheckOnly，报告 source_commit 必须等于运行该脚本的 HEAD；不得把它当成实际编译证据。
- [x] 中文提交文档；将旧 master 保存为 archive/pre-restructure-20260909，主目录切换到新 master，取消旧 origin/master 跟踪关系，不更改远程地址。
- [x] 核对最终分支关系、工作区清洁、标签指向和运行程序存在，记录完成证据。

详细命令和机器结果保存在原工作区 `.local-validation/history-restructure`，bundle 与恢复镜像在仓库外的独立归档目录。与最初草案相比，验证收敛为 tree 等同性和 CheckOnly 来源验证：没有程序代码变化，不为纯历史/文档改动重复运行整套构建与桌面测试。
