# Trilium LazyCat 适配器设计

## 目标

为 `TriliumNext/Trilium` 的稳定 GitHub Release 创建 `peter.lazycat.app.trilium` 适配器，跟踪稳定 `vX.Y.Z` 标签，使用官方 `triliumnext/trilium:{tag}` 镜像，并生成可以在 LazyCat 上运行的 LPK。笔记数据库、附件、配置和索引持久化在 `/lzcapp/var/trilium`。

## 范围

- 监控 `https://github.com/TriliumNext/Trilium.git` 的稳定 semver 标签。
- 用 `triliumnext/trilium:{tag}` 作为唯一运行时镜像，保留 Git 标签中的 `v` 前缀。
- 应用入口使用 `trilium` 子域名，服务监听 8080。
- 为文件导入、附件和下载加入 LazyCat 文件选择器拦截资源。
- 生成 amd64 目标 LPK，明确不支持 Android 和 iOS 启动平台。
- 提供中文和英文应用描述，并保留上游 AGPL-3.0 许可说明。

## 非目标

- 不把 `in.zhaoj.trilium` 改造成该新包名的原地升级。
- 不修改 Trilium 上游源码，不构建自定义应用镜像。
- 不跟踪 `main`、nightly、RC、beta 或 Docker `latest` 标签。

## 实现方案

采用现有 `lazycat-action` 适配器模板。`lazycat-action.yml` 使用 `semver-tag` 和 `github-release`，镜像源使用 `docker.io/triliumnext/trilium:{tag}`。`lzc-manifest.yml` 将 8080 路由到 Trilium 服务，并把 `/lzcapp/var/trilium` 映射至上游默认数据目录 `/home/node/trilium-data`。由于新包名与参考应用的包名不同，应用商店会将其视为新应用，旧包的数据不会自动迁移。

## 验收标准

- 静态契约测试通过，且拒绝 `latest`、分支和预发布标签。
- `lzc-cli project build` 成功生成 `/opt/test/peter.lazycat.app.trilium-v0.107.0.lpk`。
- LPK 内包含 512×512 PNG 图标、包名、版本、服务路由、持久化绑定和文件选择器注入资源。
