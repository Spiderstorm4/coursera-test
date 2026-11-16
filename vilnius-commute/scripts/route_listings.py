import sys, json, datetime as dt, warnings; warnings.filterwarnings('ignore')
import pandas as pd, geopandas as gpd, numpy as np
from shapely.geometry import Point
import r5py
sys.path.insert(0, sys.argv[2]); from chain import evaluate, load_pair, fmt
S=sys.argv[1]
import gc
L=json.load(open(f"{S}/listings/all_listings.json"))
K=(25.3193472,54.6754507); SC=(25.3131255,54.6850765)
net=r5py.TransportNetwork(f"{S}/data/vilnius.osm.pbf",[f"{S}/data/gtfs.zip"])
D=dt.date(2026,11,18); modes=[r5py.TransportMode.TRANSIT,r5py.TransportMode.WALK]
orig=gpd.GeoDataFrame({'id':[x['lid'] for x in L]},geometry=[Point(x['lon'],x['lat']) for x in L],crs=4326)
fixed=gpd.GeoDataFrame({'id':['K','S']},geometry=[Point(K),Point(SC)],crs=4326)
def T(m): return dt.datetime.combine(D,dt.time(m//60,m%60))
def ttm(o,de,minutes):
    rows=[]
    for m in minutes:
        r=pd.DataFrame(r5py.TravelTimeMatrix(net,origins=o,destinations=de,departure=T(m),departure_time_window=dt.timedelta(minutes=1),transport_modes=modes,max_time=dt.timedelta(minutes=45),snap_to_network=True)); r['dep_min']=m; rows.append(r)
    return pd.concat(rows)
g2k=pd.read_csv(f"{S}/out/listings_G2K.csv").dropna(); g2s=pd.read_csv(f"{S}/out/listings_G2S.csv").dropna()
K2S=load_pair(S,'K2S'); S2K=load_pair(S,'S2K')
def itin(lon1,lat1,lon2,lat2,m,target):
    o=gpd.GeoDataFrame({'id':[0]},geometry=[Point(lon1,lat1)],crs=4326); de=gpd.GeoDataFrame({'id':[0]},geometry=[Point(lon2,lat2)],crs=4326)
    df=pd.DataFrame(r5py.DetailedItineraries(net,origins=o,destinations=de,departure=T(m),departure_time_window=dt.timedelta(minutes=5),transport_modes=modes,max_time=dt.timedelta(minutes=40),snap_to_network=True))
    if len(df)==0: return None
    t0=T(m); best=None
    for opt,g in df.groupby('option'):
        g=g.sort_values('segment')
        # reconstruct clock times: walk-first segments have departure_time; arrival = last dep + travel
        clock=None; segs=[]; walk=0.0; routes=[]
        for _,r in g.iterrows():
            md=str(r.transport_mode).split('.')[-1]
            tt=r.travel_time.total_seconds()/60; wt=r.wait_time.total_seconds()/60
            if md=='WALK': walk+=tt
            rid=str(r.route_id) if pd.notna(r.route_id) else ''
            name=rid.replace('vilnius_','').replace('_',' ') if rid else ''
            if name: routes.append(name)
            dep=r.departure_time if pd.notna(r.departure_time) else None
            segs.append(f"{md.lower()}{' '+name if name else ''}{' '+dep.strftime('%H:%M') if dep is not None else ''} ({tt:.0f} min{', wait '+format(wt,'.0f') if wt>=0.5 else ''})")
        last=g.iloc[-1]; first=g.iloc[0]
        if pd.isna(first.departure_time) or pd.isna(last.departure_time): continue
        start=first.departure_time; arr=last.departure_time+last.travel_time
        if start < t0 - dt.timedelta(seconds=30): continue
        tot=(arr-t0).total_seconds()/60
        c=dict(total_from_dep=round(tot,1),arrive=arr.strftime('%H:%M'),walk=round(walk,1),routes=' + '.join(routes) if routes else 'walk only',segments=' | '.join(segs))
        if best is None or arr<best[0]: best=(arr,c)
    return best[1] if best else None
res=[]
for x in L:
    lid=x['lid']
    l1k=dict(zip(g2k[g2k.from_id==lid].dep_min,g2k[g2k.from_id==lid].travel_time))
    l1s=dict(zip(g2s[g2s.from_id==lid].dep_min,g2s[g2s.from_id==lid].travel_time))
    out=dict(lid=lid)
    for order,leg1,tab,dest1,dest2 in (('KS',l1k,K2S,K,SC),('SK',l1s,S2K,SC,K)):
        e=evaluate(leg1,tab,order)
        out[order]=e
        out[order+'_robust18']=(evaluate(leg1,tab,order,lim=18,blim=23) or {}).get('cls')
        if order=='KS':
            out['KS_early']=evaluate(leg1,tab,order,deadline=450)  # school by 07:30
    need = (out['KS'] and out['KS']['cls']>=1) or (out['SK'] and out['SK']['cls']>=1)
    if need:
        for key,dest1,dest2 in (('KS',K,SC),('SK',SC,K),('KS_early',K,SC)):
            e=out.get(key)
            if e and e['cls']>=1:
                e['it1']=itin(x['lon'],x['lat'],dest1[0],dest1[1],e['dep'],e['leg1']); e['it2']=itin(dest1[0],dest1[1],dest2[0],dest2[1],e['dep2'],e['leg2'])
    res.append(out); print(lid, out['KS'] and (out['KS']['cls'],out['KS']['leg1'],out['KS']['leg2']), flush=True)
json.dump(res,open(f"{S}/out/listing_commutes.json",'w'),ensure_ascii=False,indent=1,default=str)
print('done')
