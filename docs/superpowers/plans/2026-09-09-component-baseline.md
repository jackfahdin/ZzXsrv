# 依赖基线整理执行记录

> 2026-09-10 历史说明：本文保留当时的方案、提交号与验证结果。旧分支、标签和工作区登记已清理，源码及运行目录保留为普通目录；旧命令不应直接照搬执行。现行规则见[维护规则](../../UPSTREAM.md)，对应关系与恢复材料见[整理记录](../../validation/2026-09-10-repository-reorganization.md)。旧依赖快照清单见[历史 JSON](../../history/2026-09-09-dependency-snapshot.json)；当前不再维护上游源码分支。

用户已在当前会话确认两层方案并授权开始整理；范围是现有分支与维护文档，不是组件升级。

## 目标与设计

upstream 保存依赖来源集合，master 保留继承的整合适配和后续开发。用本地已整合的 released 文件树建立一个独立精简根，再建立保留原 master 文件树的基线合并；不重写已有提交，不导入组件旧历史。原作者 VcXsrv 仅作为初始来源，不设持续快照分支。

## 步骤与验收

- [x] 固定原 master、upstream、其他引用及运行文件哈希到本地 before.json；确认 released 是初始来源的祖先。
- [x] 用 git commit-tree 导入 released 完整树，再以原 master 和新根为父构造相同开发树的基线接续提交；在 codex/component-baseline 隔离工作区整理。
- [x] 修正 README.md、FORK.md、docs/UPSTREAM.md、docs/MAINTENANCE.md，标注第一次整理文档为历史记录；增加 docs/DEPENDENCIES.json 固定基线和根目录对象。
- [x] 核对新依赖树与来源完全相等、基线合并树与旧 master 完全相等、开发差异只有维护文档；检查清单、链接、Git 合并行为及引用保护，完成独立审查。
- [x] 本地快进 master，以旧值校验更新 upstream；复核最终关系、工作区、其他引用与运行文件哈希，并记录到 docs/validation/2026-09-09-component-baseline.md。完成后移除本次临时 worktree 和工作分支。

不执行远程 fetch/push，不安装工具，不修改组件版本，不合入其他候选。验证使用 Git 对象与文件不变性，不把本次整理称为程序构建或功能验收。
