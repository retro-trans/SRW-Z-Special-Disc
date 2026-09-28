"""Verify receipt-listed inputs and finished patch after independent ISO audit."""
import argparse
import json
import re
from sp_disc import ROOT, file_sha, require, Disc, SOURCE, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', required=True)
    parser.add_argument('--previous', required=True)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    for version in (args.version, args.previous):
        require(re.fullmatch(r'0\.\d+\.\d+', version) is not None, 'Expected version 0.x.y')
    iso = ROOT/f'work/output/SRW Z Special Disc English v{args.version}.iso'
    receipt = json.loads(iso.with_suffix('.json').read_text(encoding='utf-8'))
    previous = json.loads((ROOT/f'work/output/SRW Z Special Disc English v{args.previous}.json').read_text(encoding='utf-8'))
    audit = json.loads((ROOT/f'work/analysis/build-{args.version}-independent-audit.json').read_text(encoding='utf-8'))
    require(receipt['version'] == audit['version'] == args.version, 'Version mismatch')
    require(file_sha(iso) == receipt['output_sha256'] == audit['iso_sha256'], 'Finished ISO changed')
    counts = {}
    for group in ('source_files', 'translation_files', 'glossary_files', 'artifact_files'):
        counts[group] = len(receipt.get(group,{}))
        for relative, expected in receipt.get(group,{}).items():
            path = (ROOT/relative).resolve()
            require(path.is_relative_to(ROOT.resolve()), 'Input outside workspace')
            require(file_sha(path) == expected, 'Receipt input changed: ' + relative)
    patch = iso.with_suffix('.xdelta')
    require(file_sha(patch) == receipt['patch']['sha256'] and patch.stat().st_size == receipt['patch']['bytes'], 'Finished patch changed')
    require(receipt['patch']['roundtrip_verified'] is True and audit['patch_reconstruction_verified'] is True,
            'Patch reconstruction missing')
    added=set(receipt['members'])-set(previous['members'])
    removed=set(previous['members'])-set(receipt['members'])
    require(not removed and added <= {'MAP/MAPMODEL.BIN','KURODATA/KVMDATA.BIN'}, 'Unplanned payload inventory change')
    if 'KURODATA/KVMDATA.BIN' in added:
        require(audit['deployment_ui']['graphic_tiles_read_back']==4,'New squad artwork has no independent audit')
        prior=Disc(ROOT/f'work/output/SRW Z Special Disc English v{args.previous}.iso')
        require(prior.read('KURODATA/KVMDATA.BIN')==Disc(SOURCE).read('KURODATA/KVMDATA.BIN'),'Previous squad archive was not native')
    if 'MAP/MAPMODEL.BIN' in added:
        require(receipt.get('world_map_titles')==13 and audit['world_map_titles']['titles_read_back']==13,
                'New location component has no independent audit')
        prior=Disc(ROOT/f'work/output/SRW Z Special Disc English v{args.previous}.iso')
        require(prior.read('MAP/MAPMODEL.BIN')==Disc(SOURCE).read('MAP/MAPMODEL.BIN'),
                'Previous location archive was not native')
    texture_delta=None
    if receipt.get('episode_titles')==21 and not previous.get('episode_titles'):
        require(audit['episode_titles']['titles_read_back']==21,'Episode component has no independent audit')
        prior=Disc(ROOT/f'work/output/SRW Z Special Disc English v{args.previous}.iso')
        current=Disc(iso);old=prior.read('DATA/VT1.BIN');new=current.read('DATA/VT1.BIN')
        title_report=json.loads((ROOT/f'work/analysis/build-{args.version}-episode_titles.json').read_text(encoding='utf-8'))
        spans=sorted((r['start'],r['end']) for r in title_report['entries'] if r['changed'])
        cursor=0;protected=0
        for lo,hi in spans+[(len(old),len(old))]:
            require(old[cursor:lo]==new[cursor:lo],'Previous-release artwork changed outside episode spans')
            protected+=lo-cursor;cursor=hi
        require(len(new)==len(old),'Previous-release texture archive size changed')
        texture_delta=dict(member='DATA/VT1.BIN',changed_spans=len(spans),protected_bytes=protected,
                           all_other_texture_bytes_identical=True)
    report = dict(version=args.version, input_counts=counts, all_receipt_inputs_match=True,
                  compared_release=args.previous,
                  changed_payloads=[k for k,v in receipt['members'].items() if k in added or v['sha256'] != previous['members'][k]['sha256']],
                  added_payloads=sorted(added),
                  texture_delta=texture_delta,
                  iso_bytes=iso.stat().st_size, iso_sha256=receipt['output_sha256'],
                  patch=receipt['patch'], validation=receipt['validation'])
    print(json.dumps(report, indent=2))
    if args.write:
        (ROOT/f'work/analysis/build-{args.version}-input-verification.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    else:
        print('DRY RUN: no report written')


if __name__ == '__main__':
    main()
