# R3 RENDER/RECORD 验证与主线整合

日期：2026-09-10。状态：重启后分阶段恢复构建完成，97 项测试、独立运行验证和审查通过；维护者已针对本组反馈“没问题”，修复已快进合入 master，合入后 97 项测试通过。旧文件比较发现主仓库 dist 的 16 项差异，已保留并记录，未声称所有旧文件均未变化。

## 范围与来源

维护者要求开始 R3 的 RENDER/RECORD 修复。起点为 `1bc06775c03e128168064d931f63667d1bc95598`，当时的候选分支为 `codex/render-record-20260910`（现已删除），工作目录为 `D:/File/Program/GitHub/zzxsrv-render-record-20260910`。保留 GLX、XFIXES 和输入处理修复，GUI-001 按此前要求暂缓排查。

| 修复 | 上游固定提交 | 本地代码提交 | 行为 |
| --- | --- | --- | --- |
| RENDER 动画光标数量 | `0885e0b26225c90534642fe911632ec0779eebee` | `d7af5de4c3b6350ccb0e7e112bf55c501c4a3930` | 在协议入口和公共构造函数中拒绝非正数量，返回 `BadValue` |
| RECORD 注册数量 | `2bde9ca49a8fd9a1e6697d5e7ef837870d66f5d4` | `13f058a646a69f4a8b13a56e56d2bb4fb6980ef7` | 在请求长度乘加运算前限制客户端数量和范围数量，保留后续长度、选择器和范围校验 |

生产改动仅涉及 `src/xorg-server/render/render.c`、`src/xorg-server/render/animcur.c` 和 `src/xorg-server/record/record.c`，共增加 14 行。非空新增行与上游 master 补丁一致，`render.c` 额外保留一行空行；路径适配为当前 `src/xorg-server/`，不替换整包源码，保留继承的 Windows API 和既有字节序处理。

两笔补丁于 2026-09-10 从同 SHA 的 GitHub 镜像 API 下载，原始上游链接、实际下载链接、时间、作者、响应与提取补丁的 SHA-256 见[来源清单](../dependencies/SOURCES.md)和[JSON](../dependencies/SOURCES.json)。作者均为 Olivier Fourdan。GitLab 页面本次未成功读取，不将其写成实际下载来源。

交叉核对使用本地已保存的官方 `xorg-server-21.1.24.tar.xz`，SHA-256 为 `1a4eb36ca65cc3b1b936566d677a9786e13c11cd5806e951ac55f3f5ce3984af`；重新计算归档哈希，核对 ChangeLog 中 master 与 stable 提交映射及最终源码检查逻辑。stable 对应提交分别为 `ea7b770952dbcf6c769db7538b55b4f92e1f95c5`、`8592cab6820f77c209c2ea9a7b94e0d4d1ac848c`。stable 的头文件依赖与 master 不同，新增 `os/osdep.h` 按本次 master 补丁核对。不保留上游源码分支或新增整合快照。

## 回归验证

原生 C 测试直接包含完整生产翻译单元，使用 MSVC x64 AddressSanitizer；编译命令及输出保存在本地证据中。测试使用小型本地缓冲区和资源、定时器、私有数据服务替身，不连接服务器。完整生产分发表带入的无关外部服务通过明确的 x64 链接别名指向立即终止函数，不能将其视为已验证功能。

