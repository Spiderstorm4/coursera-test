import sys, json
S=sys.argv[1]; sys.path.insert(0,sys.argv[2]); from chain import fmt
F={x['lid']:x for x in json.load(open(f"{S}/out/listings_final.json"))}
from stops_parse import parse
R3=json.load(open(f"{S}/out/stops_r3.json"))
layout={46:"3 isolated rooms + kitchen",90:"3 separate rooms + separate kitchen",80:"2-level flat, 3 rooms, 2 bathrooms",
 2:"living+kitchen, main bedroom, child/work room",66:"living+kitchen, main bedroom, child/work room",
 55:"living+kitchen, 1 bedroom + vaulted basement room (3rd room is a basement – check if usable for sleeping)",
 6:"kitchen-living + 2 bedrooms; own entrance (private house)",18:"living + 2 bedrooms, 2 WC",29:"living + 2 bedrooms (part of a house, 3rd floor)",
 43:"living + 2 bedrooms",92:"not stated in list view",22:"living + bedroom + guest/work room",71:"living/kitchen + bedroom + extra room (work/wardrobe)",85:"3 separate rooms"}
notes={46:"Map pin approximate per realu.lt; ad says ~0.16 km to Subačiaus st. stop",90:"OLD AD: posted 2025-01-15 – may already be rented. Location = street centroid (no house no.)",
 80:"",2:"Same flat as next row (Vingrių g. 13) – duplicate ad",66:"Duplicate of Vingrių g. 13 ad above",55:"Ad text says the flat is on Dysnos g. (not Šiaulių g.)",
 6:"",18:"Exact address Pilies g. 42",29:"",43:"",92:"STALE AD: last updated 2020-05-26. Location = street centroid",22:"",71:"Only 53 m²",
 85:"Card says 680 EUR but ad text says 750 EUR + utilities; lease at least until summer; was available from 5 Oct"}
deposit={85:"2 months (stated in ad)"}
def leg2_desc(e):
    if e['dep2']==451: return "bus 13 (07:33) or 10 (07:34) Vilnelės st. → Zarasų/Subačiaus st. → bus 34 → Polocko st. 07:44 → walk"
    return f"leave kindergarten {fmt(e['dep2'])}; bus 10/13 → transfer → bus 33/34/74/89 (r5 GTFS)"
order=[46,90,80,2,66,55,6,18,29,43,92,22,71,85]
rows=[["Rank","Status (r5py / GTFS)","Status cross-check (stops.lt planner)","Link","Address","Price EUR/month","Deposit","Rooms","Layout","m²","Floor","Posted / updated","Leg 1 home→kindergarten (min)","Leg 2 kindergarten→school (min)","Total home→school (min)","Latest departure from home","Leave kindergarten","School arrival","Routes leg 1 (stops.lt)","Routes leg 2","Walking min leg1 / leg2 (stops.lt)","Early stops.lt-verified chain (school 07:28)","Reverse order (school first)","Notes / caveats","Site","Contacted? (you fill)","Contact notes (you fill)"]]
items=sorted(order,key=lambda l:(F[l]['KS']['total'],l))
for i,l in enumerate(items,1):
    x=F[l]; e=x['KS']; s=x.get('stops_KS') or {}
    st=x['KS_class']
    if st=='QUALIFYING': cross=f"BORDERLINE at 07:31 slot (stops.lt leg2 = 22 min: leave K 07:28 → 07:50); leg1 {s.get('leg1')} min"
    else: cross=f"leg1 {s.get('leg1')} min, leg2 22 min → " + ("borderline" if s.get('leg1') and s['leg1']<=25 else "too long")
    if l==85: s85=parse(R3['85_H2K_arr0728'])[0]; s={'leg1':s85['dur'],'leg1_routes':s85['routes'],'leg1_walk':s85['walk_min']}; cross=f"leg1 {s85['dur']} min, leg2 22 → too long"
    ek=R3.get(f"{l if l!=66 else 2}_H2K_arr0708"); ev=parse(ek)[0] if ek and parse(ek) else None
    early = (f"leave {ev['dep']} → kindergarten {ev['arr']} ({ev['dur']} min, {ev['routes']}) → leave 07:08 → school 07:28 (20 min): " + ("BOTH LEGS ≤20 ✔" if ev['dur']<=20 else ("borderline" if ev['dur']<=25 else "leg1 too long"))) if ev else ""
    sk=x['SK']; rev=f"{x['SK_class']} (leg1 {sk['leg1']}, leg2 {sk['leg2']} min)" if sk else x['SK_class']
    rows.append([i, st if st=='QUALIFYING' else 'BORDERLINE', cross, x['url'], x['addr'], x['price_eur'], deposit.get(l,"not stated in ad"), int(x['rooms']), layout[l], x['area_m2'], x['floor'], x.get('posted'),
      e['leg1'], e['leg2'], e['total'], fmt(e['dep']), fmt(e['dep2']), fmt(e['school_arr']), s.get('leg1_routes',''), leg2_desc(e), f"{s.get('leg1_walk','')} / 10", early, rev, notes[l], x['site'], "", ""])
others=[["Link","Address","Price EUR","m²","Floor","Posted","Kindergarten-first class","Best leg1/leg2/total (min)","School-first class","Site"]]
for x in sorted([v for k,v in F.items() if k not in order], key=lambda v:(v['KS']['total'] if v['KS'] else 999)):
    e=x['KS']
    others.append([x['url'],x['addr'],x['price_eur'],x.get('area_m2'),x.get('floor'),x.get('posted'),x['KS_class'],f"{e['leg1']}/{e['leg2']}/{e['total']}" if e else "no option ≤45 min",x['SK_class'],x['site']])
json.dump({'shortlist':rows,'others':others},open(f"{S}/out/sheet_rows.json",'w'),ensure_ascii=False)
for r in rows: print(r[:3],r[4],r[12:18])
print(len(others))
