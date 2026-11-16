"""Chained-trip evaluation. Inputs: per-minute travel times. Leg times are door-to-door minutes
from the given departure minute (r5py includes initial wait at stops)."""
import pandas as pd, numpy as np
DEADLINE=480  # 08:00 in minutes after midnight
def fmt(m): m=int(m); return f"{m//60:02d}:{m%60:02d}"
def load_pair(S,tag):
    d=pd.read_csv(f"{S}/out/tt_{tag}.csv"); return dict(zip(d.dep_min,d.travel_time))
def evaluate(leg1, leg2tab, order, dwell=0, deadline=DEADLINE, lim=20, blim=25):
    """leg1: dict dep_min->tt (from home). leg2tab: dict dep_min->tt (K->S or S->K).
    order 'KS': arrival at school (end of leg2) must be <= 08:00.
    order 'SK': arrival at school (end of leg1) must be <= 08:00.
    Returns best option: class rank (2 ok,1 borderline,0 none), latest home departure."""
    best=None
    for d,t1 in sorted(leg1.items()):
        if t1 is None or (isinstance(t1,float) and np.isnan(t1)): continue
        a1=d+int(t1); m=a1+dwell
        if m not in leg2tab: continue
        t2=leg2tab[m]
        if t2 is None or (isinstance(t2,float) and np.isnan(t2)): continue
        a2=m+int(t2)
        school_arr = a2 if order=='KS' else a1
        if school_arr>deadline: continue
        cls = 2 if (t1<=lim and t2<=lim) else (1 if (t1<=blim and t2<=blim) else 0)
        cand=dict(cls=cls,dep=d,leg1=int(t1),arr1=a1,dep2=m,leg2=int(t2),arr2=a2,total=a2-d,school_arr=school_arr)
        # prefer higher class, then later departure, then shorter total
        key=(cls,d,-cand['total'])
        if best is None or key>best[0]: best=(key,cand)
    return best[1] if best else None

def evaluate_flex(leg1, leg2tab, order, mindwell=0, maxdwell=15, deadline=DEADLINE, lim=20, blim=25):
    """Leg 2 starts when the mother leaves the first destination; she may leave any minute
    between arrival+mindwell and arrival+maxdwell (drop-off / waiting inside not counted in a leg)."""
    best=None
    for d,t1 in sorted(leg1.items()):
        if t1 is None or (isinstance(t1,float) and np.isnan(t1)): continue
        a1=d+int(t1)
        if order=='SK' and a1>deadline: continue
        for m in range(a1+mindwell, a1+maxdwell+1):
            t2=leg2tab.get(m)
            if t2 is None or (isinstance(t2,float) and np.isnan(t2)): continue
            a2=m+int(t2); school_arr=a2 if order=='KS' else a1
            if school_arr>deadline: continue
            cls = 2 if (t1<=lim and t2<=lim) else (1 if (t1<=blim and t2<=blim) else 0)
            cand=dict(cls=cls,dep=d,leg1=int(t1),arr1=a1,dep2=m,dwell=m-a1,leg2=int(t2),arr2=a2,total=a2-d,school_arr=school_arr)
            key=(cls,d,-cand['total'],-cand['dwell'])
            if best is None or key>best[0]: best=(key,cand)
    return best[1] if best else None
