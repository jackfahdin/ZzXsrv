# XSYNC / PRESENT / 屏保公开修复静态核对

> 目录迁移说明（2026-09-10）：文档链接已更新，正文中的旧命令与文件路径仍表示当时状态；当前入口见[文档导航](../README.md)。

> 2026-09-10 历史说明：本文保留当时的方案、提交号与验证结果。旧分支、标签和工作区登记已清理，源码及运行目录保留为普通目录；旧命令不应直接照搬执行。现行规则见[维护规则](../maintenance/UPSTREAM.md)，对应关系与恢复材料见[整理记录](2026-09-10-repository-reorganization.md)。旧依赖快照清单见[历史 JSON](../history/2026-09-09-dependency-snapshot.json)；当前不再维护上游源码分支。

审计日期：2026-09-09。工作树基线：master `dd555fe9f`。仅静态读取；未修改源码、Git 引用，未构建、运行服务或发送网络测试请求。下表判断的是源码是否具有官方修复条件，不代表已经证明任何已发布二进制可被动态利用。

参考为本次取得的官方 X.Org Server 21.1.24 源码，路径 `.local-validation/xserver-audit-20260909/release/xorg-server-21.1.24`，来源 https://xorg.freedesktop.org/archive/individual/xserver/xorg-server-21.1.24.tar.xz ，SHA256 `1a4eb36ca65cc3b1b936566d677a9786e13c11cd5806e951ac55f3f5ce3984af`。下列官方 SHA 来自该源码包的 ChangeLog；未假设 VcXsrv 的 21.1.99 开发快照等同于稳定分支，逐函数比较了控制流和生命周期。

## 结果

| 事项 | 状态 | 本地关键位置 | 官方关键修复及缺口 |
|---|---|---|---|
| CVE-2025-62229 / PRESENT | 需回补 | `xorg-server/present/present_notify.c:74`，尤其 `:95`、`:100` | 本地成功加入后 `added = i`，清理按 `added` 个元素执行，记录的是最后下标，少清理一个已挂链的元素。官方成功加入后 `added++`，按实际数量摘链。 |
| CVE-2026-34001 / miSyncTriggerFence | 需回补 | `xorg-server/miext/sync/misync.c:130`，尤其 `:137-140` | 本地预存 `pNext` 后执行可能删除同组 await 触发器的回调，再沿旧 `pNext` 继续。官方在触发后 break，并从当前表头重新遍历。 |
| CVE-2026-50257 / miSyncDestroyFence（ZDI-CAN-30159） | 需回补 | `xorg-server/miext/sync/misync.c:107`，尤其 `:117-120`；共享释放 `xorg-server/Xext/sync.c:1218` | 本地回调后才读取 next，未提前更新表头，也未防止同组 await 的失效 pTrigger 被再次解引用。官方安全遍历、回调前更新表头、跳过 NULL 触发器，并由 FreeAwait 对正在销毁对象的相应节点清空 pTrigger。 |
| CVE-2026-50260 / FreeCounter（ZDI-CAN-30163） | 需回补 | `xorg-server/Xext/sync.c:1186`，尤其 `:1196-1199`；`:1235-1238` | 与上一项同一个官方提交。FreeCounter 的更新表头和 NULL 检查、FreeAwait 的清空残余节点 pTrigger 分支均缺失。 |
| CVE-2026-50261 / SyncChangeCounter（ZDI-CAN-30164） | 需回补 | `xorg-server/Xext/sync.c:744`，尤其 `:752-755` | 本地 TriggerFired 后直接沿预存 pnext 继续。官方最终源码在回调后验证 pnext 仍在当前表中；若不在则从当前表头继续，避免使用已删除节点。 |
| CVE-2026-50263 / CreateSaverWindow（ZDI-CAN-30168） | 需回补 | `xorg-server/Xext/saver.c:453`，尤其 `:470-475`；释放条件 `:192-203` | CheckScreenPrivate 可能释放 pPriv 并把屏幕私有指针设为 NULL；本地继续解引用缓存 pPriv。官方在该调用后 `pPriv = GetScreenPrivate(pScreen)`，使后续 NULL 检查有效。 |

分派范围共 6 个 CVE，源码层面均缺少关键修复。2026-502xx 与 ZDI 的映射沿用本次公告索引核对的已核实映射；21.1.24 ChangeLog 对这些条目只列 ZDI，不能单靠该 ChangeLog 独立证明 CVE 编号映射。

## 官方提交与源码定位

