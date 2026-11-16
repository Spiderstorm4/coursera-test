import sys, json, pandas as pd, geopandas as gpd
from shapely.geometry import box
S=sys.argv[1]; sys.path.insert(0,sys.argv[2]); from chain import evaluate_flex, evaluate, load_pair, fmt
grid=gpd.read_file(f"{S}/out/grid.geojson").to_crs(3346)
K2S=load_pair(S,'K2S'); S2K=load_pair(S,'S2K')
A={i:dict(zip(g.dep_min,g.travel_time)) for i,g in pd.read_csv(f"{S}/out/tt_G2K.csv").dropna().groupby('from_id')}
B={i:dict(zip(g.dep_min,g.travel_time)) for i,g in pd.read_csv(f"{S}/out/tt_G2S.csv").dropna().groupby('from_id')}
lab={2:'qualifying',1:'borderline',0:'too long',-1:'no option within 30 min'}
rows=[]
for gid in grid.id:
    r=dict(id=gid)
    for tag,leg1,tab in (('KS',A.get(gid,{}),K2S),('SK',B.get(gid,{}),S2K)):
        e=evaluate_flex(leg1,tab,tag)
        r[f'{tag}_class']=lab[e['cls'] if e else -1]
        if e: r.update({f'{tag}_latest_departure':fmt(e['dep']),f'{tag}_leg1_min':e['leg1'],f'{tag}_leave_first_stop':fmt(e['dep2']),f'{tag}_leg2_min':e['leg2'],f'{tag}_total_min':e['total'],f'{tag}_school_arrival':fmt(e['school_arr'])})
        e2=evaluate_flex(leg1,tab,tag,lim=18,blim=23); r[f'{tag}_class_robust18']=lab[e2['cls'] if e2 else -1]
    rows.append(r)
G=grid.merge(pd.DataFrame(rows),on='id')
G['geometry']=G.geometry.apply(lambda p: box(p.x-100,p.y-100,p.x+100,p.y+100))
G=G.to_crs(4326)
Z=G[G.KS_class.isin(['qualifying','borderline'])|G.SK_class.isin(['qualifying','borderline'])]
Z.to_file(f"{S}/out/zone_cells.geojson",driver='GeoJSON')
for tag in ('KS','SK'):
    for nm in ('qualifying','borderline'):
        sub=G[G[f'{tag}_class']==nm].to_crs(3346)
        if len(sub): gpd.GeoDataFrame({'order':[tag],'class':[nm],'cells':[len(sub)],'area_km2':[round(len(sub)*0.04,2)]},geometry=[sub.union_all()],crs=3346).to_crs(4326).to_file(f"{S}/out/zone_{tag}_{nm}.geojson",driver='GeoJSON')
print(G.KS_class.value_counts().to_dict()); print(G.SK_class.value_counts().to_dict())
