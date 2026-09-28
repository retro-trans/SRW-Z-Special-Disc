"""Font-aware layout for the native three-line save/load recap panel."""
from sp_disc import ROOT,require
from library_text import CHARS
from inspect_english_runtime import CAVE,CAVE_FILE

# The printer starts at x=-236 on a 640-wide centered canvas. 520 leaves
# 36 pixels before the right edge. The English advance trampoline adds these
# values directly to the screen pen; do not scale them by the JP font size.
LINE_LIMIT=520
ROWS=3
DONOR=(ROOT/'work/cache/english-runtime/english.elf').read_bytes()
WIDTHS=DONOR[CAVE_FILE+0x78b960-CAVE:CAVE_FILE+0x78b960-CAVE+69]


def width(value):
    return sum(WIDTHS[CHARS.index(ord(c))]+2 if ord(c)in CHARS else 13 if c==' 'else 24 for c in value)


def wrap(value,strict=True):
    lines=[];line=''
    for word in value.split():
        require(width(word)<=LINE_LIMIT,'Save recap word exceeds the panel: '+word)
        candidate=(line+' '+word).strip()
        if line and width(candidate)>LINE_LIMIT:lines.append(line);line=word
        else:line=candidate
    if line:lines.append(line)
    if strict:require(len(lines)<=ROWS,'Save recap needs '+str(len(lines))+' lines: '+value)
    return lines,[width(line)for line in lines]
