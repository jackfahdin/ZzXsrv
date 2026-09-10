# XKB 公开修复静态核对（2026-09-09）

> 后续状态：本文是历史缺口审计。所列 8 项及配套修复已在 [XKB 候选](2026-09-10-xkb.md)中实施，正在验证且尚待实际使用确认，未合入 master。以下“需回补”表示原审计基线。

> 目录迁移说明（2026-09-10）：文档链接已更新，正文中的旧命令与文件路径仍表示当时状态；当前入口见[文档导航](../README.md)。

> 2026-09-10 历史说明：本文保留当时的方案、提交号与验证结果。旧分支、标签和工作区登记已清理，源码及运行目录保留为普通目录；旧命令不应直接照搬执行。现行规则见[维护规则](../maintenance/UPSTREAM.md)，对应关系与恢复材料见[整理记录](2026-09-10-repository-reorganization.md)。旧依赖快照清单见[历史 JSON](../history/2026-09-09-dependency-snapshot.json)；当前不再维护上游源码分支。

对象：VcXsrv `master`，HEAD `dd555fe9febd00dc2880553a55e82a27dace284f`。本报告只核对所列 8 项公开修复特征，不修改源码、Git 引用或执行网络/动态利用测试。

基准：`.local-validation/xserver-audit-20260909/release/xorg-server-21.1.24/`，官方下载包 `https://xorg.freedesktop.org/archive/individual/xserver/xorg-server-21.1.24.tar.xz`；本次计算的 SHA256：`1a4eb36ca65cc3b1b936566d677a9786e13c11cd5806e951ac55f3f5ce3984af`。下列“官方行”相对于该基准目录；“本地行”相对于仓库根。修复 SHA 来自该包 ChangeLog，核对以函数行为为准，没有把整文件不同当作缺补丁证据。

结论：这 8 项均为 **需回补**，含义是本地缺少官方针对这些问题的关键检查/生命周期更新。不是动态可利用性结论，也不是这份源码全部 CVE 的审计结果。本次已确认当前 `XKB=1` 且构建包含 xkb。

| 项目 | 状态 | 本地直接证据 | 官方修复特征 |
| --- | --- | --- | --- |
| CVE-2025-62230 | 需回补 | `xorg-server/xkb/xkbEvents.c:1056,1067` 直接 free interest/victim；`xorg-server/xkb/xkb.c:56` RT_XKBCLIENT 仍是 static | 官方 `xkb/xkbEvents.c:1059,1071` 在释放前调用 `FreeResource(..., RT_XKBCLIENT)`，并让资源类型可供该编译单元使用 |
| CVE-2025-62231 | 需回补 | `xorg-server/xkb/xkb.c:2990-2994` 把 `firstSI+nSI` 直接写入 `num_si/size_si` 后分配，缺 `USHRT_MAX` 检查 | 官方 `xkb/xkb.c:3065-3066` 在赋值前拒绝大于 `USHRT_MAX` 的总数 |
| CVE-2026-33999 | 需回补 | `xorg-server/xkb/xkb.c:3000` 仅在 `truncateSI` 时更新复用缓冲区的 `num_si` | 官方 `xkb/xkb.c:3077` 还检查 `firstSI+nSI > compat->num_si`，扩大有效项数 |
| CVE-2026-34000 | 需回补 | `xorg-server/xkb/xkb.c:5594` 仅验证 `wire + XkbKeyNameLength`，紧接 `5597` 读取第二个名称 | 官方 `_CheckSetGeom`，`xkb/xkb.c:5693` 验证 `wire + 2 * XkbKeyNameLength` |
| CVE-2026-34002 | 需回补 | `xorg-server/xkb/xkb.c:1941` CheckModifierMap 无 ClientPtr；`1965-1966` 按 totalModMapKeys 迭代直接读 wire | 官方 `xkb/xkb.c:2003,2028-2031` 传入 client，并逐项验证 `wire..wire+2` |
| CVE-2026-34003 | 需回补 | `xorg-server/xkb/xkb.c:1637-1644` 在循环中直接交换/读取类型；`1664-1666` 构造 map/preserve 指针后直接迭代 | 官方 `xkb/xkb.c:1647-1650,1676-1687` 分别验证类型描述、map entries、preserve entries 的请求范围 |
| CVE-2026-50258（ZDI-CAN-30160） | 需回补 | `xorg-server/xkb/xkb.c:1645` 只检查 width < 1，没有 numLevels 上界 | 官方 CheckKeyTypes，`xkb/xkb.c:1656` 检查 `width < 1 || width > XkbMaxShiftLevel` |
| CVE-2026-50259（ZDI-CAN-30161） | 需回补 | `xorg-server/xkb/xkb.c:1612-1618` ResizeTypes 分支只检查 nMaps 下界；`1707` 以 firstType+i 写入 mapWidthRtrn；调用者 `2479` 只有 `XkbMaxLegalKeyCode+1` 项 | 官方 `xkb/xkb.c:1620-1624` 拒绝 `nMaps > XkbMaxLegalKeyCode + 1` |

