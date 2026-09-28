"""Audit staged/tracked files, not ignored private working data. Uses only stdlib."""
import ast
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = {".gitattributes", ".gitignore", "AGENTS.md", "BASE_RULES.md", "README.md", "CHANGELOG.md", "CONTRIBUTING.md", "THIRD_PARTY_NOTICES.md"}
ALLOWED_SUFFIXES = {".py", ".md", ".txt", ".json", ".yml", ".yaml"}
JP = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")
PRIVATE = re.compile(r"[A-Za-z]:[/\\]Users[/\\]|(?:gh[pousr]_|github_pat_)[A-Za-z0-9_]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----")
BAD_FIELDS = {"jp", "japanese", "original", "source_text", "raw", "raw_hex", "source_hex"}

def check_export(obj, where):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key.casefold() in BAD_FIELDS:
                raise ValueError(f"{where}: forbidden original-source field {key}")
            check_export(value, where)
    elif isinstance(obj, list):
        for value in obj:
            check_export(value, where)
    elif isinstance(obj, str) and JP.search(obj):
        raise ValueError(f"{where}: Japanese text in English-only export")

def main():
    git = ["git", "-c", f"safe.directory={ROOT.as_posix()}"]
    names = subprocess.check_output(git + ["ls-files", "-z"], cwd=ROOT).decode().split("\0")
    names = [n for n in names if n]
    if not names:
        raise ValueError("No staged/tracked files to audit. Stage the intended publication first.")
    total = 0
    for name in names:
        p = PurePosixPath(name)
        allowed = name in ROOT_FILES or name.startswith(("tools/", "docs/", "work/translation/en/public/", ".github/workflows/"))
        if not allowed or (p.suffix not in ALLOWED_SUFFIXES and name not in ROOT_FILES and name != "tools/shared/LICENSE"):
            raise ValueError(f"Disallowed publication path: {name}")
        # Audit the index bytes so unstaged cleanup cannot hide staged sensitive data.
        blob = subprocess.check_output(git + ["show", ":" + name], cwd=ROOT)
        if len(blob) > 8_000_000 or b"\0" in blob:
            raise ValueError(f"Unexpected large/binary file: {name}")
        text = blob.decode("utf-8-sig")
        if PRIVATE.search(text):
            raise ValueError(f"Private path or secret pattern: {name}")
        if name.startswith("work/translation/en/public/") and p.suffix == ".json":
            check_export(json.loads(text), name)
        if p.suffix == ".py":
            tree = ast.parse(text, filename=name)
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str) and len(JP.findall(node.value)) > 250:
                    raise ValueError(f"Review extensive Japanese literal: {name}:{node.lineno}")
        total += len(blob)
    print(f"Publication audit passed: {len(names)} files, {total:,} bytes; Python syntax and English exports checked.")

if __name__ == "__main__":
    main()
