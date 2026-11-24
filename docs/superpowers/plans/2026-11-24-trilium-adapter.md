# Trilium LazyCat 适配器 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a new `peter.lazycat.app.trilium` adapter for the stable TriliumNext Docker image and produce a validated LPK.

**Architecture:** Reuse the shared `lazycat-adapter/lazycat-action@v1` workflow. The adapter selects stable upstream Git tags, maps the matching `triliumnext/trilium:{tag}` image to one LazyCat service, and keeps application data in `/lzcapp/var/trilium`. The package is a new app listing and has no `in.zhaoj.trilium` migration contract.

**Tech Stack:** YAML package and manifest, GitHub Actions reusable workflow, Python/PyYAML contract tests, `lzc-cli 2.0.9`, official Trilium PNG icon.

**Spec:** `docs/superpowers/specs/2026-11-24-trilium-adapter-design.md`

## Global Constraints

- Package ID is `peter.lazycat.app.trilium`.
- Initial upstream and package version is `0.107.0`.
- Source tags match stable `^v[0-9]+\.[0-9]+\.[0-9]+$` only.
- Runtime image is `docker.io/triliumnext/trilium:{tag}`.
- Persistent bind is `/lzcapp/var/trilium:/home/node/trilium-data`.
- Service and application subdomain are `trilium`, port `8080`.
- Target architecture is amd64 and unsupported launcher platforms are Android and iOS.
- The workflow uses `secrets: inherit` and the floating shared action `@v1`.

## Review Focus

- A prerelease tag must not be selected. Test in `test_source_tracks_stable_trilium_releases`.
- A mutable `latest` image must not be selected. Test in `test_image_and_manifest_preserve_data_and_service_contract`.
- A package rename must not imply old-app migration. Pin the new package ID and document it in the spec.
- The upstream data directory must remain persistent. Test the exact bind path.
- File chooser interception and icon assets must be present in the LPK context. Test both manifest injection and PNG dimensions.

### Task 1: Define package and source metadata

**Files:**
- Modify: `package.yml`
- Modify: `lazycat-action.yml`
- Modify: `lzc-build.yml`
- Modify: `.github/workflows/update.yml`

- [ ] Write and run the contract tests first.
- [ ] Set package metadata, locale descriptions, permissions, version `0.107.0`, and unsupported platforms.
- [ ] Configure stable GitHub tag selection, release changelog, official image template, and official store publishing.
- [ ] Use `secrets: inherit` in the reusable workflow.

### Task 2: Define the runtime manifest and assets

**Files:**
- Modify: `lzc-manifest.yml`
- Add: `content/lazycat-injects/lzc-file-chooser-inject.js`
- Modify: `icon.png`

- [ ] Write a manifest for the `trilium` service at port 8080 with the exact persistent bind.
- [ ] Add the browser file chooser injection resource and reference it from the manifest.
- [ ] Replace the placeholder icon with the upstream 512×512 PNG.
- [ ] Run the contract tests and `lzc-cli project build`.

### Task 3: Validate and publish the repository

**Files:**
- Add: `README.md` updates if required
- Add: `.gitignore` updates if required
- Add: `dist/peter.lazycat.app.trilium-v0.107.0.lpk` only outside Git via `.gitignore`

- [ ] Inspect the LPK manifest and file list.
- [ ] Copy the built LPK to `/opt/test/peter.lazycat.app.trilium-v0.107.0.lpk`.
- [ ] Create the public repository under `lazycat-adapter` if it does not exist.
- [ ] Commit and push the adapter after local verification.
