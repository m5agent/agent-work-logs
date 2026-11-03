"""Validate downloaded host runtime/source closure; never starts an emulator."""
import hashlib
import json
from pathlib import Path
import runpy
import sys
import tarfile

def verify_members(archive, expected):
    seen = set()
    with tarfile.open(archive, "r|xz") as package:
        for member in package:
            if member.name not in expected:
                continue
            if member.name in seen or not member.isfile():
                raise ValueError("Duplicate or non-file source member: " + member.name)
            digest = hashlib.sha256()
            stream = package.extractfile(member)
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
            if digest.hexdigest() != expected[member.name]:
                raise ValueError("Actual archived source postimage mismatch: " + member.name)
            seen.add(member.name)
    if seen != set(expected):
        raise ValueError("Missing actual archived source postimages")
    return len(seen)

def main(repo, directory):
    repo, directory = Path(repo), Path(directory)
    builder = runpy.run_path(str(repo / "scripts/qemu-wasm-build/build.py"), run_name="pages_runtime_validator")
    manifest, _ = builder["runtime_files"](directory)
    lock = builder["load_lock"]()
    assert len(lock["patches"]) == 72 and len(lock["patched_files"]) == 160
    expected = {"qemu/" + path: digest for path, digest in lock["patched_files"].items()}
    expected.update({row["path"]: row["sha256"] for row in lock["patches"] + lock["dependency_patches"]})
    expected.update({"scripts/qemu-wasm-build/build.py": manifest["build"]["recipe_sha256"],
                     "scripts/qemu-wasm-build/sources.lock.json": manifest["build"]["lock_sha256"]})
    count = verify_members(directory / manifest["assets"]["source"]["path"], expected)
    return {"result": "PASS", "runtime_assets": 6, "actual_archived_members_verified": count,
            "actual_qemu_source_postimages": 160, "actual_ordered_patch_files": 72,
            "actual_dependency_patch_files": len(lock["dependency_patches"]),
            "source_archive_sha256": manifest["assets"]["source"]["sha256"],
            "source_lock_sha256": manifest["build"]["lock_sha256"],
            "source_build_all_objects_rebuilt": manifest["build"]["all_objects_rebuilt"],
            "guest_execution": "NOT RUN by this verifier"}

if __name__ == "__main__":
    print(json.dumps(main(*sys.argv[1:])))
