from pathlib import Path
import json
import re
import subprocess
import yaml

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    return yaml.safe_load((ROOT / name).read_text())


def test_package_contract():
    package = load("package.yml")
    assert package["package"] == "peter.lazycat.app.trilium"
    # The shared action may persist a patch increment after a successful
    # submission, so the generated checkout can be 0.107.1 or newer.
    package_version = tuple(int(part) for part in package["version"].split("."))
    assert package_version >= (0, 107, 0)
    assert package["homepage"] == "https://triliumnotes.org"
    assert {"android", "ios"}.issubset(set(package["unsupported_platforms"]))
    assert package["locales"]["zh-CN"]["name"] == "Trilium Notes"
    assert package["locales"]["en-US"]["name"] == "Trilium Notes"


def test_source_tracks_stable_trilium_releases():
    config = load("lazycat-action.yml")
    assert config["source"]["url"] == "https://github.com/TriliumNext/Trilium.git"
    assert config["source"]["select"]["strategy"] == "semver-tag"
    pattern = re.compile(config["source"]["select"]["tag_regex"])
    assert pattern.fullmatch("v0.107.0")
    assert not pattern.fullmatch("v0.108.0-rc.1")
    assert not pattern.fullmatch("nightly")


def test_image_and_manifest_preserve_data_and_service_contract():
    config = load("lazycat-action.yml")
    image = config["images"][0]
    assert image["service"] == "trilium"
    assert image["source"] == "docker.io/triliumnext/trilium:{tag}"
    assert "latest" not in image["source"]

    manifest = load("lzc-manifest.yml")
    assert manifest["application"]["subdomain"] == "trilium"
    assert manifest["application"]["routes"] == ["/=http://trilium:8080"]
    assert manifest["services"]["trilium"]["binds"] == [
        "/lzcapp/var/trilium:/home/node/trilium-data"
    ]
    assert manifest["services"]["trilium"]["image"].startswith("registry.lazycat.cloud/")
    assert "docker.io/triliumnext/trilium:v0.107.0" in (ROOT / "lzc-manifest.yml").read_text()


def test_file_picker_injection_is_packaged():
    manifest = load("lzc-manifest.yml")
    assert manifest["application"]["public_path"] == ["/_lzc/health"]
    injects = manifest["application"]["injects"]
    bridge = next(item for item in injects if item["id"] == "lazycat-file-bridge")
    assert bridge["on"] == "request"
    assert bridge["when"] == ["/__lazycat_file_bridge/*"]
    assert "ctx.proxy.to" in bridge["do"][0]["src"]
    browser_inject = next(item for item in injects if item["id"] == "open-save-chooser")
    assert browser_inject["on"] == "browser"
    assert browser_inject["do"][0]["src"].startswith("file:///lzcapp/pkg/content/")
    assert (ROOT / "content/lazycat-injects/lzc-file-chooser-inject.js").is_file()


def test_icon_is_store_ready():
    from PIL import Image

    image = Image.open(ROOT / "icon.png")
    assert image.size == (512, 512)
    assert image.format == "PNG"


def test_passwordless_login_contract_and_state_transitions():
    package = load("package.yml")
    usage = "\n".join([
        package["locales"]["zh-CN"]["usage"],
        package["locales"]["en-US"]["usage"],
    ]).lower()
    assert "123456" in usage
    assert "单用户" in usage
    assert "single-user" in usage

    manifest = load("lzc-manifest.yml")
    injects = manifest["application"]["injects"]
    by_id = {item["id"]: item for item in injects}

    capture = by_id["trilium-capture-password"]
    commit = by_id["trilium-commit-password"]
    assert capture["on"] == "request"
    assert commit["on"] == "response"
    assert {"/set-password", "/login", "/api/password/change"}.issubset(set(capture["when"]))
    assert {"/set-password", "/login", "/api/password/change"}.issubset(set(commit["when"]))

    for inject_id, selector in (
        ("trilium-setup-password1", 'input[name="password1"]'),
        ("trilium-setup-password2", 'input[name="password2"]'),
        ("trilium-login-autofill", 'input[name="password"]'),
    ):
        inject = by_id[inject_id]
        assert inject["on"] == "browser"
        script = inject["do"][0]
        assert script["src"] == "builtin://simple-inject-password"
        params = script["params"]
        assert params["password"] == {"$persist": "trilium.password", "default": "123456"}
        assert params["passwordSelector"] == selector
        assert params["autoSubmit"] is (inject_id != "trilium-setup-password1")

    request_script = capture["do"]
    response_script = commit["do"]
    assert isinstance(request_script, str)
    assert isinstance(response_script, str)
    node_program = r'''
const assert = require("node:assert/strict");
const scripts = JSON.parse(require("node:fs").readFileSync(0, "utf8"));
const capture = new Function("ctx", scripts.request);
const commit = new Function("ctx", scripts.response);
const flow = new Map();
const persist = new Map();
const form = (values) => Object.fromEntries(Object.entries(values).map(([key, value]) => [key, [value]]));
const ctx = {
  flow,
  persist,
  request: { path: "/set-password", method: "POST" },
  body: { getForm: () => form({ password1: "123456", password2: "123456" }), getJSON: () => ({}) },
  status: 302,
  headers: { get: () => "" },
};
capture(ctx); commit(ctx);
assert.equal(persist.get("trilium.password"), "123456");

ctx.request.path = "/login";
ctx.body.getForm = () => form({ password: "wrong" });
ctx.status = 401;
capture(ctx); commit(ctx);
assert.equal(persist.get("trilium.password"), "123456");

ctx.status = 302;
capture(ctx); commit(ctx);
assert.equal(persist.get("trilium.password"), "wrong");

ctx.request.path = "/api/password/change";
ctx.body.getJSON = () => ({ new_password: "new-secret" });
ctx.status = 400;
capture(ctx); commit(ctx);
assert.equal(persist.get("trilium.password"), "wrong");

ctx.status = 200;
capture(ctx); commit(ctx);
assert.equal(persist.get("trilium.password"), "new-secret");
'''
    subprocess.run(
        ["node", "-e", node_program],
        input=json.dumps({"request": request_script, "response": response_script}),
        text=True,
        check=True,
    )
