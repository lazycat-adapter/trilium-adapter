# Trilium Passwordless Login Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add official LazyCat inject-based first-run password setup, automatic login, and persisted password changes to the Trilium adapter.

**Architecture:** Keep the upstream Trilium image unchanged. Add request/response injects that capture only successful password operations and three built-in browser injects for the two setup fields and the password-only login page. Preserve the existing health, public path, and file-picker injects.

**Tech Stack:** LazyCat `lzc-manifest.yml` injects, YAML package metadata, Python `unittest`, Node.js smoke tests, `lzc-cli`.

**Spec:** `docs/superpowers/specs/2026-11-26-trilium-passwordless-login-design.md`

## Global Constraints

- Trilium is single-user; do not describe or inject an `admin` username.
- Default password is exactly `123456`.
- Persist only successful credentials, keyed by `trilium.password`.
- Keep `public_path: /_lzc/health` and the existing file-picker bridge/browser injects.
- Final runtime image must remain under `registry.lazycat.cloud`.

## Review Focus

- First-run form has two password fields and must submit only after both are filled — covered by manifest selector assertions.
- Login has a password-only field — covered by the login inject assertion.
- Failed login or password-change responses must not overwrite the saved password — covered by the Node smoke test.
- JSON and form-encoded request bodies use different parsers — covered by endpoint-specific smoke inputs.
- Existing file-picker/public-path injects must survive YAML edits — covered by the existing Trilium contract and LPK lint.

### Task 1: Add failing passwordless contract coverage

**Files:**
- Modify: `tests/test_contract.py`

- [ ] **Step 1: Add assertions for single-user usage, default `123456`, endpoint coverage, and the three browser selectors.**
- [ ] **Step 2: Add a Node smoke test that executes the request/response scripts for failed and successful setup/login/password-change responses.**
- [ ] **Step 3: Run the focused test and confirm it fails against the current manifest.**

### Task 2: Implement injects and usage metadata

**Files:**
- Modify: `lzc-manifest.yml`
- Modify: `package.yml`

- [ ] **Step 1: Add request/response capture and commit injects for `/set-password`, `/login`, and `/api/password/change`.**
- [ ] **Step 2: Add browser injects for `password1`, `password2`, and `password`, using `$persist: trilium.password`, default `123456`, and `requestSubmit` auto-submit.**
- [ ] **Step 3: Replace username-oriented usage text with the single-user/password-only wording in both locales.**
- [ ] **Step 4: Run the focused contract and smoke tests and confirm they pass.**

### Task 3: Build and package verification

**Files:**
- Generated: `dist/peter.lazycat.app.trilium-v0.107.1.lpk`

- [ ] **Step 1: Run `python3 -B scripts/verify_package.py`.**
- [ ] **Step 2: Run `lzc-cli project lint .` and `lzc-cli project build .`.**
- [ ] **Step 3: Run `lzc-cli lpk lint` on the generated LPK and inspect its manifest for the official image, public path, file bridge, and password injects.**
- [ ] **Step 4: Commit and push the adapter changes.**
