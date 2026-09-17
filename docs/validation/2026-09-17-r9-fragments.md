# R9.9 嵌套片段归属澄清

日期：2026-09-17。基线 `077377e17d`；分支 `codex/r9-fragments-20260917`，独立工作区 `D:/File/Program/GitHub/zzxsrv-r9-fragments-20260917`。

状态：候选待验收。本轮为纯来源归属核查：对 SOURCES 清单中 7 个"未知 / 未固定"的嵌套片段逐一以上游证据澄清归属，全部得到确定性结论；仅更新 `docs/dependencies/SOURCES.md` 与 `SOURCES.json` 对应条目，未修改任何产品代码。纯文档改动不改变构建输入，dist 产物与合入点无关，无需重建；验收后快进合入即可。

## 结论汇总

| 片段 | 原状态 | 核查结论 | 验证方式 |
| --- | --- | --- | --- |
| `third_party/libregex` | 未知 | **gnulib 提交窗口 `1276a2c5f24c`..`8c7f2f9de84e`（2014-01-01..03-05）**；直接来源是 gnulib 而非 glibc（glibc 2.5–2.36 全部 tag 已排除）。5 个文件与窗口内逐字节一致；regex.c 仅删一行 `# include <config.h>`、regex.h 仅删一空行；langinfo.h 由 gnulib 模板手工展开 | gnulib 全历史 blob SHA-1 扫描（51 个提交窗口均满足） |
| `src/platform/libwinmain` | 未知 | **VcXsrv/marha 项目原创，无第三方上游**；2009-08-07 首次写入 xlaunch，2009-11-05 `17cd2280a71d` 抽为独立库；PuTTY 上游不含 WinMain，已排除。本地与上游逐字节一致 | VcXsrv 完整提交历史 + PuTTY 各版本比对 + SHA-256 |
| `third_party/graphics/dxtn` | 未知 | **libtxc_dxtn 20070518 dated 快照（0.1 线末端，非 1.0/1.0.1）**，经 O3D trunk 转引；6/7 文件与 O3D 最终态逐字节一致，`txc_compress_dxtn.c` 含 VcXsrv 本地补丁 2 行 | 与 nobled/libtxc_dxtn、petersont/o3d、deb-multimedia 1.0.1 比对（1.0.1 已排除） |
| `dxtn/base`、`dxtn/build`（Chrome 头 via O3D） | 未知 | 与 O3D trunk 最终 vendored 副本**逐字节一致**；具体 Chromium 版本不可考 | petersont/o3d 比对 |
| `include/dirent.h` | 未知 | **Toni Ronkko dirent 1.10（2010-08-11）** + 3 处本地补丁（PATH_MAX、空白、尾部自增 scandir/alphasort 约 83 行）；GitHub 历史（2015 年起）无此版本属预期 | Wayback 官方 dirent-1.10.zip 比对；GitHub 179 提交全扫描 |
| `include/inttypes.h`、`include/stdint.h` | 未知 | **msinttypes r26（2009-10-02）**；inttypes.h 与官方 r26 zip 逐字节一致；stdint.h 基于 r26 含 3 处本地补丁（30 个 diff 行） | 官方 r26 zip + GitHub 镜像 27 提交全扫描 |
| `include/xcb` utility 头 | 未知 | 逐文件定位：**xcb-util 0.4.1（aux）、xcb-util-image 0.4.1（image）、xcb-util-wm 0.4.2（icccm，内容 0.3.9–0.4.2 相同）；ewmh 为 m4 生成头（0.4.0–0.4.2 产物相同）**；errors/windefs 与仓库内已单列副本逐字节一致 | 上游全 tag blob 扫描 + Debian 安装头 SHA-256 比对 |
| `third_party/zlib` | 声明 1.3，未证实（**条目已过期**） | R8 实际已导入 **1.3.2**；复核：254 文件中 243 个与官方 `zlib-1.3.2.tar.gz`（SHA-256 `bb329a0a…9d16`）逐字节一致，11 个改动由 `patches/windows.patch` 干净复现 | 官方归档下载校验 + 全树哈希比对 + 补丁复现 |

## 说明

- zlib 的 SOURCES.md 条目此前仍写 1.3（R8 导入 1.3.2 后未同步），本轮一并修正；SOURCES.json 的 zlib 条目在 R8 已正确，无需改动。
- 每项结论都区分了"逐字节验证一致"与"版本声明一致"；dxtn 的 O3D SVN revision、Chrome 头的具体 Chromium 版本因上游服务下线不可考，按"内容等同最终态"如实记录，未拔高。
- include/X11、include/gl 混合头集合与 mesalib 内嵌片段（DRM UAPI、Fuchsia radix sort、gfxstream、Khronos registry 副本等）不在本轮范围，维持原登记。

## 证据与范围

证据目录 `.local-validation/r9-fragments-20260917/`（git 忽略、不入库），按片段分 7 个子目录：libregex/（gnulib 部分克隆与扫描记录）、libwinmain/（VcXsrv 提交历史与 PuTTY 排除证据）、dxtn/（o3d 镜像稀疏检出、nobled 导入镜像、被排除的 1.0.1 归档）、dirent/（v1.10 zip、GitHub 全历史比对）、msinttypes/（r26 官方 zip 与镜像克隆）、zlib-verify/（官方归档与补丁复现记录）、xcb-util-headers/（三个上游仓库全量克隆与 Debian 包头）。

本轮范围为来源归属核查与清单更新：无产品代码改动，构建与回归不适用。

## 下一步

候选交付维护者验收。本轮收官 R9 嵌套片段归属澄清；验收后 R9 系列全部完成。
