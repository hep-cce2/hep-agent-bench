"""Check a baseline tree against Git blob hashes (spec: grading.md, "Baseline integrity").

usage: python -m hepbench.snapshot verify --root DIR --manifest source-manifest.json
       python -m hepbench.snapshot export --root DIR --manifest source-manifest.json --dest NEW_DIR
       python -m hepbench.snapshot create --repo GIT_CHECKOUT [--upstream URL] > source-manifest.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def verify(root, manifest_path) -> list:
    """Return a list of problems; empty means every manifest file is present and unchanged."""
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    failures = []
    for item in manifest["files"]:
        path = Path(root) / item["path"]
        if not path.is_file():
            failures.append(f"missing: {item['path']}")
            continue
        actual = git_blob_sha(path.read_bytes())
        if actual != item["blob_sha"]:
            failures.append(f"changed: {item['path']} ({actual} != {item['blob_sha']})")
    return failures


def export(root, manifest_path, dest) -> list:
    """Verify, then copy only the manifest files into dest, so builds never see leftovers
    (old build/ trees, extra files) in root. Returns verify's problems; copies nothing if any."""
    failures = verify(root, manifest_path)
    if failures:
        return failures
    for item in json.loads(Path(manifest_path).read_text(encoding="utf-8"))["files"]:
        target = Path(dest) / item["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(Path(root) / item["path"], target)
    return []


def create(repo, upstream: str = "") -> dict:
    """Manifest of every tracked file at HEAD of a git checkout."""
    git = ["git", "-C", str(repo)]
    commit = subprocess.check_output(git + ["rev-parse", "HEAD"], text=True).strip()
    files = []
    for line in subprocess.check_output(git + ["ls-tree", "-r", "HEAD"], text=True).splitlines():
        meta, path = line.split("\t", 1)
        mode, kind, sha = meta.split()
        if kind == "blob":
            files.append({"path": path, "mode": mode, "blob_sha": sha})
    return {"schema_version": "1.0.0", "upstream_repository": upstream, "upstream_commit": commit, "files": files}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m hepbench.snapshot")
    sub = parser.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("verify")
    v.add_argument("--root", type=Path, required=True)
    v.add_argument("--manifest", type=Path, required=True)
    e = sub.add_parser("export")
    e.add_argument("--root", type=Path, required=True)
    e.add_argument("--manifest", type=Path, required=True)
    e.add_argument("--dest", type=Path, required=True)
    c = sub.add_parser("create")
    c.add_argument("--repo", type=Path, required=True)
    c.add_argument("--upstream", default="")
    args = parser.parse_args(argv)

    if args.cmd == "create":
        print(json.dumps(create(args.repo, args.upstream), indent=2))
        return 0
    if args.cmd == "export":
        failures = export(args.root, args.manifest, args.dest)
    else:
        failures = verify(args.root, args.manifest)
    if failures:
        print("Snapshot verification failed:")
        print("\n".join(f"  {line}" for line in failures))
        return 1
    print(f"Verified {args.root} against {args.manifest}" + (f"; exported to {args.dest}." if args.cmd == "export" else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
