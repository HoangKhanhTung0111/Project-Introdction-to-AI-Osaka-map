import csv, json, math, random
random.seed(42)

LAT_MIN, LAT_MAX = 21.00, 21.06
LON_MIN, LON_MAX = 105.80, 105.88

nodes = []
nid = 0
for i in range(10):
    for j in range(10):
        lat = LAT_MIN + (LAT_MAX - LAT_MIN) * i / 9
        lon = LON_MIN + (LON_MAX - LON_MIN) * j / 9
        nodes.append({"node_id": nid, "lat": round(lat,6), "lon": round(lon,6)})
        nid += 1
for _ in range(30):
    lat = LAT_MIN + random.random() * (LAT_MAX - LAT_MIN)
    lon = LON_MIN + random.random() * (LON_MAX - LON_MIN)
    nodes.append({"node_id": nid, "lat": round(lat,6), "lon": round(lon,6)})
    nid += 1

with open("nodes.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["node_id","lat","lon"])
    w.writeheader(); w.writerows(nodes)

def haversine(lat1,lon1,lat2,lon2):
    R=6371000
    phi1,phi2=math.radians(lat1),math.radians(lat2)
    dlat=math.radians(lat2-lat1); dlon=math.radians(lon2-lon1)
    a=math.sin(dlat/2)**2+math.cos(phi1)*math.cos(phi2)*math.sin(dlon/2)**2
    return R*2*math.asin(math.sqrt(a))

edges = []
for i in range(10):
    for j in range(10):
        cur = i*10+j
        if j+1 < 10:
            nb = i*10+(j+1)
            d = haversine(nodes[cur]['lat'],nodes[cur]['lon'],nodes[nb]['lat'],nodes[nb]['lon'])
            edges += [{"from":cur,"to":nb,"distance":round(d,2)},{"from":nb,"to":cur,"distance":round(d,2)}]
        if i+1 < 10:
            nb = (i+1)*10+j
            d = haversine(nodes[cur]['lat'],nodes[cur]['lon'],nodes[nb]['lat'],nodes[nb]['lon'])
            edges += [{"from":cur,"to":nb,"distance":round(d,2)},{"from":nb,"to":cur,"distance":round(d,2)}]
for idx in range(100, 130):
    dists = sorted((haversine(nodes[idx]['lat'],nodes[idx]['lon'],nodes[g]['lat'],nodes[g]['lon']),g) for g in range(100))
    for d, g in dists[:3]:
        edges += [{"from":idx,"to":g,"distance":round(d,2)},{"from":g,"to":idx,"distance":round(d,2)}]

with open("edges.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=["from","to","distance"])
    w.writeheader(); w.writerows(edges)

features = []
seen = set()
for e in edges:
    key = tuple(sorted([e['from'],e['to']]))
    if key in seen: continue
    seen.add(key)
    n1,n2 = nodes[e['from']],nodes[e['to']]
    features.append({"type":"Feature","properties":{"distance":e['distance']},
        "geometry":{"type":"LineString","coordinates":[[n1['lon'],n1['lat']],[n2['lon'],n2['lat']]]}})

with open("roads.geojson","w") as f:
    json.dump({"type":"FeatureCollection","features":features},f)

print(f"Generated {len(nodes)} nodes, {len(edges)} edges, {len(features)} road segments")
