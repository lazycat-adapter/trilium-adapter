from pathlib import Path
import re
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
    assert manifest["services"]["trilium"]["image"] == "docker.io/triliumnext/trilium:v0.107.0"


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
