import sys, datetime as dt, time, json
import numpy as np, pandas as pd, geopandas as gpd
from shapely.geometry import Point
S=sys.argv[1]
import r5py
K=(25.3193472,54.6754507); SC=(25.3131255,54.6850765)
net=r5py.TransportNetwork(f"{S}/data/vilnius.osm.pbf",[f"{S}/data/gtfs.zip"])
pts=gpd.GeoSeries([Point(K),Point(SC)],crs=4326).to_crs(3346)
cx,cy=(pts.x.mean(),pts.y.mean())
R=7000; step=200
xs=np.arange(cx-R,cx+R+1,step); ys=np.arange(cy-R,cy+R+1,step)
g=[(x,y) for x in xs for y in ys if (x-cx)**2+(y-cy)**2<=R*R]
grid=gpd.GeoDataFrame({'id':range(len(g))},geometry=gpd.points_from_xy([a for a,b in g],[b for a,b in g]),crs=3346).to_crs(4326)
grid.to_file(f"{S}/out/grid.geojson",driver="GeoJSON")
print('grid',len(grid),flush=True)
fixed=gpd.GeoDataFrame({'id':['K','S']},geometry=[Point(K),Point(SC)],crs=4326)
D=dt.date(2026,11,18)
def run(orig,dest,minutes,tag):
    rows=[]
    import os
    for m in minutes:
        if os.path.exists(f"{S}/out/part_{tag}_{m}.csv"): rows.append(pd.read_csv(f"{S}/out/part_{tag}_{m}.csv")); continue
        t=dt.datetime.combine(D,dt.time(m//60,m%60))
        t0=time.time()
        ttm=r5py.TravelTimeMatrix(net,origins=orig,destinations=dest,departure=t,
            departure_time_window=dt.timedelta(minutes=1),transport_modes=[r5py.TransportMode.TRANSIT,r5py.TransportMode.WALK],
            max_time=dt.timedelta(minutes=30),snap_to_network=True)
        df=pd.DataFrame(ttm); df['dep_min']=m; rows.append(df); df.to_csv(f"{S}/out/part_{tag}_{m}.csv",index=False)
        print(tag,m,round(time.time()-t0,1),flush=True)
    out=pd.concat(rows); out.to_csv(f"{S}/out/tt_{tag}.csv",index=False); return out
mins=list(range(7*60+0,8*60))


run(grid,fixed[fixed.id=='K'],list(range(405,461)),'G2K')

print('done')
