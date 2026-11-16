import sys, json, folium, geopandas as gpd, html
S=sys.argv[1]; OUT=sys.argv[2]; sys.path.insert(0,sys.argv[3]); from chain import fmt
m=folium.Map(location=[54.680,25.300],zoom_start=14,tiles='OpenStreetMap')
styles={('KS','qualifying'):('#1a9850',0.45,'Qualifying (kindergarten first, both legs ≤20 min)'),
        ('KS','borderline'):('#fdae61',0.40,'Borderline (kindergarten first, legs ≤25 min)'),
        ('SK','borderline'):('#7b3294',0.0,'Borderline – reverse order (school first); no qualifying cells')}
for (o,c),(col,op,name) in styles.items():
    try: g=gpd.read_file(f"{S}/out/zone_{o}_{c}.geojson")
    except Exception: continue
    folium.GeoJson(g.__geo_interface__,name=name,style_function=lambda f,col=col,op=op,o=o:{'color':col,'weight':2 if o=='SK' else 1,'fillColor':col,'fillOpacity':op,'dashArray':'6 4' if o=='SK' else None}).add_to(m)
folium.Marker([54.6754507,25.3193472],tooltip='Kindergarten: Markučių l/d, Pakraščio g. 15',icon=folium.Icon(color='blue',icon='child',prefix='fa')).add_to(m)
folium.Marker([54.6850765,25.3131255],tooltip='School: Filaretų pradinė, Filaretų g. 43A',icon=folium.Icon(color='darkblue',icon='graduation-cap',prefix='fa')).add_to(m)
F=json.load(open(f"{S}/out/listings_final.json"))
colr={'QUALIFYING':'green','BORDERLINE':'orange'}
fg_c=folium.FeatureGroup(name='Listings – qualifying / borderline').add_to(m)
fg_o=folium.FeatureGroup(name='Listings – outside zone',show=False).add_to(m)
for x in F:
    c=x['KS_class']; e=x['KS']
    t=(f"<b>{html.escape(x['addr'])}</b><br>{x['price_eur']:.0f} EUR · {x.get('area_m2')} m² · floor {x.get('floor')}<br>"
       f"Kindergarten-first: <b>{c}</b>" + (f"<br>leave {fmt(e['dep'])} · leg1 {e['leg1']} · leg2 {e['leg2']} · total {e['total']} min" if e else '') +
       f"<br>School-first: {x['SK_class']}<br><a href='{x['url']}' target='_blank'>{x['site']} listing</a>")
    if c in colr:
        folium.CircleMarker([x['lat'],x['lon']],radius=8,color='black',weight=1,fill=True,fill_color=colr[c],fill_opacity=0.95,popup=folium.Popup(t,max_width=320),tooltip=x['addr']).add_to(fg_c)
    else:
        folium.CircleMarker([x['lat'],x['lon']],radius=4,color='#555',weight=1,fill=True,fill_color='#bbb',fill_opacity=0.8,popup=folium.Popup(t,max_width=320),tooltip=x['addr']).add_to(fg_o)
folium.LayerControl(collapsed=False).add_to(m)
m.get_root().html.add_child(folium.Element('<div style="position:fixed;bottom:12px;left:12px;z-index:9999;background:white;padding:8px 10px;border:1px solid #999;font:12px sans-serif;max-width:340px">Weekday 2026-11-18, arrive school by 08:00. Walking + Vilnius public transport (GTFS stops.lt, r5py). Each leg door-to-door incl. waiting; drop-off time at kindergarten not counted in a leg.</div>'))
m.save(f"{OUT}/commute_zone_map.html"); print('saved')