| 检查 | 当前结果 |
| --- | --- |
| RENDER 最初 10 项测试，未修复源码 | 7 通过、3 项预期失败：空协议请求、公共函数零数量和负数量；负数量由 ASan 报告堆越界 |
| RENDER 同样 10 项测试，修复后 | 10 通过、0 跳过 |
| RECORD 13 项测试，未修复源码 | 10 通过、3 项预期失败：客户端上限、范围上限和二者联合边界 |
| RECORD 同样 13 项测试，修复后 | 13 通过、0 跳过 |
| 审查后补充 RENDER 交换字节序空请求 | 通过；本组最终 24 项专项测试通过 |
| 独立代码审查 | 无 Critical/Important；已补充所建议的交换字节序空请求用例，复审无问题 |
| 基础依赖构建 | PASS，退出码 0，14:56:06–15:05:51（UTC+08:00） |
| 首次 All 构建 | 中断，无退出码和完成结果；日志最后写入约 15:15，恢复会话时系统时间已到 22:48，未生成最终服务器程序，不记作通过；本机最近启动时间为 22:44:46 |
| 原中间目录重跑 All | FAIL，退出码 1，22:48:34–22:49:11；OpenSSL `app.pdb` 报 C2471，无法更新程序数据库；保留目录后从空 OpenSSL 输出目录重建 |
| 空 OpenSSL 输出目录重跑 All | 依赖与构建工具阶段完成；整体 FAIL，22:51:03–23:00:22，退出码 1。XLaunch 两份 PDB 报 C1051，文件创建于下午中断时且文件头全为零 |
| 清空生成对象后的 Server 构建及便携目录整理 | PASS，退出码 0，23:02:46–23:04:54，固定产品源码 `a8bc1793a2` |
| 全套项目测试，启用本地工具和真实运行 | PASS：97 项，0 失败、0 跳过，32.766 秒；此前 73 项加本组 24 项 |
| 独立依赖、版本、认证启动、根窗口查询和清理 | PASS，35 个 EXE/DLL 依赖检查及所有步骤通过；独立 display 97，临时认证，1.311 秒 |
| 便携文件及字体 | PASS：5,129 个唯一文件，文件集合与输入整合版本一致；4,297 个压缩字体完整解压且 PCF 文件头正确 |
| 旧运行文件比较 | 315 个 EXE/DLL 中 299 个 SHA-256 不变，16 个不同；差异全部位于主仓库 `dist/x64/Release`，修改时间为 14:57–14:59，各历史候选目录均未变；不把此项写成全部通过 |

RENDER 覆盖协议长度、空请求、公共函数零/负数量、一帧/两帧构造、分配/查询/安全钩子错误，以及交换字节序空请求。后者的请求体为空，`SwapLongs` 替身断言没有负载；不声称覆盖非空交换字节序负载。正常构造使用无屏幕环境及定时器、资源替身，不验证真实鼠标显示、动画时序或屏幕回调。

RECORD 覆盖共享检查器的数量上限、整数边界、合法空请求、普通范围、2048 客户端选择器、非法头和范围、长度不足，以及真实交换字节序辅助函数的短请求和合法范围转换。不声称完整 RECORD 数据捕获与回放已人工验证。

## 构建与证据

固定产品源码为 `a8bc1793a2a24617794d46416ce11c4ab3ec6696`。先在本次新检出中执行 Dependencies 阶段，再在固定提交执行 All 阶段；中间没有修改第三方依赖、构建脚本或 mhmake 源码。依赖阶段起点为本组基线，其结果文件的 source_commit 字段记录结束时 HEAD，不代表整段构建从该提交开始。两阶段均使用本次新目录，没有复制旧目录的构建缓存。All 仍继承使用 libxml2 预编译文件，不代表该组件已从源码重建。

```powershell
Set-Location D:\File\Program\GitHub\zzxsrv-render-record-20260910
.\scripts\build\buildall.ps1 -Stage Dependencies -Jobs 30 `
  -EnvironmentReport .local-validation/render-record-20260910/dependency-environment.json
.\scripts\build\buildall.ps1 -Jobs 30 `
  -EnvironmentReport .local-validation/render-record-20260910/environment.json
.\scripts\build\buildall.ps1 -Stage Server -Jobs 30 `
  -EnvironmentReport .local-validation/render-record-20260910/environment-server.json
