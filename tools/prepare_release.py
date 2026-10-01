"""Package v0.3.16 using a separate Retro Trans checkout. Dry run unless --write.

This helper builds local release assets only. It never pushes or changes visibility.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.16"
EXPECTED_SOURCE = "c3bd8c1af4e411e5ab2ae2d4be877170b6ab1ea9b51fa62bc0b91a51ba1a2952"
EXPECTED_TARGET = "38199a3be48e759e2b887c369609b404afe9376a6f28a91d02036bfca914f5a7"

def digest(path, algo):
    h = hashlib.new(algo)
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--retro-trans", type=Path, required=True)
    parser.add_argument("--source", type=Path, default=ROOT / "work/source/special-disc.bin")
    parser.add_argument("--target", type=Path, default=ROOT / f"work/output/SRW Z Special Disc English v{VERSION}.iso")
    parser.add_argument("--out", type=Path, default=ROOT / f"work/output/release-v{VERSION}")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    for path in (args.source, args.target, args.retro_trans / "retro_trans/release.py"):
        if not path.is_file():
            raise ValueError(f"Missing required local file: {path}")
    if args.out.exists():
        raise ValueError("Use a new release directory; never overwrite an existing package.")
    print(f"{'Building' if args.write else 'Dry run:'} v{VERSION}, clean Japanese Special Disc -> English ISO", flush=True)
    print("Assets: xdelta, manifest, validation, checksums, README and changelog", flush=True)
    if not args.write:
        return
    git = ["git", "-c", f"safe.directory={ROOT.as_posix()}"]
    if subprocess.check_output(git + ["status", "--porcelain"], cwd=ROOT).strip():
        raise ValueError("Commit the publication source before packaging.")
    commit = subprocess.check_output(git + ["rev-parse", "HEAD"], cwd=ROOT).decode().strip()
    sys.path.insert(0, str(args.retro_trans.resolve()))
    from retro_trans.release import build_release, validate_directory
    from retro_trans.catalog import atomic_json
    for path, expected in ((args.source, EXPECTED_SOURCE), (args.target, EXPECTED_TARGET)):
        if digest(path, "sha256") != expected:
            raise ValueError("Input does not match the verified v0.3.16 source/target identity")
    private = ROOT / "work/cache/publication"
    private.mkdir(parents=True, exist_ok=True)
    config = {"game_id": "srw-z-special-disc", "game_name": "Super Robot Taisen Z Special Disc",
              "platform": "PS2", "version": VERSION, "source_commit": commit, "patches": [{
              "patch": f"SRWZ-SP-English-v{VERSION}.xdelta", "edition": "Japan (SLPS-25920)",
              "language": "en", "source_version": "original", "source_format": "iso", "target_format": "iso",
              "source": str(args.source.resolve()), "target": str(args.target.resolve())}]}
    config_path = private / "release-local.json"
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    manifest = build_release(config_path, args.out, cache=private / "runtime")
    manifest["patches"][0]["source_sha1"] = digest(args.source, "sha1")
    manifest["patches"][0]["target_sha1"] = digest(args.target, "sha1")
    atomic_json(args.out / "BUILD-MANIFEST.json", manifest)
    validation = json.loads((args.out / "VALIDATION.json").read_text(encoding="utf-8"))
    validation["manifest_sha256"] = digest(args.out / "BUILD-MANIFEST.json", "sha256")
    atomic_json(args.out / "VALIDATION.json", validation)
    for original, name in (("README.md", f"README-v{VERSION}.txt"), ("CHANGELOG.md", f"CHANGELOG-v{VERSION}.txt")):
        (args.out / name).write_bytes((ROOT / original).read_bytes())
    # Catalog ingestion fetches only these core files before validation.
    core_names = {"BUILD-MANIFEST.json", "VALIDATION.json"} | {p["patch"] for p in manifest["patches"]}
    sums = [f"{digest(args.out / name, 'sha256')}  {name}" for name in sorted(core_names)]
    (args.out / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="utf-8")
    validate_directory(args.out)
    print("Official build, exact reconstruction and final package validation passed.", flush=True)
    print(json.dumps(manifest, indent=2), flush=True)

if __name__ == "__main__":
    main()
