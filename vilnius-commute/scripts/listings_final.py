import sys, json, pandas as pd
S=sys.argv[1]; sys.path.insert(0,sys.argv[2]); from chain import evaluate_flex, load_pair, fmt
from stops_parse import parse
L=json.load(open(f"{S}/listings/all_listings.json"))
K2S=load_pair(S,'K2S'); S2K=load_pair(S,'S2K')
gk=pd.read_csv(f"{S}/out/listings_G2K.csv").dropna(); gs=pd.read_csv(f"{S}/out/listings_G2S.csv").dropna()
A={i:dict(zip(g.dep_min,g.travel_time)) for i,g in gk.groupby('from_id')}; B={i:dict(zip(g.dep_min,g.travel_time)) for i,g in gs.groupby('from_id')}
R1=json.load(open(f"{S}/out/stops_r1.json")); R2=json.load(open(f"{S}/out/stops_r2.json"))
# fill failed duplicates
R2['66_H2K_arr0728']=R2['2_H2K_arr0728']; R2['46_S2K_dep0755']=R2['2_S2K_dep0755']; R2['15_S2K_dep0756']=R2['6_S2K_dep0756']
lab={2:'QUALIFYING',1:'BORDERLINE',0:'too long',-1:'no option'}
k2s_variants=[('07:08','07:30'),('07:28','07:50')]  # stops.lt K->S variants (arrive-by 07:30 / 08:00)
def mins(hm): h,m=map(int,hm.split(':')); return h*60+m
out=[]
for x in L:
    lid=x['lid']; r=dict(x); r.pop('desc',None)
    for tag,leg1,tab in (('KS',A.get(lid,{}),K2S),('SK',B.get(lid,{}),S2K)):
        e=evaluate_flex(leg1,tab,tag)
        r[f'{tag}']=e; r[f'{tag}_class']=lab[e['cls'] if e else -1]
        e2=evaluate_flex(leg1,tab,tag,lim=18,blim=23); r[f'{tag}_class_robust18']=lab[e2['cls'] if e2 else -1]
    # stops.lt cross-check (only candidates queried)
    v1=parse(R2.get(f'{lid}_H2K_arr0728',''))
    if v1:
        v=v1[0]; ka=mins(v['arr'])
        dep2,arr2=next(((d,a) for d,a in k2s_variants if mins(d)>=ka),k2s_variants[-1])
        r['stops_KS']=dict(dep=v['dep'],leg1=v['dur'],leg1_routes=v['routes'],leg1_walk=v['walk_min'],leave_K=dep2,leg2=mins(arr2)-mins(dep2),leg2_routes='bus 10 + bus 34',leg2_walk=10,school_arr=arr2,total=mins(arr2)-mins(v['dep']),wait_at_K=mins(dep2)-ka)
    h=parse(R1.get(f'{lid}_H2S_arr0800',''))
    if h:
        v=h[0]; s2=[k for k in R2 if k.startswith(f'{lid}_S2K')]
        w=parse(R2[s2[0]]) if s2 else []
        r['stops_SK']=dict(dep=v['dep'],leg1=v['dur'],leg1_routes=v['routes'],leg1_walk=v['walk_min'],school_arr=v['arr'],
            leg2_dep=w[0]['dep'] if w else None,leg2=(mins(w[0]['arr'])-mins(v['arr'])) if w else None,leg2_routes=w[0]['routes'] if w else None,leg2_walk=w[0]['walk_min'] if w else None,k_arr=w[0]['arr'] if w else None)
    out.append(r)
json.dump(out,open(f"{S}/out/listings_final.json",'w'),ensure_ascii=False,indent=1)
c=pd.Series([o['KS_class'] for o in out]).value_counts(); print(c.to_dict()); print(pd.Series([o['SK_class'] for o in out]).value_counts().to_dict())
for o in sorted([o for o in out if o['KS_class'] in ('QUALIFYING','BORDERLINE')],key=lambda o:(o['KS_class']!='QUALIFYING',o['KS']['total'])):
    e=o['KS']; s=o.get('stops_KS',{})
    print(o['lid'],o['KS_class'],o['addr'],o['price_eur'],f"r5: dep {fmt(e['dep'])} L1 {e['leg1']} dwell {e['dwell']} L2 {e['leg2']} tot {e['total']} arr {fmt(e['school_arr'])}",'| stops:',s.get('dep'),s.get('leg1'),s.get('leg2'),s.get('total'),s.get('leg1_routes'), '| r18',o['KS_class_robust18'])
