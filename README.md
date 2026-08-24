# ZzXsrv

ZzXsrv 是 [VcXsrv](https://github.com/marchaesen/vcxsrv) 的 fork，作为
[ZzClawTerm](https://github.com/jackfahdin/ZzClawTerm) 的嵌入式 X server
组件维护。上游原始 README 见 [README.upstream.md](README.upstream.md)，
许可与差异声明见 [NOTICE](NOTICE)。

## 与上游的差异

1. **xtrans 默认仅绑定回环地址**——默认只监听 127.0.0.1/::1；
   设置环境变量 `ZZXSRV_LISTEN_ANY=1` 恢复全网卡监听（仅限隔离调试）。
2. **新增 `-parent <HWND>` 启动参数**——rootful 窗口可嵌入外部容器
   （供 Qt 侧嵌入使用，窗口类名约定为 `ZzXsrv/x`）。
3. **裁剪**——mesa 软渲染 OpenGL（swrast_dri/swrastwgl_dri/dxtn）、
   xlaunch、apps/*（xcalc/xclock/xwininfo/xhost/xrdb/xauth）、plink、
   Xv/XDMCP/record 已移出构建图，只保留 xkbcomp。
4. **品牌化**——产物为 `ZzXsrv.exe`，安装包为
   `zzxsrv-64.<版本>.installer[.noadmin].exe`。

## 构建

本仓库不维护本地构建说明的 fork 副本，构建走 GitHub Actions CI
（`.github/workflows/build.yml`，windows-2022 + WSL + mhmake 原链）：

- push 到 `master`：完整构建 + 产物核验 + 冒烟断言（监听地址行为）。
- 打 `zz-*` tag：额外产出 SHA256 并发布 GitHub Release。

## 发布物

- `zzxsrv-64.<版本>.installer.exe`：管理员安装包（装到 Program Files）。
- `zzxsrv-64.<版本>.installer.noadmin.exe`：免管理员安装包
  （装到 `C:\ZzXsrv`，当前用户上下文）。
- 各安装包附带 `.sha256` 校验文件。

tools/mhmake 为 GPLv3，仅构建期使用，不随产品分发。
