# Trilium Notes LazyCat 适配器

这个仓库为 `peter.lazycat.app.trilium` 生成 LazyCat 应用包，运行时使用 TriliumNext 官方的 `triliumnext/trilium` 镜像。

## 当前版本

- 上游仓库：<https://github.com/TriliumNext/Trilium>
- 稳定版本：`v0.107.0`
- 运行时镜像：`docker.io/triliumnext/trilium:v0.107.0`
- 数据目录：`/lzcapp/var/trilium`
- 应用域名：安装后由 LazyCat 分配，默认子域名为 `trilium`

## 数据和升级

这是新建的应用包，包名是 `peter.lazycat.app.trilium`。它与应用商店中的 `in.zhaoj.trilium` 是两个不同的应用，安装后不会自动迁移旧应用数据。

Trilium 容器内的数据目录是 `/home/node/trilium-data`，适配器将其持久化到 `/lzcapp/var/trilium`。后续同一包名的版本升级会沿用该目录。

## 本地构建

```bash
python3 scripts/verify_package.py
lzc-cli project build -o /opt/test/peter.lazycat.app.trilium-v0.107.0.lpk
```

本地构建会保留 Docker Hub 镜像引用。正式送审时，`lazycat-action` 会先将对应的官方镜像复制到 LazyCat 官方镜像仓库，再把 Manifest 中的镜像地址替换为复制后的地址。

## 自动更新

`.github/workflows/update.yml` 通过 `lazycat-adapter/lazycat-action@v1` 每天检查稳定的 `vX.Y.Z` GitHub Release。组织级 `LZC_API_TOKEN` 通过 `secrets: inherit` 传入。手动运行时，取消 `dry-run` 才会执行镜像转存、LPK 构建和应用审核提交。
