"""Export an English-only review corpus. Dry run by default; --write publishes it.

Requires local translation inputs and the story runtime cache. Original strings,
encoded bytes, source dumps, local paths and review conversations are never copied.
These exports are review material, not a complete rebuild input snapshot.
"""
import argparse
import json
import re
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EN = ROOT / "work/translation/en"
OUT = EN / "public"
JP = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")
ENTRY_FILES = ["library_complete", "compdata", "system", "battle_release_0.2.14",
               "chart_bound", "narration_reviewed", "mission_conditions",
               "save_summaries_release_0.2.9", "deployment_ui"]
FIELDS = {"id", "offset", "capacity", "source_sha256", "text", "lines", "set", "record", "tag"}

def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def corpus():
    result = {}
    for name in ENTRY_FILES:
        raw = read(EN / (name + ".json"))
        entries = raw if isinstance(raw, list) else raw["entries"]
        rows = [{k: v for k, v in row.items() if k in FIELDS} for row in entries]
        result[name + ".json"] = {"schema_version": 1, "entries": rows}
    for name in ("briefings", "reference_names"):
        result[name + ".json"] = read(EN / (name + ".json"))
    # Use the same reviewed-fit and name-rule selection as the shipped story build.
    from story_layout import load, layout_row
    source, speakers, final = load()
    by_chunk = {}
    for row in source:
        tr = final[row["id"]]
        rendered, _, variant = layout_row(row, speakers, tr)
        item = {"id": row["id"], "speaker": rendered.split("\n", 1)[0],
                "en": tr["en"], "display_variant": variant,
                "display_text": rendered.split("\n", 1)[1]}
        by_chunk.setdefault(row["chunk"], []).append(item)
    for chunk, rows in sorted(by_chunk.items()):
        result[f"story/c{chunk:02}.json"] = {"schema_version": 1, "rows": rows}
    for f in sorted((EN / "story_extra_reviewed").glob("*.json")):
        result[f"story/extra-{f.name}"] = {"schema_version": 1, "rows": [
            {k: v for k, v in r.items() if k in {"id", "en", "speaker"}}
            for r in read(f)["rows"]]}
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = corpus()
    total = 0
    for name, obj in result.items():
        text = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
        match = JP.search(text)
        if match:
            raise ValueError(f"Japanese text in English-only export {name}: {text[max(0,match.start()-50):match.end()+50]!r}")
        total += len(text.encode("utf-8"))
        if args.write:
            path = OUT / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    print(f"{'Wrote' if args.write else 'Dry run:'} {len(result)} English-only files, {total:,} bytes")
    print("Story sample:", result["story/c01.json"]["rows"][0])

if __name__ == "__main__":
    main()
