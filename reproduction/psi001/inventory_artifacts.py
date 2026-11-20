#!/usr/bin/env python3
"""Read-only SHA-256 inventory of a user-selected PSI-001 staging directory.

Does not upload files or assert that discovered files are the original experiment.
Review the JSON locally before publication: filenames can contain sensitive data.
"""
import argparse
import hashlib
import json
from pathlib import Path

def inventory(root: Path):
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("root must be a directory")
    records = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        h = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                h.update(block)
        records.append({"path": path.relative_to(root).as_posix(),
                        "bytes": path.stat().st_size, "sha256": h.hexdigest()})
    return {"project": "PSI-001", "gate": "05", "status": "inventory-only",
            "files": records, "file_count": len(records)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    target = args.output.resolve()
    source = args.directory.resolve(strict=True)
    if target == source or source in target.parents:
        parser.error("output must be outside the scanned directory to avoid self-inclusion")
    if target.exists():
        parser.error("refusing to overwrite existing inventory")
    result = inventory(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(f"Inventoried {result['file_count']} files. Review output before sharing.")
