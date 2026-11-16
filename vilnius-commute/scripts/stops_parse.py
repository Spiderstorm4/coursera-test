import re
def parse(txt):
    """Return list of variants: dict(dep,arr,dur,routes,walk_min,steps)."""
    if not txt: return []
    txt=txt.replace("\xa0"," ").replace("\u2007"," ")
    if "Variantas" not in txt: return []
    parts=re.split(r'Variantas \d+\.',txt)[1:]; res=[]
    for p in parts:
        m=re.match(r'\s*(\d+:\d\d)\s*—\s*(\d+:\d\d),\s*kelionės trukmė (\d+):(\d\d)',p)
        if not m: continue
        lines=[l.strip() for l in p.split('\n') if l.strip()]
        walk=sum(int(x) for x in re.findall(r'eiti (\d+) min',p))
        routes=[]
        for i,l in enumerate(lines):
            mm=re.match(r'^([0-9]+[A-Z]?|[A-Z]?[0-9]+[A-Z]?)\s*(Autobusas|Troleibusas|Greitasis|Naktinis|Ekspres)',l)
            if mm: routes.append(('trol ' if 'Troleib' in l else 'bus ')+mm.group(1))
        res.append(dict(dep=m.group(1).zfill(5),arr=m.group(2).zfill(5),dur=int(m.group(3))*60+int(m.group(4)),routes=' + '.join(routes) or 'walk only',walk_min=walk,steps=' / '.join(lines[1:12])))
    return res
