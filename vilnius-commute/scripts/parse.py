import re, html, json, glob, sys, os
S=sys.argv[1]; out=[]
def txt(t):
    s=re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S); s=html.unescape(re.sub(r'<[^>]+>',' ',s)); return re.sub(r'\s+',' ',s)
def num(x):
    if x is None: return None
    x=x.replace(' ','').replace('\xa0','').replace(',','.'); 
    try: return float(x)
    except: return None
# rinka
urls={u.strip().rsplit('-id-',1)[1]:u.strip() for u in open(f'{S}/listings/raw/rinka/urls.txt')}
for f in glob.glob(f'{S}/listings/raw/rinka/ad_*.html'):
    id=f.rsplit('_',1)[1][:-5]; t=open(f,encoding='utf8',errors='ignore').read(); s=txt(t)
    def g(lbl,stop=r'(?= [A-ZĄČĘĖĮŠŲŪŽ][a-ząčęėįšųūž ,/²]+:|$)'):
        m=re.search(re.escape(lbl)+r'\s*(.*?)'+stop,s); return m.group(1).strip() if m else None
    title=re.search(r'<title>(.*?)</title>',t,re.S); title=html.unescape(title.group(1).strip()) if title else None
    price=re.search(r'Kaina:\s*([\d\s.,]+)\s*€',s)
    d=dict(site='rinka.lt',id=id,url=urls.get(id),title=title,price_eur=num(price.group(1)) if price else None,
      rooms=num(g('Kambarių skaičius:')),area_m2=num(g('Bendras plotas, m²:')),floor=g('Kelintame aukšte:'),floors_total=g('Pastato aukštų skaičius:'),
      district=g('Mikrorajonas / Gyvenvietė:'),street=g('Gatvė:'),city=g('Miestas / Rajonas:'),
      date=(re.search(r'Vilnius \|\s*(\d{4} \d\d \d\d)',s) or [None,None])[1])
    m=re.search(r'Gatvė:.*?(?=Kaina:)',s); d['desc']=m.group(0)[:1500] if m else None
    dep=re.search(r'(depozit[^.]{0,120})',s,re.I); d['deposit']=dep.group(1) if dep else None
    out.append(d)
# remax
for f in glob.glob(f'{S}/listings/raw/remax/ad_*.html'):
    id=f.rsplit('_',1)[1][:-5]; t=open(f,encoding='utf8',errors='ignore').read(); s=txt(t)
    u=[x.strip() for x in open(f'{S}/listings/raw/remax/urls.txt') if x.strip().endswith('-'+id)]
    m=re.search(r'Butas : (.*?) Kambarių sk\. (\d+)',s)
    pr=re.search(r'Rodyti ekrane .*? ([\d\s]+) € ',s)
    d=dict(site='remax.lt',id=id,url=u[0] if u else None,rented=('Išnuomota' in s[:1500]),
      addr=m.group(1) if m else None,rooms=num(m.group(2)) if m else None,price_eur=num(pr.group(1)) if pr else None,
      area_m2=num((re.search(r'Plotas ([\d.,]+) m²',s) or [None,None])[1]),floor=(re.search(r'Aukštas (\d+/\d+)',s) or [None,None])[1])
    i=s.find('Aukštas'); d['desc']=s[i:i+1800]
    dep=re.search(r'(depozit[^.;]{0,120})',s,re.I); d['deposit']=dep.group(1) if dep else None
    out.append(d)
json.dump(out,open(f'{S}/listings/parsed_all.json','w'),ensure_ascii=False,indent=1)
print(len(out))
