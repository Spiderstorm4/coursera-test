import sys, pandas as pd, numpy as np
G=sys.argv[1]; dep_door=sys.argv[2]  # HH:MM leaving kindergarten door
WALK=60.0  # m/min straight line (3.6 km/h)
st=pd.read_csv(f'{G}/stops.txt',dtype=str); st['lat']=st.stop_lat.astype(float); st['lon']=st.stop_lon.astype(float)
def dist(lat,lon,df=st): return np.hypot((df.lat-lat)*111200,(df.lon-lon)*111200*np.cos(np.radians(54.68)))
st['dK']=dist(54.6754507,25.3193472); st['dS']=dist(54.6850765,25.3131255)
cal=pd.read_csv(f'{G}/calendar.txt',dtype=str); cd=pd.read_csv(f'{G}/calendar_dates.txt',dtype=str)
act=set(cal[(cal.wednesday=='1')&(cal.start_date<='20261118')&(cal.end_date>='20261118')].service_id)
act-=set(cd[(cd.date=='20261118')&(cd.exception_type=='2')].service_id); act|=set(cd[(cd.date=='20261118')&(cd.exception_type=='1')].service_id)
tr=pd.read_csv(f'{G}/trips.txt',dtype=str); tr=tr[tr.service_id.isin(act)]; rt=pd.read_csv(f'{G}/routes.txt',dtype=str)
tr=tr.merge(rt[['route_id','route_short_name','route_type']],on='route_id')
stt=pd.read_csv(f'{G}/stop_times.txt',dtype=str,usecols=['trip_id','arrival_time','departure_time','stop_id','stop_sequence'])
stt=stt[stt.trip_id.isin(set(tr.trip_id))].copy(); stt['seq']=stt.stop_sequence.astype(int)
def mn(t): h,m,s=map(int,t.split(':')); return h*60+m+s/60
stt['arr']=stt.arrival_time.map(mn); stt['dep']=stt.departure_time.map(mn)
stt=stt[(stt.dep>=410)&(stt.arr<=500)]
stt=stt.merge(tr[['trip_id','route_short_name']],on='trip_id').merge(st[['stop_id','stop_name','lat','lon','dK','dS']],on='stop_id')
t0=mn(dep_door+':00')
# leg A: board near K
A=stt[(stt.dK<=600)]; A=A[A.dep>=t0+A.dK/WALK]
res=[]
for (trip,rname),g in A.groupby(['trip_id','route_short_name']):
    b=g.sort_values('dep').iloc[0]
    down=stt[(stt.trip_id==trip)&(stt.seq>b.seq)]
    for _,x in down.iterrows():
        # direct to school
        if x.dS<=600: res.append((x.arr+x.dS/WALK, f"walk {b.dK/WALK:.0f}m→{b.stop_name} {rname} {int(b.dep)//60:02d}:{int(b.dep)%60:02d}→{x.stop_name} {int(x.arr)//60:02d}:{int(x.arr)%60:02d} walk {x.dS/WALK:.0f}m"))
        # transfer
        near=stt[(np.hypot((stt.lat-x.lat)*111200,(stt.lon-x.lon)*111200*np.cos(np.radians(54.68)))<=250)&(stt.trip_id!=trip)]
        for _,y in near.iterrows():
            tw=np.hypot((y.lat-x.lat)*111200,(y.lon-x.lon)*111200*np.cos(np.radians(54.68)))/WALK
            if y.dep < x.arr+tw+0.5: continue
            z=stt[(stt.trip_id==y.trip_id)&(stt.seq>y.seq)&(stt.dS<=600)]
            for _,zz in z.iterrows():
                res.append((zz.arr+zz.dS/WALK, f"walk {b.dK/WALK:.0f}m→{b.stop_name} {rname} {int(b.dep)//60:02d}:{int(b.dep)%60:02d}→{x.stop_name} {int(x.arr)//60:02d}:{int(x.arr)%60:02d} | {y.route_short_name} {y.stop_name} {int(y.dep)//60:02d}:{int(y.dep)%60:02d}→{zz.stop_name} {int(zz.arr)//60:02d}:{int(zz.arr)%60:02d} walk {zz.dS/WALK:.0f}m"))
res=sorted(set((round(a,1),s) for a,s in res))
for a,s in res[:8]: print(f"door-arrive {int(a)//60:02d}:{a%60:04.1f}  ({a-t0:.1f} min)  {s}")
