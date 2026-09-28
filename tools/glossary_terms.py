"""Apply only reviewed English spelling corrections before text layout."""
import json
import re
from sp_disc import ROOT

PATH=ROOT/'work/glossary/english.json'

def canonicalize(value,context=None,row=None):
    data=json.loads(PATH.read_text(encoding='utf-8'))
    rules=dict(data['spelling_corrections'])
    if context:
        scoped=data.get('context_sensitive_rules',{}).get(context,{})
        rules.update(scoped.get(str(row),{}) if row is not None else scoped)
    for old,new in rules.items():
        pattern=r'(?<![A-Za-z])'+r'\s+'.join(re.escape(w)for w in old.split())+r'(?![A-Za-z])'
        value=re.sub(pattern,new,value)
    return value
