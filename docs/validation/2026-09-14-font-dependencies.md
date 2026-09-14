# R4 字体依赖升级验证与主线整合

状态：维护者已确认新版本启动、gitk、中文显示和重启正常，已快进合入 master；合入前后各 363 项测试通过、0 跳过，未 push。字体／字号切换未确认，异常输入回归未执行，Fontconfig 既有缓存重复问题继续跟踪。

## 范围与来源

从主线 `0f121774d` 在 `codex/fonts-20260914` 独立工作区推进，计划见 [R4 计划](../plans/2026-09-14-font-dependencies.md)。

| 组件 | 变更 | 本地提交 |
| --- | --- | --- |
| libXfont2 | 2.0.6 → 2.0.9 | `37a7def6f` |
| FreeType | 2.13.3 → 2.14.3 | `3cc7468fc` |
| 公共头文件 | 同步优先 include 副本，防止旧定义遮蔽 | `b0acf97` |
| 正常字体测试 | FreeType、缓存、索引及真实 X Server 绘图 | `4c86cef0a` |

libXfont2 新旧正式包从 [X.Org 发布目录](https://xorg.freedesktop.org/archive/individual/lib/)下载。FreeType 使用[官方网站指定下载入口](https://freetype.org/download.html)的 Savannah 地址，实际重定向至 Rabisu 镜像。完整请求 URL、实际 URL、时间与 SHA-256 记录在[来源 JSON](../dependencies/SOURCES.json)的 `release_archive`。FreeType 新包 SHA-256 与项目 SourceForge 发布页一致；libXfont2 当前记录为实际下载文件计算值，未声称已经对照独立发布 checksum。

| 正式包 | SHA-256 |
| --- | --- |
| libXfont2 2.0.6 | `74ca20017eb0fb3f56d8d5e60685f560fc85e5ff3d84c61c4cb891e40c27aef4` |
| libXfont2 2.0.9 | `f042a370666815e7b941e9b7019024755bd1c6c2954afbfa515af378251799e2` |
| FreeType 2.13.3 | `0550350666d427c74daeb85d5ac7bb353acba5f76956395995311a9c6f063289` |
| FreeType 2.14.3 | `36bc4f1cc413335368ee656c42afca65c5a3987e8768cc28cf11ba775e785a5f` |

保留原导入范围，并纳入新正式包新增文件；未恢复原先就未导入的旧包文件。统一换行比较后，libXfont2 的 121 个、FreeType 的 855 个已跟踪文件与新正式包一致。差异仅为下列明确保留项：

- libXfont2：本地 `config.h`、mhmake `makefile`；`fsio.c` 先 undef EWOULDBLOCK；`bufio.c` 使用 intptr_t 进行文件描述符转换。上游已删除 fontencc 代码及头文件，本地同步移除对应编译项。
- FreeType：本地 `.gitignore`、`ftstring.vcproj`、`ftview.vcproj`。其余原已跟踪文件与旧正式包一致，无额外项目私有源码 patch 需要移植。继续使用现有 MSBuild 工程及配置，不引入动态 HarfBuzz 依赖。
- FreeType 内嵌 zlib 仍声明 1.3，来源现为 FreeType 2.14.3 正式包及包内 patches，不等同于根目录 zlib，也不声称独立取得新 zlib 包。

libXfont2 上游新版本默认关闭 fontserver，但 Windows 现有 `XFONT_FC=1` 配置保持启用。现有消费者配置不因此发生意外变化；远程 fontserver 使用场景仍未验收。

## 共享头文件审查修正

独立审查确认 mhmake 的全局 `include/` 优先于组件 `include/`。原共享 `bdfint.h` 仍定义 `BDF_GENPROPS=6`，会遮蔽正式包的新定义 8。同步该头及 `libxfont2.h`，删除无消费者的共享 `fontencc.h`；其他继承头文件不作整目录替换。新增公共副本一致性测试，修正前两个子用例失败，修正后通过。

## 验证记录

基线在新工作区运行：350 项，无失败、3 项跳过，40.512 秒。跳过源于本工作区尚未构建 mhmake 和字体工具；这些项目已在最终完整构建后的运行中覆盖，最终 0 跳过。

首次构建在依赖阶段主动停止以修正审查发现的共享头文件遗漏；原日志为 `build-before-shared-headers.log`，不计为成功构建。重跑 All 构建固定源码 `b0acf97cab01ff80ac70e96152252e58925aa858`，命令：

```powershell
.\scripts\build\buildall.ps1 -Jobs 30 -EnvironmentReport .local-validation/fonts-20260914/environment.json
```

完整构建时间 `2026-09-14T16:43:48.5730072+08:00` 至 `2026-09-14T16:55:40.1704808+08:00`，退出码 0，构建前后 HEAD 相同。

| 验证 | 结果 |
| --- | --- |
| 全套测试，启用本地工具和实际运行 | 363 项测试通过，0 失败、0 跳过，42.140 秒 |
| FreeType 正常 API 与消费者 | 10 项通过：实际 DLL 版本、TTF/CFF OTF 灰度/单色、缺字回退、Latin/CJK BDF、Fontconfig 缓存重载/列表/匹配、mkfontscale |
| 经真实 X Server 的 core font 绘制 | 2 项通过：PCF 绘制 117 个非背景像素，TrueType 绘制 204 个非背景像素 |
| 公共头文件一致性 | 1 项通过；原两个子用例失败证据保留 |
| 独立运行验证 | PASS，3.284 秒；依赖、版本、认证启动、根窗口查询及清理通过 |
| 便携目录实际文件 | 5,129 个；文件集合与上一候选相同 |
| 压缩字体 | 4,297 个解压及 PCF 文件头检查通过 |
| 既有运行文件 | 490 个 EXE/DLL 哈希保持不变 |

上面新增的 13 项包含在全套 363 项中，不重复累加。FreeType API/消费者使用真实 Release DLL，未将其描述为经过 ASan 插桩。CJK 自动覆盖的是 BDF 中的“中”字，不代表中文轮廓字体、塑形或 GUI 显示已验收。测试也确认旧 2.13.3 DLL 被版本断言拒绝，避免误用旧产物。

独立审查复核新旧归档与导入文件集合、Windows 适配、FreeType 模块衔接及来源记录，并发现公共头遗漏；修正后原 Important/Minor 项均关闭。后续正常测试审查无新增 Important；绘图日志保留建议已落实。详细证据位于 `.local-validation/fonts-20260914/`：`build-result.json`、`build.log`、`environment.json`、`tests-final.log`、`freetype-tests.log`、`core-font-tests.log`、`runtime/result.json`、`artifact-verification.json`、`source-verification.json`、`import-review.md`、`fix-and-test-review.md`、`final-review.md`。最终定向审查确认可交付待人工验收候选，无剩余 Critical/Important/Minor；未将本轮范围外的已知问题或未执行测试视为已解决。

## 验证限制

正常缓存测试另发现 Fontconfig 既有 Windows 枚举问题：`FcCompatReaddirWin32` 将返回名称指向 `fdata.cFileName`，随后 `FindNextFile` 覆盖同一缓冲。旧产物预检和本轮新产物的两字体目录均产生 3 条缓存 pattern，最后一项重复；`FcFontList` 去重后仍返回两字体，重新加载及匹配可用。保留原严格数量断言失败日志，测试核对字体列表中每条 pattern 的文件和字符集，缓存数量如实输出。本轮未修改 Fontconfig，此问题进入 R9 单独维护；不把正常测试通过扩展成任意目录枚举正确或缓存无重复。

libXfont2 异常输入回归子任务被自动安全审核拒绝，返回“possible cybersecurity risk”，未执行。没有重试或改由其他路径执行该被拒绝任务；上游包自带测试作为正式源码内容保留，但未声称其已在 Windows 编译或运行。该项仍为验证缺口，正常字体加载、绘制及整包回归不能替代它。

R3 的实际反馈仅适用于旧目录：启动、gitk、中文显示和重启正常；传统字体、OpenGL、双向复制未测试。R4 已取得启动、gitk、中文显示和重启的实际反馈；字体／字号切换原文为“正常或未测”，不记为已通过。GUI-001 已关闭，不重新开展。

## 实际反馈与主线整合

2026-09-14，维护者反馈：“R4 新目录：启动正常；gitk 正常；中文正常；重启正常；字体／字号切换正常或未测。”前四项记录为正常；最后一项保留未确认，不自行选择“正常”。传统字体、OpenGL、双向复制的人工结果未补充。详细场景见 [兼容性记录](../maintenance/COMPATIBILITY.md)。

master 从 `0f121774d07c6895fe4e5be5d5872fefe78c7094` 快进到 `7b4468fef5692f1e9cffb06ef0df0c037acb9a00`，保留组件、公共头文件、测试与文档的独立提交，没有 merge commit。

合入前后各执行 363 项测试，均无失败、无跳过，耗时分别为 42.313 秒和 42.284 秒。两次均在保留的候选工作区运行，使用其匹配的本机构建依赖和运行目录；合入后核实该工作区与 master 指向同一整合提交且无文件差异。没有冒用主目录旧 FreeType 产物，也没有声称本轮重新执行完整构建。生产构建仍固定为 `b0acf97cab01ff80ac70e96152252e58925aa858`。

核对原交付清单，5,129 个运行文件集合及 SHA-256 均未改变。继续使用 `D:/File/Program/GitHub/zzxsrv-fonts-20260914/dist/x64/Release/xlaunch.exe`；主目录源码更新不会自动重编译主目录旧 dist。

运行目录、临时分支及 worktree 登记保留。此前 R3 的登记清理受到自动审批拒绝，本轮不尝试绕过或重复同类清理。整合证据位于主目录 `.local-validation/fonts-integration-20260914/`，包含合入前后日志及 `verification.json`。仅本地提交，未 push。

R4 版本升级与有限实际验收已整合；异常输入回归缺口、字体／字号切换未确认及 Fontconfig R9 问题仍明确保留，不宣称全场景完成。
