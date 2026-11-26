# Trilium Passwordless Login Design

## Intent

Make the Trilium LazyCat adapter remember the password selected during first-run setup and use it for subsequent login while preserving Trilium's own password-change flow. Trilium is a single-user application, so the adapter must not invent a username field or claim that an `admin` account exists.

## Goals

- The first-run `password1`/`password2` form remains user-controlled.
- After a successful first-run setup, the chosen password is persisted.
- The normal `password` login form is filled and submitted automatically when a saved password exists.
- Successful `/set-password`, `/login`, and `/api/password/change` requests update a per-user persisted password.
- Existing `public_path` and file-picker request/browser injects remain unchanged.

## Non-goals

- No changes to the upstream Trilium image or its database schema.
- No fake `admin` username; Trilium's server authentication is password-only.
- No disabling of Trilium authentication.

## Approach

Use LazyCat's built-in `simple-inject-password` browser inject only for the normal login field. Use request/response injects with `ctx.flow` and `ctx.persist` to remember only credentials accepted by Trilium. Form-encoded setup/login requests use `ctx.body.getForm`; JSON password changes use `ctx.body.getJSON`.

## Verification

Static contract tests will assert the single-user wording, the three browser inject selectors/defaults, and the request/response endpoint coverage. A Node smoke test will execute the request/response scripts to prove failed credentials are not persisted while successful setup, login, and password-change responses are.
