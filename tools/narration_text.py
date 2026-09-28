"""Thirteen-line narration layout using the ported font's conservative advance."""
from functools import lru_cache
from sp_disc import require
from save_summary_text import width

LINE_LIMIT=550
ROWS=13


def wrap_exact(value, rows):
    words=value.split()
    require(len(words)>=rows>0,'Narration line count cannot preserve words')
    target=(width(' '.join(words))-13*(rows-1))/rows
    @lru_cache(None)
    def solve(start,left):
        if left==0:return (0,()) if start==len(words) else None
        best=None
        for end in range(start+1,len(words)-left+2):
            line=' '.join(words[start:end]);span=width(line)
            if span>LINE_LIMIT:break
            tail=solve(end,left-1)
            if tail is None:continue
            candidate=((span-target)**2+tail[0],(line,)+tail[1])
            if best is None or candidate[0]<best[0]:best=candidate
        return best
    result=solve(0,rows)
    require(result is not None,'Narration full meaning does not fit '+str(rows)+' lines')
    return list(result[1])


def layout(value,index):
    paragraphs=[p.strip() for p in value.splitlines() if p.strip()]
    first=[];last=[]
    if index in (4,5,6,7):
        first=[paragraphs.pop(0)];last=[paragraphs.pop()]
    elif index==9:
        last=wrap_exact(paragraphs.pop(),2)
    require(all(width(line)<=LINE_LIMIT for line in first+last),'Narration date/signature overflow')
    lines=first+wrap_exact(' '.join(paragraphs),ROWS-len(first)-len(last))+last
    require(' '.join(value.split())==' '.join(lines),'Narration layout lost or reordered words')
    require(len(lines)==ROWS and max(map(width,lines))<=LINE_LIMIT,'Narration layout bound')
    return lines
