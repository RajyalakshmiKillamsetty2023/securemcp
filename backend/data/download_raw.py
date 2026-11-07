"""Download raw datasets into backend/data/raw/ and write a hash manifest.

Usage (from backend/):  python data/download_raw.py [--only mcptox|bfcl|msb]

Licences are recorded in docs/decisions.md (D3). Raw files are gitignored; only
raw_manifest.json (names, sizes, sha256) is committed.
"""
import argparse
import hashlib
import json
import shutil
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
RAW = HERE / "raw"
MANIFEST = HERE / "raw_manifest.json"

MCPTOX_BASE = "https://raw.githubusercontent.com/zhiqiangwang4/MCPTox-Benchmark/main/"
MCPTOX_FILES = ["pure_tool.json", "response_all.json"]  # ~0.3 MB and ~20 MB

BFCL_REPO = "gorilla-llm/Berkeley-Function-Calling-Leaderboard"
BFCL_PATTERNS = ["BFCL_v3_simple.json", "BFCL_v3_multiple.json",
                 "BFCL_v3_live_simple.json", "BFCL_v3_live_multiple.json", "README.md"]

MSB_REPO = "DongsenZhang/MSB"
# Top-level data files only. data/tools/ is deliberately excluded (see decisions.md D3).
MSB_PATTERNS = ["data/*.jsonl", "data/*.json", "README.md"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def get_mcptox():
    out = RAW / "mcptox"
    out.mkdir(parents=True, exist_ok=True)
    for name in MCPTOX_FILES:
        dest = out / name
        if not dest.exists():
            print("downloading", name)
            urllib.request.urlretrieve(MCPTOX_BASE + name, dest)
    return out


def get_hf(repo: str, patterns: list[str], sub: str, ignore: list[str] | None = None):
    from huggingface_hub import snapshot_download  # installed with the [ml] extra

    out = RAW / sub
    snapshot_download(repo_id=repo, repo_type="dataset", allow_patterns=patterns,
                      ignore_patterns=ignore, local_dir=out)
    return out


def write_manifest():
    files = {}
    for p in sorted(RAW.rglob("*")):
        if p.is_file() and ".cache" not in p.parts:
            files[str(p.relative_to(RAW)).replace("\\", "/")] = {
                "bytes": p.stat().st_size, "sha256": sha256(p)}
    MANIFEST.write_text(json.dumps(files, indent=2))
    print(f"manifest: {len(files)} files -> {MANIFEST.name}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["mcptox", "bfcl", "msb"])
    args = ap.parse_args()
    if args.only in (None, "mcptox"):
        get_mcptox()
    if args.only in (None, "bfcl"):
        get_hf(BFCL_REPO, BFCL_PATTERNS, "bfcl")
    if args.only in (None, "msb"):
        out = get_hf(MSB_REPO, MSB_PATTERNS, "msb", ignore=["data/tools/*"])
        # fnmatch's * also matches "/", so allow patterns can pull in nested folders:
        # remove data/tools/ explicitly (server launch configs; see decisions.md D3).
        shutil.rmtree(out / "data" / "tools", ignore_errors=True)
    write_manifest()
