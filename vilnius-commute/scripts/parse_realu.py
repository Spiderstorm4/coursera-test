import re, html, json, glob, sys
S=sys.argv[1]; out=[]
urls={u.strip().rsplit('realu',1)[1]:u.strip() for u in open(f'{S}/listings/raw/realu/urls.txt') if u.strip()}
def txt(t):
    s=re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S); s=html.unescape(re.sub(r'<[^>]+>',' | ',s)); return re.sub(r'(\s*\|\s*)+',' | ',s)
def num(x):
    try: return float(x.replace('\xa0','').replace(' ','').replace(',','.'))
    except: return None
for f in glob.glob(f'{S}/listings/raw/realu/ad_*.html'):
    id=f.rsplit('_',1)[1][:-5]; t=open(f,encoding='utf8',errors='ignore').read(); s=txt(t)
    def after(lbl): m=re.search(r'\| '+re.escape(lbl)+r' \| ([^|]+) \|',s); return m.group(1).strip() if m else None
    lat=re.search(r'latitude="([\d.]+)',t); lon=re.search(r'longitude="([\d.]+)',t)
    m=re.search(r'\| Nuomojamas butas \| ([^|]+) \| Žiūrėti žemėlapyje \| ([\d\s\xa0]+) €',s)
    i=s.find('Papildoma informacija'); desc=s[i+22:i+3000] if i>=0 else ''
    dep=re.findall(r'[^|.]{0,60}(?:depozit|užstat)[^|.]{0,80}',desc,re.I)
    title=re.search(r'<title>(.*?)</title>',t,re.S)
    out.append(dict(site='realu.lt',id=id,url=urls.get(id),addr=m.group(1).strip() if m else None,price_eur=num(m.group(2)) if m else None,
      area_m2=num((after('Plotas') or '').replace(' m','').split()[0]) if after('Plotas') else None,floor=after('Aukštas'),rooms=num(after('Kambariai') or ''),
      status=after('Statusas'),posted=(re.search(r'Skelbimas įkeltas \| (\d{4}-\d\d-\d\d)',s) or [None,None])[1],
      lat=float(lat.group(1)) if lat else None,lon=float(lon.group(1)) if lon else None,
      deposit='; '.join(x.strip() for x in dep)[:300] or None,desc=desc[:2500],title=html.unescape(title.group(1).strip()) if title else None))
json.dump(out,open(f'{S}/listings/realu.json','w'),ensure_ascii=False,indent=1); print(len(out))
