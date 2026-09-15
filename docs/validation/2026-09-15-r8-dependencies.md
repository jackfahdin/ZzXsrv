# R8 键盘、图标与压缩依赖维护

日期：2026-09-15。基线：`20901884259bacfe34b9ca435c81021862800a5a`。
分支：`codex/r8-20260915`，工作区：`D:/File/Program/GitHub/zzxsrv-r8-20260915`。

状态：源码导入、独立审查、完整构建和提交前 420 项实际产物回归通过；提交后复核进行中。尚未取得本版本人工反馈，未合入或推送。R7 和更早工作区、运行目录继续保留。

## 来源与范围

| 组件 | 继承版本 → 本轮版本 | 官方归档 SHA-256 |
| --- | --- | --- |
| xkbcomp | 1.4.7 → 1.5.0 | `2ac31f26600776db6d9cd79b3fcd272263faebac7eb85fb2f33c7141b8486060` |
| libXpm | 3.5.17 → 3.5.19 | `ad3576d689221a39dc728f0e0dc02ca7bb6a0d724c9a77fd1bfa1e9af83be900` |
| zlib | 1.3 → 1.3.2 | `bb329a0a2cd0274d05519d61c667c062e06990d72e125ee2dfa8de64f0119d16` |

分别从 [X.Org app 归档](https://xorg.freedesktop.org/archive/individual/app/xkbcomp-1.5.0.tar.xz)、[X.Org lib 归档](https://xorg.freedesktop.org/archive/individual/lib/libXpm-3.5.19.tar.xz)和 [zlib 官方归档](https://zlib.net/fossils/zlib-1.3.2.tar.gz)取得。校验值与维护者发布公告或官方网站一致：[xkbcomp 公告](https://www.mail-archive.com/xorg-announce@lists.x.org/msg01854.html)、[libXpm 公告](https://www.mail-archive.com/xorg@lists.x.org/msg08285.html)、[zlib 官网](https://zlib.net/)。未独立验证 PGP 签名，不把发布 tag 当作已核验 Git 提交。

三个官方归档分别含 57、156、254 个普通文件。各组件的 `source-files.json` 分列原始摘要、实际文件摘要、路径映射及本地文件，`patches/windows.patch` 记录上游文件修改。Git 属性保留原始字节。旧版本官方包也下载对照，继承源码保存在忽略证据目录，没有整文件覆盖新上游修复。

这次更新根 zlib，FreeType 内嵌 zlib 和各 Meson fallback 声明保持各自来源，不能称为全仓 zlib 副本统一升级。zlib contrib/minizip 不在现有 Windows 产品编译清单中。未扩展 Mesa、PuTTY 或其他组件范围。

## Windows 适配与实际修正

- xkbcomp：沿用文件枚举、调试内存分配、初始化、文件 ID 和 `-R` 不切换进程目录的适配。已进入上游的符号修复和 libc 映射不重复覆盖；保留 1.5.0 新增修复。修正 Windows makefile 长期写死的 1.2.3，使实际 CLI 报告 1.5.0。归档生成的 parser 移到 `upstream-generated/xkbparse.c` 原样留存，生产仍由本地 grammar 经 Bison 生成，避免绕过调试适配。
- xkbcomp：正常 US 键盘映射含 26 个类型，二进制对应字节 `0x1A`。旧程序以文本模式读 XKM，CRT 提前返回 EOF，命令虽退出 0，类型和符号却丢失。本轮以二进制模式探测文件和读取 XKM；XKB 文本和标准输入行为保留。测试要求 US 的 q/Q、德语第二组符号通过完整二进制往返。
- libXpm：同步公共头到官方内容；`XpmIncludeVersion=30411` 是沿用的 API 编号，新 3.5.19 也相同，不能用于判定发布包版本。保留指针宽度哈希转换，集中声明 MSVC fdopen 映射及 NO_ZPIPE；不恢复上游已删除的非产品 Amiga/FOR_MSW 支持文件。
- libXpm：旧 `XpmReadFileToBuffer` 用文本模式读含 CRLF 的正常文件，`fread` 得到 161 字节，`stat` 为 171，因而拒绝。验证仅将 fdopen 改为 rb 仍失败；本轮在 Windows 描述符 open 增加 `_O_BINARY`，并使用 rb，使文件长度和读取字节一致。
- zlib：保留 mhmake、八个 stdio 头适配和 DLL 导出方式，增加 1.3.2 的七个接口。MSVC POSIX 文件标志别名集中且有条件声明，覆盖排他创建和二进制模式；修正旧代码只转换部分 O_EXCL 条件、遗漏模式解析的情况。生产 DLL 的新接口、压缩、CRC、gzip 追加/排他/读取由实际调用检查。

`-R` 重复插入和 warningLevel 影响当前目录的旧逻辑、Windows wildcard listing 的旧限制已记录在独立审查中，本次未顺带重写，不宣称已解决。

## 验证记录

证据目录：`.local-validation/r8-20260915/`。含旧/新官方归档、继承源码、逐文件差异、基线测试、旧产物对照和三个独立审查记录。

构建前基线 410 项，46 项执行通过、364 项缺少产物跳过。新增 10 项实际消费者测试后，源码阶段 420 项，46 项执行通过、374 项跳过，8.802 秒；这不是完整产品通过。

旧 R7 对照确认版本、新接口、键盘往返、XPM 文件读取及 gzip 排他创建测试失败；原有二进制压缩和 CRC 向量通过。初次 XPM 测试链接遗漏真实 X11 导入库，补齐后验证到上述真实文件读取失败。测试清理也补上意外成功的 gzopen 句柄关闭，避免用临时目录清理错误遮盖根因。Xkbcomp 与 XPM 的独立探针确认失败边界，使用正常数据，没有恶意输入复现。

独立审查确认 xkbcomp 和 zlib 的全部原始/落盘摘要、补丁集合与实际源码一致，没有阻断项；XPM 审查在旧生产静态库上逐阶段验证了 CRLF 修正。

首次 `All -Jobs 16` 构建于 15:22:55–15:34:43 完成，退出 0，无编译失败恢复步骤。使用 VS2022/MSVC 19.44.35227、SDK 10.0.26100.0 和既有原生工具链，OpenSSL 阶段保持串行。开始时 HEAD 尚为基线，R8 修改未提交；`first-build-inputs.json` 的 29701 个源码/构建输入摘要在构建后复核未变。其后按组件提交，再运行提交后的 Server/Portable 阶段记录最终源码号，不能把环境报告里的基线号说成 R8 已提交源码。

新目录 R8 专项 10 项通过，0.284 秒；全量提交前回归 420 项通过、0 跳过，43.018 秒。旧对照同样 10 项，8 项测试方法失败（含子项共 10 个 failure）、2 项通过，0.333 秒。新旧对照均实际调用对应产物，测试没有改为跳过或放宽键盘符号断言。

上游 `test/example.c` 链接新生产 zlib 导入库并使用新 DLL，压缩、gzip 读写/定位、inflate、流同步和字典解压全部通过，退出 0。DLL 旧 87 个导出全部保留，新版共 96 个：七个显式新增接口，另有 upstream 自动导出的 `adler32_combine64` 与 `crc32_combine64`；未发现旧导出缺失。

四份 NSIS 声明和历史 mkzip 同步加入 xkbcomp、libXpm、zlib 的许可证和来源说明；NSIS 卸载声明也对应更新，但本轮未运行安装或卸载。Portable 使用其文件清单打包。

Git 索引首次复核发现继承 `.gitignore` 的 CRLF 落盘字节与旧索引 LF 不同；对三个组件执行受限路径的 `git add --renormalize` 后，全部原始归档、落盘文件、索引 blob 与路径大小写核对通过。

## 验证边界

本轮目标为完整 x64 Release；完整 Win32/Debug、NSIS 安装包、上游全部测试集和逐项安全公告复现不在本轮验证范围。人工启动、gitk、中文、重启仍需对本轮新目录反馈；传统字体、OpenGL、双向剪贴板等未确认场景不补记为通过。