```

本地证据目录为候选下 `.local-validation/render-record-20260910/`。包含原始下载及哈希、`verify-sources.py`、编译环境、红绿测试日志、完整构建和运行报告。最终全套测试使用 `python -B -m unittest discover -s tools/tests -p 'test*.py' -v`，由 `run-tests.ps1 -Runtime` 初始化 x64 MSVC、本地工具和真实运行参数。

重启造成的中断记录为 `build-interrupted.json`，首次重跑失败为 `build-retry-result.json`；相关日志均保留。已核对 `third_party/openssl/release64` 全部为忽略的构建产物，将其在本候选内部移动至证据目录的 `openssl-interrupted-build` 后重新运行 All。后续命令只将环境报告和日志名称改为 `environment-fresh.json`、`build-fresh.log`、`build-fresh-result.json`，产品源码和构建参数不变。不能把这次恢复描述为整个目录从未经历中断的一次构建。

该次 All 已成功完成依赖和 mhmake 阶段，随后发现下午中断留下的 XLaunch PDB 损坏。将本候选 `src/`、`third_party/` 下 100 个不含跟踪文件的 `obj64` 目录移入 `server-interrupted-objects`，路径清单见 `preserved-object-directories.json`；再以同一固定产品源码执行 Server 阶段，包含便携目录整理。保留刚重建成功的基础依赖，不重复执行其配置；最终构建应按各阶段证据组合判断，不把此前 All 的非零退出码改写为成功。

最终环境、构建结果、完整测试及独立运行分别记录在 `environment-server.json`、`build-server-result.json`、`tests.log`、`runtime/result.json`。工具为 MSVC 14.44.35207、SDK 10.0.26100.0、Python 3.14.2。构建期间 HEAD 及产品源码保持固定，后续只追加审查建议的测试和本报告等文档；全套 97 项测试已包含追加用例，追加测试提交为 `c9ab483ee1076e0a03baa9c207c4b5ef55eb7b9d`。

旧运行文件比较见 `old-runtime-comparison.json`。本任务构建、整理命令的输出目标均为新候选目录；主仓库 16 个文件在 14:57–14:59 更新的具体操作者和原因未确认，因此只记录差异，未覆盖或回滚这些文件。新候选验证以自己的源码、产物和日志为依据；不能拿主仓库 dist 代替此候选。`artifact-verification.json` 分别记录便携验证和旧文件差异，避免用一个 PASS 掩盖差异。

## 人工验收与主线整合

2026-09-10，维护者在收到本组候选路径及试用说明后反馈“没问题”，记录为本组实际使用正常。运行目录为 `D:/File/Program/GitHub/zzxsrv-render-record-20260910/dist/x64/Release`。未提供的 Linux/应用版本、连接方式和逐项场景不补造；此次反馈不扩大为所有鼠标动画、RECORD 数据捕获、剪贴板、OpenGL 或多显示器场景已全面验证。GUI-001 仍按此前要求暂缓排查。

本地 master 从 `1bc06775c03e128168064d931f63667d1bc95598` 快进至候选 `918d227ca67df4714b7c6d1352cc69f6b8ddc361`，未产生 merge commit。合入前完整测试 97 项通过、0 跳过，23.917 秒；合入后的主目录源码再次通过 97 项测试、0 跳过，22.981 秒。两次均启用本地工具和真实运行，运行目录指向本组已构建版本，产品源码关联 `a8bc1793a2a24617794d46416ce11c4ab3ec6696`；没有因文档整合重复构建产品。

整合证据位于主仓库 `.local-validation/render-record-integration-20260910/`，合入后测试日志为 `tests-after-merge.log`。此前候选证据继续保留在原目录 `.local-validation/render-record-20260910/`，合入前测试日志为 `tests-acceptance.log`。

清理前完整保留 52,266 个文件、8,815,391,162 字节，逐文件 SHA-256 一致，仅排除根目录 Git 工作区指针；随后通过原生 Git 解除 worktree 登记、删除临时分支 `codex/render-record-20260910`，保留内容恢复到原路径。该目录现为普通保留目录，不能再按 Git worktree 操作；其中源码及旧报告保留候选时点，当前状态以主仓库文档为准。本组运行目录保持原路径，此前保留版本不作修改；主仓库 dist 不会随源码快进自动更新。

本组修复已完成主线整合，仅作本地提交，不 push。R3 历史 21 项中，输入 2 项和 RENDER/RECORD 2 项已整合，另外 17 项尚待实施；下一组为 XKB。
