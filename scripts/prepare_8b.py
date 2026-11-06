"""Prepare the 8B family for Phase II: download, convert to GGUF, quantize to Q6_K, hash. Windows, run once.

    python scripts/prepare_8b.py                 # all three models, resumable
    python scripts/prepare_8b.py --only qwen3-8b

Pre-registration §3: one quantization chain for the three files. No i1 file exists for all three, so each is converted
by us from its original BF16 weights with the converter of the same llama.cpp release as the server (b10786), then
quantized to Q6_K by that release's llama-quantize. The Hugging Face weights are kept (Phase III loads them in
PyTorch); the intermediate BF16 GGUF is deleted. Everything is recorded in docs/models.md.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LLAMA_BIN = Path(r"C:\llm\llamacpp")
LLAMA_SRC = Path(r"C:\llm\llama.cpp-src")          # git clone --branch b10786
HF_DIR = Path(r"C:\llm\hf")
OUT_DIR = Path(r"C:\llm\models")
BUILD = "10786"
QUANT = "Q6_K"

MODELS = [  # server name, Hugging Face repository, role
    ("qwen3-8b", "Qwen/Qwen3-8B", "original"),
    ("qwen3-8b-huihui", "huihui-ai/Huihui-Qwen3-8B-abliterated-v2", "abliterated (Huihui v2)"),
    ("qwen3-8b-mlabonne", "mlabonne/Qwen3-8B-abliterated", "abliterated (mlabonne)"),
]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def run(cmd: list[str]) -> str:
    print(" ", " ".join(str(c) for c in cmd), flush=True)
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-4000:])
        sys.exit(f"failed: {cmd[0]}")
    return r.stdout + r.stderr


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="server name of one model")
    args = ap.parse_args()
    from huggingface_hub import HfApi, snapshot_download

    conv = LLAMA_SRC / "convert_hf_to_gguf.py"
    if not conv.exists():
        sys.exit(f"converter not found: {conv}\n  git clone --depth 1 --branch b{BUILD} "
                 f"https://github.com/ggml-org/llama.cpp {LLAMA_SRC}")
    tag = run(["git", "-C", LLAMA_SRC, "describe", "--tags"]).strip()
    if tag != f"b{BUILD}":
        sys.exit(f"converter is {tag}, the server is b{BUILD}: clone the matching tag")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, repo, role in MODELS:
        if args.only and name != args.only:
            continue
        print(f"\n== {name}  ({repo})")
        rev = HfApi().model_info(repo).sha
        local = HF_DIR / repo.split("/")[1]
        snapshot_download(repo, revision=rev, local_dir=local)
        out = OUT_DIR / f"{repo.split('/')[1]}-{QUANT}.gguf"
        if not out.exists():
            bf16 = OUT_DIR / f"{repo.split('/')[1]}-BF16.tmp.gguf"
            if not bf16.exists():
                run([sys.executable, conv, local, "--outtype", "bf16", "--outfile", bf16])
            log = run([LLAMA_BIN / "llama-quantize.exe", bf16, out, QUANT])
            m = re.search(r"build = (\d+)", log)
            if m and m.group(1) != BUILD:
                print(f"  WARNING: llama-quantize build {m.group(1)}, server build {BUILD}")
            (out.with_suffix(".quantize.log")).write_text(log, encoding="utf-8")
            bf16.unlink()
        digest = sha256(out)
        print(f"  {out.name}  {digest}")
        rows.append(f"| `{name}` | {role} | [{repo}](https://huggingface.co/{repo}) at `{rev[:12]}` | "
                    f"`{out}` | `{digest}` |")
    if rows:
        md = ROOT / "docs" / "models.md"
        t = md.read_text(encoding="utf-8")
        head = ("| Server name | Role | Weights (revision) | File | SHA-256 |\n|---|---|---|---|---|\n")
        block = (f"Converted from BF16 with `convert_hf_to_gguf.py` of llama.cpp b{BUILD}, quantized to {QUANT} with "
                 f"`llama-quantize` of the same release ({date.today().isoformat()}).\n\n" + head + "\n".join(rows) + "\n")
        t = re.sub(r"To be added before the first 8B test run:.*?(?=\n\n|\Z)", lambda _: block.rstrip(), t, flags=re.S) \
            if "To be added before the first 8B test run" in t else t.rstrip() + "\n\n" + block
        md.write_text(t, encoding="utf-8")
        print(f"\nrecorded in {md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