## 官方提交对应

这些 SHA 是 ChangeLog 对修复归属的记载（release SHA / cherry-picked master SHA），不是根据本地 Git 祖先关系作出的判断。

- **62230**：`87fe2553937a99fd914ad0cde999376a3adc3839` / `10c94238bdad17c11707e0bdaaa3a9cd54c504be`，`xkb: Free the XKB resource when freeing XkbInterest`。ChangeLog 1961-2019。前置提交：`865089ca70840c0f13a61df135f7b44a9782a175` / `99790a2c9205a52fbbec01f21a92c9b7f4ed1d8f`，`xkb: Make the RT_XKBCLIENT resource private`，ChangeLog 2021-2043。官方涉及 `xkb/xkb.c`、`include/xkbsrv.h`、`xkb/xkbEvents.c`。
- **62231**：`3baad99f9c15028ed8c3e3d8408e5ec35db155aa` / `475d9f49acd0e55bc0b089ed77f732ad18585470`，`xkb: Prevent overflow in XkbSetCompatMap()`，`xkb/xkb.c`；ChangeLog 1933-1959。
- **33999**：`432cb931cf1f40cbc992916fcff716db864da1af` / `b024ae1749ee58c6fbf863b9a1f5dc440fee2e1b`，`xkb: fix buffer re-use in _XkbSetCompatMap`，`xkb/xkb.c`；ChangeLog 1074-1101。
- **34000**：`a48d67f38753de551cd177e471b545bd8b9b1b64` / `81b6a34f90b28c32ad499a78a4f391b7c06daea2`，`xkb: Fix bounds check in _CheckSetGeom()`，`xkb/xkb.c`；ChangeLog 1022-1072。
- **34002**：`5328a544ba6c32ecdd1758283ee69058dec100f8` / `f056ce1cc96ed9261052c31524162c78e458f98c`，`xkb: Fix out-of-bounds read in CheckModifierMap()`，`xkb/xkb.c`；ChangeLog 907-956。
- **34003**：`905194d1fa3009c5c7f94ec0392424cd44e6a6d9` / `b85b00dd7b9eee05e3c12e7ad1fce4fc6671507b`，`xkb: Add additional bound checking in CheckKeyTypes()`，`xkb/xkb.c`；ChangeLog 835-905。
- **50258 / CAN-30160**：`eced7e74cad4a46c3a3c17b2df13b70b8bedfc25` / `543e108516428fc8c3bea91d6563ad266f9a801e`，`xkb: reject key types with num_levels exceeding XkbMaxShiftLevel`，`xkb/xkb.c`；ChangeLog 512-541。
- **50259 / CAN-30161**：`54c3d9fad0f2f97835da9d275b53255f4963029f` / `867b59b33bee669cb412f1314e47c52eacf6e00b`，`xkb: clamp nMaps to mapWidths buffer size in CheckKeyTypes`，`xkb/xkb.c`；ChangeLog 481-510。

