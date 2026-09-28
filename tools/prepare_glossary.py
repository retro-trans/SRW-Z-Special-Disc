"""Snapshot the existing SRW Z term database with explicit provenance."""
import argparse
import json
from sp_disc import *

SOURCE_GLOSSARY=Path('E:/Projects/SRW-Z/analysis/glossary.json')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    terms=json.loads(SOURCE_GLOSSARY.read_text(encoding='utf-8'))
    require(isinstance(terms,dict) and all(isinstance(v,str)for v in terms.values()),'Glossary shape')
    result=dict(schema_version=1,source_path=str(SOURCE_GLOSSARY),source_sha256=file_sha(SOURCE_GLOSSARY),
        status='inherited spellings; not an independently researched character biography database',terms=terms)
    print(json.dumps(dict(entries=len(terms),source_sha256=result['source_sha256'],samples=list(terms.items())[:5]),ensure_ascii=True,indent=2))
    if args.write:
        (ROOT/'work/glossary/srw-z-terms.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else:print('DRY RUN: no files written')

if __name__=='__main__':main()
