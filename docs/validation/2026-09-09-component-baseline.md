# 依赖快照与开发主线整理

> 2026-09-10 历史说明：本文保留当时的方案、提交号与验证结果。旧分支、标签和工作区登记已清理，源码及运行目录保留为普通目录；旧命令不应直接照搬执行。现行规则见[维护规则](../UPSTREAM.md)，对应关系与恢复材料见[整理记录](../validation/2026-09-10-repository-reorganization.md)。旧依赖快照清单见[历史 JSON](../history/2026-09-09-dependency-snapshot.json)；当前不再维护上游源码分支。

日期：2026-09-09。维护者确认 upstream 保存依赖原始来源集合，master 保存整合开发；不再专门维护原作者 VcXsrv 的整合快照。

## 固定来源与接续方式

| 对象 | 提交或文件树 |
| --- | --- |
| 整理前 master | `a55ce37fd7887bc364ae68313cd51cd996d7bc8d` |
| 整理前 upstream | `e13a9d52d43c447d402932e89fcb3db9e177093b` |
| 本地 released 来源 | `3244d44e08ca6a350b8caad28e47b2fc90bcf59c` |
| 来源文件树 | `6cebd341e7682d5c455f0ad01fbcd050f9d6eb7c` |
| 新 upstream 根 | `9971201a65e6f8ec2d34f9c8d4fbc45479cf9578` |
| 开发基线接续提交 | `86247907bfb70aa0afaea04f3bba424d6ed8eab8` |

来源 released 是项目初始 VcXsrv 提交的祖先。新 upstream 精确复制其文件树，仅压缩历史，不增加开发文档或改动来源内容。开发接续提交保留原 master 的完整树，父提交依次为旧 master 和新依赖根。其作用是登记已经整合的依赖基线，后续采用普通三方合并。

现有 master 提交号、候选分支、归档、标签和远程引用保留。master 有两个精简根，upstream 只有一个；这是保留开发历史的结果，不维护第三条来源主线，也没有重新引入 released 的完整历史。

## 来源边界

本基线是依赖源码的历史导入集合，包含原有布局、裁剪、辅助文件与许可证。未独立验证每个目录与组件官方仓库的逐文件一致性；libxml2、libregex、libwinmain 等缺失于集合的目录继续留在 master，不能声明已经建立了其纯净源码基线。

初始集合和根目录对象见 [DEPENDENCIES.json](../DEPENDENCIES.json)。旧 GLX 修改保留在 master，XFIXES 候选保留在原工作分支；本次不升级组件、不合入候选、不重新构建。

## 核验

准备阶段记录了 175 个运行 EXE/DLL 的 SHA-256。候选提交 `fdc996d306512c5a52c976afdd835fea2c5d3bb4` 已本地快进合入 master，upstream 已从旧值校验更新到新依赖根。

候选阶段与切换后各执行一次核验，均为 `PASS`（各 305 项断言，其中包括逐引用和逐运行文件检查）。结果如下：

| 检查 | 结果 |
| --- | --- |
| 依赖基线树等于固定 released 来源树 | PASS |
| 接续提交两父正确、开发文件树与旧 master 完全相等 | PASS |
| upstream 为开发主线的合并基线，旧 master 仍为祖先 | PASS |
| upstream 仅一个提交；开发主线两个精简根 | PASS |
| 变更限定为 11 个维护文档，程序源码与构建脚本不变 | PASS |
| 清单中 43 个根目录条目、模式、类型与对象与来源匹配 | PASS |
| 修改文档中的 36 个本地链接目标存在，diff 空白检查通过 | PASS |
| 除 master/upstream 外原有引用及全部标签不变 | PASS |
| 175 个运行 EXE/DLL 的 SHA-256 不变 | PASS |
| 在临时 Git 对象中模拟后续依赖更新：普通三方合并仅引入新增文件，保留全部开发文件 | PASS |
| 切换后主工作区干净；本次临时 worktree 与工作分支已清理 | PASS |

独立只读审查核对了分支关系、来源清单、更新规则和文档范围，未发现需要修改的问题。模拟更新仅创建无引用的临时 Git 对象，没有改变实际组件版本。此次不重新编译、不运行程序功能测试；程序不变性的依据是 Git 文件树与运行文件哈希，而非沿用旧测试结果。

本机证据保存在 `.local-validation/component-baseline-20260909/`：`before.json` 为原引用和运行哈希，`candidate.json` 为新根及接续提交，`candidate-verification.json` 与 `integrated-verification.json` 为检查结果，`verify.py` 为核验脚本。最终验收文档提交后再运行同一脚本更新 integrated 结果；临时 worktree 清理后少一项工作区检查，不影响其他断言。
