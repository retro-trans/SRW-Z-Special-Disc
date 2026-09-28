"""Create an isolated copy of the existing emulator for SP tests; dry-run first."""
import argparse
import configparser
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('E:/Projects/SRW Z/_work/emulators/pcsx2-1.7.4005')
DEST=ROOT/'work/emulator'


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    files=[p for p in SOURCE.iterdir() if p.is_file() and (p.suffix=='.dll' or p.name in
           ('pcsx2-qtx64-avx2.exe','portable.ini','qt.conf'))]
    for folder in ('bios','resources','QtPlugins'):
        files.extend(p for p in (SOURCE/folder).rglob('*') if p.is_file())
    print('Copy',len(files),'existing runtime files,',sum(p.stat().st_size for p in files),'bytes to',DEST)
    print('Separate settings, no user memory cards, no texture pack, keyboard controls; native source/other games untouched.')
    if not args.write:return
    if DEST.exists():raise ValueError('Isolated emulator already exists; do not overwrite settings')
    for p in files:
        out=DEST/p.relative_to(SOURCE);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
    cfg=configparser.RawConfigParser(strict=False);cfg.optionxform=str
    cfg.read(SOURCE/'inis/PCSX2.ini',encoding='utf-8')
    changes={'UI':{'RenderToSeparateWindow':'false','PauseOnFocusLoss':'false','ConfirmShutdown':'false'},
             'MemoryCards':{'Slot1_Enable':'false','Slot2_Enable':'false'},
             'EmuCore/GS':{'upscale_multiplier':'1','LoadTextureReplacements':'false','DumpReplaceableTextures':'false'},
             'Pad1':{'Up':'Keyboard/Up','Right':'Keyboard/Right','Down':'Keyboard/Down','Left':'Keyboard/Left',
                     'Circle':'Keyboard/X','Cross':'Keyboard/Z','Triangle':'Keyboard/S','Square':'Keyboard/A',
                     'Start':'Keyboard/Return','Select':'Keyboard/Backspace','L1':'Keyboard/Q','R1':'Keyboard/W'},
             'Folders':{'Snapshots':str(ROOT/'work/ui/runtime'),'MemoryCards':str(DEST/'memcards'),
                        'Savestates':str(DEST/'sstates'),'Bios':str(DEST/'bios')}}
    for section,values in changes.items():
        if not cfg.has_section(section):cfg.add_section(section)
        for key,value in values.items():cfg.set(section,key,value)
    (DEST/'inis').mkdir();(ROOT/'work/ui/runtime').mkdir(parents=True,exist_ok=True)
    with (DEST/'inis/PCSX2.ini').open('w',encoding='utf-8') as f:cfg.write(f)
    print('Isolated emulator ready:',DEST/'pcsx2-qtx64-avx2.exe')


if __name__=='__main__':main()