50258/50259 的 CVE ↔ ZDI 映射由本次读取 [X.Org 官方安全索引](https://www.x.org/Development/Security/)（June 02, 2026）确认；本地包的这两条 ChangeLog 只出现 ZDI 标识。

## 前置、重叠与已有检查

1. **62230 资源类型可见性前置缺失。** 本地 `xkb.c:56` 仍是 static，`include/xkbsrv.h` 和 `xkb/xkbsrv_priv.h` 均没有该资源类型声明。回补需要把资源类型提供给 xkbEvents.c，不能只复制 FreeResource 两行。21.1.24 稳定分支在 `include/xkbsrv.h:61` 声明；本地开发快照已使用 `xkb/xkbsrv_priv.h`，应按本地私有头结构适配。实际设备清理路径在 `xorg-server/dix/devices.c:1037` 调用 XkbRemoveResourceClient；客户端资源回调在 `xorg-server/xkb/xkb.c:7123` 再调用它。这里仅记录静态生命周期路径。
2. **62231 和 33999 同处 _XkbSetCompatMap，但解决不同状态不变量。** 前者限制 unsigned short 存储范围（本地 `X11/extensions/XKBstr.h:378-379`）；后者维护复用容量内的有效条目计数。本地 `xkb.c:3025-3030` 还有 skipped 条目的整理和 `num_si -= skipped`，因此只加整数上界并不补上复用计数修复；二者均需纳入。
3. **34002/34003 有配套加固提交。** `e8674488a678387699629a0b558256cc04049ea8` / `d38c563fab5c4a554e0939da39e4d1dadef7cbae`（ChangeLog 804-833，`xkb: Add more _XkbCheckRequestBounds()`）明确关联这两个 CVE，在 CheckKeySyms、CheckKeyActions、CheckKeyBehaviors、CheckVirtualMods、CheckKeyExplicit、CheckVirtualModMap 及 _XkbSetMapChecks 调用处补检查/传参。该套检查本地也缺失：本地 xkb.c:1799/1832/1883/1900/1977 的签名没有 client，2536-2574 调用保持旧形式。官方检查见 xkb.c:1761/1804/1849/1904/1947/1984/2069。动作数据区域检查 1867 另属后续 a439a734，见追加核对。回补建议作为同组核对，不把它重复计算为额外 CVE。
4. **50258、50259 与 34003 都修改 CheckKeyTypes，但不能互相替代。** 34003 检查输入数据在请求内；50258 约束每个类型的层数；50259 约束类型表/栈数组索引总数。需要最终函数同时具有三组保护。
5. **50258 的消费路径未发现替代上界。** 本地 SetKeyTypes 在 `xkb.c:2041` 储存 numLevels；`xkbUtils.c:222,240-241` 将固定 `tsyms[XkbMaxSymsPerKey]` 传给 `XkbKeyTypesForCoreSymbols`；`XKBMisc.c:43,60-65` 由 num_levels 推导 groupsWidth 并据此索引。常量在 `X11/extensions/XKB.h:560-561` 定义为 63、63×4。这里只核对官方所述输入和消费条件仍存在，未发请求验证。
6. **已有早期检查不等于包含后续补丁。** 本地 `xkb.c:158` 已有 _XkbCheckRequestBounds 辅助函数，`2391` 已有总请求长度函数，`2726` 调用总长度检查。但官方 21.1.24 同样保留 _XkbSetMapCheckLength（官方 xkb.c:2463,2799），并仍加入上述逐次请求范围检查。本地 `CheckKeyTypes` 还会受 ResizeTypes 而非仅 present 位驱动，不能用“已有总长度检查”替代函数级修复特征核对。本报告未据此证明某个具体恶意请求能够穿透全部检查。

## 核对边界

- 只读检查官方发布树和本地相关函数/调用者/类型定义；未读取或比较全部 XKB 历史提交补丁，也未复现漏洞。
- 不声称这些问题一定能在当前 Windows 二进制或运行参数下被利用；运行时设备配置、访问控制、打包二进制来源仍需另行核对。
- 初轮覆盖分配的 8 项；后续按父任务要求追加相邻无 CVE 加固（见下），仍不是完整 XKB 审计。
- 本次仅新建本报告；未改动源码、构建产物、网络端口或 Git 引用。


## 追加：21.1.23 / 21.1.24 相邻无 CVE 修复

按相邻修复核对范围，核对 ChangeLog 中最近两版的相邻 XKB 加固。以下 7 项都缺官方修复特征，**不增加 CVE 个数**。其中前 6 项是 21.1.23 的 MR !2224 同组，最后一项为 21.1.24 的分配失败处理。行号规则同上。

| 修复（master SHA 前缀） | 判定 | 本地证据与官方具体检查 |
| --- | --- | --- |
| CheckKeyActions 动作数据区边界（a439a734） | 缺失，需回补 | 本地 `xorg-server/xkb/xkb.c:1826-1828` 根据实际累加 nActs 直接推进并返回，没有验证整个动作区。官方 `xkb/xkb.c:1865-1870` 在推进后执行 `nActs > 0 && !_XkbCheckRequestBounds(client, req, wire, *wireRtrn)`，错误码 0x25。`nActs > 0` 保留零动作合法情况。 |
| _CheckSetOverlay 行索引及分配检查（ed19312c） | 三处均缺失，需回补 | 本地 `xorg-server/xkb/xkb.c:5298` 是 `rowUnder > section->num_rows`；`5288` 和 `5303` 分配后未检查 NULL。官方 `xkb/xkb.c:5383` 改 `>=`，`5372-5373` 和 `5389-5390` 分别对 ol/row 为 NULL 返回 BadAlloc。 |
| _CheckSetGeom 颜色索引（6b6e8020） | 两处均缺失，需回补 | 本地 `xorg-server/xkb/xkb.c:5546,5551` baseColorNdx/labelColorNdx 与 nColors 使用 `>`；官方 `xkb/xkb.c:5645,5650` 使用 `>=`，拒绝等于数组元素数的索引。该检查也自然拒绝零颜色时的索引，不能把两个颜色索引不相等的既有检查当作替代。 |
| _CheckSetShapes 轮廓索引（86a321ad） | 两处均缺失，需回补 | 本地 `xorg-server/xkb/xkb.c:5493-5496` 只排除 XkbNoShape（0xff），直接索引 outlines。官方 `xkb/xkb.c:5580-5595` 保留哨兵例外，对 primaryNdx 和 approxNdx 分别要求 `< shapeWire->nOutlines`，否则设置错误值并返回 BadValue。 |
| XkbAddGeomDoodad section 容量（dd8b8cf4） | 缺失，需回补 | 本地 `xorg-server/xkb/XKBGAlloc.c:770` 比较 `section->num_doodads >= geom->sz_doodads`；官方 `xkb/XKBGAlloc.c:772` 使用 `section->sz_doodads`。本地 `xorg-server/xkb/xkb.c:5177` 的 _CheckSetDoodad 调用该分配函数，属于同组 geometry 请求处理的直接相关加固。全局 geometry 分支本来正确，不属于此次缺口。 |
| XkbVModIndexText CFile 前缀长度（5dfb435c） | 缺失，需回补 | 本地 `xorg-server/xkb/xkbtext.c:138-144` 给 `vmod_` 前缀只加 4 字节，在偏移 5 处复制 len-4；官方 `xkb/xkbtext.c:140-146` 加 5 且复制 len-5。这是同组格式化缓冲区修复；未验证当前运行配置是否调用 XkbCFile 路径，不将其表述为已验证的网络触发问题。 |
| _Concat realloc 失败保留旧指针（d6c462f5） | 缺失；相邻普通错误处理修复 | 本地 `xorg-server/xkb/maprules.c:480,485-488` 使用 int len，把 realloc 结果直接赋给 str1；官方 `xkb/maprules.c:474-486` 使用 size_t len 和 tmp，失败返回原 str1。官方描述为防止丢失原缓冲区引用的泄漏，未在本报告提升为 CVE 或越界问题。 |

### 追加提交出处

- `852bf24683d8d9fc482632582744c0e4b6791cb3` / `a439a7340ad976983ef34eca4f537831b38e191f`；ChangeLog 641-667，`xkb: Add bounds check for action data in CheckKeyActions()`；文件 `xkb/xkb.c`。
- `5f2ac0de4798f2290620ff89ba86af171c45013c` / `ed19312c4bda0a8f66b236348ffc553e5d8d2a09`；ChangeLog 669-687，`xkb: Fix off-by-one and NULL dereferences in _CheckSetOverlay()`；文件 `xkb/xkb.c`。
- `7ee87732a90cd557b6dd0f69b05af30e7f489b4b` / `6b6e8020b902e48e3330f9a54cd439a51988bc50`；ChangeLog 689-703，`xkb: Fix off-by-one in color index validation in _CheckSetGeom()`；文件 `xkb/xkb.c`。
- `39befa04f92a5acd2f97ef414a799a4a38e979d1` / `86a321ad98213957bbb56f295417b0939326718b`；ChangeLog 705-720，`xkb: Fix out-of-bounds array access in _CheckSetShapes()`；文件 `xkb/xkb.c`。
- `c251243f282acaf590201d8bd2508aebeb6d8fb5` / `dd8b8cf49d326802c53b01835618a7e3765d91cb`；ChangeLog 757-777，`xkb: fix incorrect size check when growing doodads in a section`；文件 `xkb/XKBGAlloc.c`。
- `cc2bd590f368cb6aaa5d1b54e3ac4689f37f54ed` / `5dfb435c1d864bf154369cb86d085d4159730378`；ChangeLog 738-755，`xkb: fix potential buff overflow in XkbVModIndexText for XkbCFile format`；文件 `xkb/xkbtext.c`。
- `a29a7c1ec5b488b4069ef976e8096cb997074e49` / `d6c462f59927b3702a54e0e8ea2a5de7639294e6`；ChangeLog 234-253，`xkb: preserve buffer on realloc failure`；文件 `xkb/maprules.c`。

### 追加前置与重叠说明

- **更正归属**：原初轮报告曾把官方 CheckKeyActions 的整个动作区检查 `xkb.c:1867` 混在 d38c563f 的检查行列表内，现已更正。d38c563f 对本函数添加的是 ClientPtr 及逐个计数字节检查（官方 `1849`）；a439a734 在这个基础上添加整个动作区检查（官方 `1867`）。本地两者都缺，仍是两项保护均待补。不能只取最新的 4 行检查而遗漏 ClientPtr/调用点前置。
- a439a734 的官方说明明确区分 `_XkbSetMapCheckLength` 使用的头部 `req->totalActs` 与 CheckKeyActions 从计数字节实际累加的 `nActs`（ChangeLog 653-657）。这进一步支撑“总长度检查不能代替后续逐区域检查”的静态结论，不代表本报告已经完成动态请求复现。
- _CheckSetGeom 颜色索引补丁与 CVE-2026-34000 的 key alias 双名称边界补丁同函数但不同数据区，均应保留。
- _CheckSetOverlay / _CheckSetShapes 本地已有 wire 描述符范围检查（本地 xkb.c:5281/5295/5306、5458/5471/5480），这些只能检查请求字节是否存在，不能代替索引必须小于服务端数组元素数的语义检查。
- 未发现这些相邻补丁已经由本地同函数中的等效条件完整覆盖；没有把它们计为新的 CVE，也未穷尽历史普通 bugfix。追加过程仍仅修改本审计 Markdown 文件，源码和 refs 保持只读。
