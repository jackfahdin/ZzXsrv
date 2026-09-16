# R9.4 Fontconfig 2.18.3

日期：2026-09-16。基线 `74c102e780baa2d78a88c8933396c52106694818`；分支 `codex/r9-fontconfig-20260916`，独立工作区 `D:/File/Program/GitHub/zzxsrv-r9-fontconfig-20260916`。

状态：候选已完成完整产品验证，待人工验收；尚未合入、未推送。

## 来源与维护范围

从[Fontconfig 官方发布接口](https://gitlab.freedesktop.org/api/v4/projects/890/packages/generic/fontconfig/2.18.3/fontconfig-2.18.3.tar.xz)取得 2.18.3。SHA-256 为 `4f7b554a38cdf78c033f666c8871f3749e14a094f65a07f630c91ed0b43d35e3`，与同地址 `.sha256sum` 一致；未独立验证签名。1060 个普通文件全部导入，无符号链接。6 个上游文件保留明确适配，其余保持原始字节；另保留 45 个继承文件，1105 个源码/构建/附属文件的原始摘要见 `source-files.json`。补丁使用 LF，见 `patches/windows-adaptations.patch`。

旧目录声明 2.16.0，历史同步 SHA `25f58a52b0b30efbba0ea27c98dc58e411a42b84` 未独立证实。已取得官方 2.16.0 标签归档（标签落在 `127bb4dbfca7ba669eb40212ffcf24dd8f30351b`），用于区分继承适配与新版变化，不把继承目录描述成纯净上游版本。

保留静态 FreeType/libxml2 后端、TEMP 缓存默认值、已合入的 Windows 目录枚举/无效句柄修复、mkdir 宏处理、stat inode 宽度以及生成文件搜索路径。新增两个库源文件、常量和通用字体表生成规则，追加 93 个语言定义且保持前 246 项顺序。MSVC 启用本地 locale 格式化路径；gperf 输出与原型保持指针、长度类型一致。公开头由官方模板替换缓存版本参数生成，库及公开头均为 2.18.3。

新版缓存格式为 12，与旧格式 9 使用不同文件名；不启用兼容符号链接，不清理用户缓存。保留上游 50-user.conf 中旧用户配置可选路径。实际交付的 `fonts.src/fonts.conf` 保持原样。新增 Fontconfig COPYING、来源说明的交付声明，未执行 NSIS 安装卸载。

## 当前验证

- 新增 7 项真实静态库消费者检查：版本、非 C locale 下小数字号解析/回写、常量反查、通用字体属性往返、显式配置默认值、正常 CFF 字体的已知名称分类，以及两个旧用户配置路径。最终旧 2.16.0 库对照中 1 项通过、6 项失败，0.449 秒；新版组件的 7 种模式通过。旧版新 API 缺失属于升级差异，不作为旧版故障。分类夹具仍为原创矩形轮廓，仅将 family 设成已知表项 Consolas；默认夹具内容摘要不变。
- 原有 Windows 目录枚举 7 项通过，0.152 秒，无目录 API mock。
- 组件构建成功；仅在这一步借用 R9.3 未变的 libxml2 生成头，初步消费者使用 R9.3 未变的依赖 DLL。最终完整构建和测试须使用本工作区全部产物，不能把组件结果当成产品结果。
- 现有 FreeType 缓存消费者增加格式 12、缓存内按位编码的 2.18.3 版本和重载不改写缓存的断言。独立进程已实际验证旧格式 9 和新格式 12 缓存共存；两种路径拼写各有缓存，两个正常字体各出现一次，旧缓存字节不变。最终会使用完整本工作区依赖重跑。

## 完整候选验证

- 完整 x64 Release All 构建：来源 `6b2f8aecfefd52bd18dee3e95e754309cab6d38e`，2026-09-16 14:04 至 14:16 完成，退出码 0，环境报告与结果见 `build-all-result.json`、`environment-all.json`。
- 全量回归 449 项通过、0 跳过（49.814 秒，`tests-final.log`）；Fontconfig 静态库消费者 7 项通过（0.604 秒，头与库版本均为 21803，`tests-fontconfig-final.log`）。两套日志均为候选定稿后重跑。
- 候选独立运行检查 PASS（1.259 秒，`runtime/result.json`）；旧格式 9 缓存保留、格式 12 缓存重载不改写（`cache-coexist-final/result.json`）。
- 交付目录 5152 个文件、33 个 PE；`vcxsrv.exe` 与构建输出逐字节一致，Fontconfig COPYING 与 README.vcxsrv.md 交付摘要匹配；完整快照见 `portable-files.json`。
- 37 个继承签出的 CRLF 记录已修正并提交 `f3b110522`，与 `source-files.json` 清单逐字节一致；验证期间主仓库保持 `74c102e78`，R9.3 运行目录摘要不变。

## 证据与边界

本地证据位于 `.local-validation/r9-fontconfig-20260916/`，包括官方归档/校验、旧标签对照、继承文件备份、组件构建、红绿日志及独立审查；完整候选结果汇总于 `verification.json`。

验证目标为 x64 Release；全部上游测试、Win32、Debug、Fontations、NSIS 执行不在通过范围。传统字体、OpenGL、双向复制等此前未确认的手工场景继续保留。旧运行目录、主分支和既有缓存均不作清理。
