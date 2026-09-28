"""Full-word caption layout within the native two-row battle area."""
from sp_disc import require
from save_summary_text import width

# Native setup 0x303340: x=160, width=480 on a 640-unit screen.
# Leave twenty units at the right edge, including the closing quotation mark.
LINE_LIMIT = 460
ROWS = 2


def flatten(value):
    return ' '.join(value.replace('\\n', ' ').split())


def layout(value):
    original = [s.strip() for s in value.split('\\n')]
    def quoted(lines): return ['"'+lines[0]] if len(lines) == 1 else ['"'+lines[0], lines[1]]
    def finish(lines):
        result = quoted(lines); result[-1] += '"'; return result
    if 0 < len(original) <= ROWS and all(original):
        result = finish(original)
        if max(map(width, result)) <= LINE_LIMIT: return result
    words = flatten(value).split(); candidates = []
    for split in range(1, len(words)):
        result = finish([' '.join(words[:split]), ' '.join(words[split:])])
        spans = list(map(width, result))
        if max(spans) <= LINE_LIMIT: candidates.append((abs(spans[0]-spans[1]), result))
    if not candidates: return None
    result = min(candidates, key=lambda r: r[0])[1]
    require(' '.join(result)[1:-1] == flatten(value), 'Caption layout lost or reordered words')
    return result