| 事项 | 官方稳定分支 SHA | ChangeLog 中列出的 master SHA | 21.1.24 对应位置 |
|---|---|---|---|
| PRESENT 计数修复 | `554dfabfbc23c3e74997e09c13f5424a60daf9ee` | `5a4286b13f631b66c20f5bc8db7b68211dcbd1d0` | `present/present_notify.c:93`；ChangeLog `:2045-2110` |
| miSyncTriggerFence | `70aad8867abdb03d8fd4fcc7405a7ee7c4666539` | `f19ab94ba9c891d801231654267556dc7f32b5e0` | `miext/sync/misync.c:136-153`；ChangeLog `:958-1018` |
| FreeCounter + miSyncDestroyFence + FreeAwait | `f304b57444be3991fd9d3389f309c6eeb056a6c4` | `f5abfb61994471023d8c6470428c8e30c411cc0b` | `miext/sync/misync.c:122-126`，`Xext/sync.c:1186-1192`、`:1231-1244`；ChangeLog `:573-609` |
| SyncChangeCounter | `92a167ab3fda0bee41cf97f6a40a4c01c67d85d4` | `bdd7bf57af208b1ddf57d4683d67104443b44812` | `Xext/sync.c:713-746`；ChangeLog `:543-569` |
| CreateSaverWindow | `182c23f780402062ab31963776a19d5b87e25ac8` | `ecc634f1b2f7aa473d3a267eada98c4918bf9e05` | `Xext/saver.c:484-486`；ChangeLog `:404-442` |

## 构建路径证据

- `buildall.ps1:327` 用 `-C xorg-server MAKESERVER=1` 启动服务器构建。`xorg-server/makefile:19`、`:24`、`:29` 链接 libsync、libxext、libpresent；`:47` 加载各库 makefile；`:55-59` 输出 vcxsrv。
- `xorg-server/miext/sync/makefile:7` 包含 misync.c；`xorg-server/Xext/Makefile:4`、`:8` 包含 saver.c、sync.c；`xorg-server/present/makefile:7` 包含 present_notify.c。
- `makefile.before:102` 将根 include 加入服务器头文件搜索路径；`include/dix-config.h:290`、`:311`、`:392` 分别定义 PRESENT、SCREENSAVER、XSYNC 为 1。
- `xorg-server/mi/miinitext.c:115` 注册 SYNC，`:140` 注册 MIT-SCREEN-SAVER（受 noScreenSaverExtension 开关控制），`:152` 注册 Present。`xorg-server/Xext/sync.c:2494-2500` 初始化扩展并对 screen 调用 miSyncSetup。
- SYNC 普通协议派发包含 DestroyCounter / Await / TriggerFence / DestroyFence / AwaitFence（`xorg-server/Xext/sync.c:2166-2192`）。此处不依赖启用 Linux DRI3 才有普通 fence 请求路径。PRESENT 初始化中 `xorg-server/present/present_screen.c:272` 为 screen 初始化默认实现。

这些证据说明不能因 Windows 平台或文件位于 miext 下，就把缺口排除出当前构建。未读取任何已安装二进制的运行时扩展清单，因此不对具体启动选项、客户端授权、网络暴露或实际攻击可达性下结论。

## 回补前置、重叠及相邻公开修复

1. 50257 与 50260 是同一个生命周期修复，必须把 miSyncDestroyFence、FreeCounter、FreeAwait 一起移植；仅改某个 for 循环不足以避免后续节点继续引用已释放的同组 await。`nt_list_for_each_entry` / `_safe` 已存在于本地 `xorg-server/include/list.h:386`、`:401`，无需仅为这个补丁引入新的链表库。
2. 34001 与 50261 都处理 TriggerFired 回调令预存后继失效，但遍历方式不能机械共用。21.1.24 的 `Xext/sync.c:731-734` 明确解释 counter 列表可能含不被移除的 alarm，delta 为 0 时无条件 do/while 重启会无限循环。应以官方最终代码的 pnext 存活检查为准，而不是只读 ChangeLog 概述后照抄 fence 循环。
3. PRESENT 同函数还有另一项公开修复也缺失：本地 `present_notify.c:97` 直接 Success 返回，未执行 `*p_notifies = notifies`；调用方 `present_request.c:121` 初始 NULL，并在 `:168` 传输出地址。官方稳定分支 `2be25deaa6a73aa9e680932065095e025019da32` / master `f70cc16c6831c9faa14c1f2a8588c6efb6ede263`（ChangeLog `:624-637`，标题 “present: actually return the created notifies”）在 `present_notify.c:96` 增加该输出赋值。它与 62229 计数修复同函数重叠，但不是把两者混为同一个 CVE；应一起评审。
4. 屏保提交还在 ScreenSaverFreeAttr 的 CheckScreenPrivate 后加入 `pPriv = NULL`（官方 `Xext/saver.c:350-353`，本地 `:340-341` 缺失）。ChangeLog 明确该处赋值没有实际行为作用；真正影响本项判断的是 CreateSaverWindow 重新读取私有指针。
5. VcXsrv 使用 int64_t counter 值、`X11_RESTYPE_NONE` 资源名和 `_MSC_VER` 适配；这些差异不抵消上述修复条件。回补应保留本地接口与 Windows 适配，按函数移植，不整文件覆盖。

## 审计边界

本报告没有 PoC、崩溃复现或动态利用性证明，没有执行网络测试，没有改源代码。证据足以给出这些公开修复的静态缺失判断；不足以推断安装版本、默认监听行为或内存破坏后果。除本审计 Markdown 外，本子任务只读取仓库内容。
