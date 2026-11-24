from pathlib import Path
import re
import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

def load(name):
    return yaml.safe_load((ROOT / name).read_text())

def main():
    package = load("package.yml")
    config = load("lazycat-action.yml")
    manifest = load("lzc-manifest.yml")
    assert package["package"] == "peter.lazycat.app.trilium"
    assert package["version"] == "0.107.0"
    assert {"android", "ios"}.issubset(set(package["unsupported_platforms"]))
    assert config["source"]["url"] == "https://github.com/TriliumNext/Trilium.git"
    assert config["source"]["select"]["strategy"] == "semver-tag"
    assert re.fullmatch(config["source"]["select"]["tag_regex"], "v0.107.0")
    assert config["images"][0]["source"] == "docker.io/triliumnext/trilium:{tag}"
    assert manifest["application"]["subdomain"] == "trilium"
    assert manifest["application"]["routes"] == ["/=http://trilium:8080"]
    assert manifest["services"]["trilium"]["binds"] == ["/lzcapp/var/trilium:/home/node/trilium-data"]
    assert (ROOT / "content/lazycat-injects/lzc-file-chooser-inject.js").is_file()
    image = Image.open(ROOT / "icon.png")
    assert image.size == (512, 512) and image.format == "PNG"
    print("Trilium adapter contract passed")

if __name__ == "__main__":
    main()
