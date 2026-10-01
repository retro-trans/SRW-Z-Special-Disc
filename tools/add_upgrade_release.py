"""Add the missing 0.3.0 -> 0.3.16 route without replacing published patch bytes.

The original package is read-only; all new assets are staged in fresh directories.
"""
import argparse,json,shutil,sys
from pathlib import Path
from prepare_release import ROOT,digest,EXPECTED_TARGET

SOURCE_SHA='ca444e5c078a6f3cb23a96c5b6d676de1df068cfa4219ecbc06e71cbea4186ec'
NAME='SRWZ-SP-English-v0.3.0-to-v0.3.16.xdelta'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--retro-trans',type=Path,required=True)
    p.add_argument('--write',action='store_true');a=p.parse_args()
    sys.path.insert(0,str(a.retro_trans.resolve()))
    from retro_trans.release import build_release,validate_directory
    from retro_trans.catalog import atomic_json,Catalog,assert_immutable
    prior=ROOT/'work/output/release-v0.3.16'
    upgrade=ROOT/'work/output/release-v0.3.16-upgrade-only'
    output=ROOT/'work/output/release-v0.3.16-with-upgrade'
    source=ROOT/'work/output/SRW Z Special Disc English v0.3.0.iso'
    target=ROOT/'work/output/SRW Z Special Disc English v0.3.16.iso'
    manifest=validate_directory(prior)
    old_source=validate_directory(ROOT/'work/output/release-v0.3.0')['patches'][0]
    assert manifest['version']=='0.3.16' and len(manifest['patches'])==1
    assert manifest['patches'][0]['target_sha256']==EXPECTED_TARGET
    assert old_source['target_sha256']==SOURCE_SHA
    assert not upgrade.exists() and not output.exists(),'Use fresh staging directories'
    assert source.is_file() and target.is_file()
    if not a.write:
        print('DRY RUN: add '+NAME+'; retain the full patch, game hashes and tag.');return
    assert digest(source,'sha256')==SOURCE_SHA and digest(target,'sha256')==EXPECTED_TARGET
    config={k:v for k,v in manifest.items() if k not in ('patches','schema_version')}
    config['patches']=[dict(patch=NAME,edition='Japan (SLPS-25920)',language='en',
        source_version='0.3.0',source_format='iso',target_format='iso',
        source=str(source),target=str(target))]
    private=ROOT/'work/cache/publication';private.mkdir(parents=True,exist_ok=True)
    local=private/'upgrade-0.3.0-to-0.3.16-local.json'
    local.write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
    print('Building and reconstructing v0.3.0 upgrade...',flush=True)
    addition=build_release(local,upgrade,cache=private/'runtime')
    entry=addition['patches'][0]
    entry['source_sha1']=digest(source,'sha1')
    entry['target_sha1']=manifest['patches'][0]['target_sha1']
    assert entry['source_sha1']==old_source['target_sha1']
    assert (entry['target_sha256'],entry['target_bytes'])==(manifest['patches'][0]['target_sha256'],manifest['patches'][0]['target_bytes'])
    combined=dict(manifest,patches=manifest['patches']+[entry])
    def catalog(m):
        return Catalog(dict(schema_version=1,releases=[dict(repo='retro-trans/SRW-Z-Special-Disc',tag='v0.3.16',manifest=m,
            assets={r['patch']:'https://github.com/retro-trans/SRW-Z-Special-Disc/releases/download/v0.3.16/'+r['patch'] for r in m['patches']})]))
    assert_immutable(catalog(manifest),catalog(combined))
    shutil.copytree(prior,output)
    shutil.copyfile(upgrade/NAME,output/NAME)
    atomic_json(output/'BUILD-MANIFEST.json',combined)
    validation=json.loads((prior/'VALIDATION.json').read_text(encoding='utf-8'))
    validation['patches']+=json.loads((upgrade/'VALIDATION.json').read_text(encoding='utf-8'))['patches']
    validation['manifest_sha256']=digest(output/'BUILD-MANIFEST.json','sha256')
    atomic_json(output/'VALIDATION.json',validation)
    for src,dst in [('README.md','README-v0.3.16.txt'),('CHANGELOG.md','CHANGELOG-v0.3.16.txt')]:
        shutil.copyfile(ROOT/src,output/dst)
    names={'BUILD-MANIFEST.json','VALIDATION.json'}|{r['patch'] for r in combined['patches']}
    (output/'SHA256SUMS.txt').write_text('\n'.join(f"{digest(output/name,'sha256')}  {name}" for name in sorted(names))+'\n',encoding='utf-8')
    assert validate_directory(output)==combined
    for old in manifest['patches']:
        assert digest(output/old['patch'],'sha256')==old['patch_sha256']
    print(json.dumps(dict(package=output.name,new_patch=entry,existing_patch_unchanged=True,roundtrip_verified=True),indent=2),flush=True)

if __name__=='__main__':main()
