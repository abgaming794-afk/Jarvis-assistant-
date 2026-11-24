"""Builds India's official outline (incl. PoK, Gilgit-Baltistan, Aksai Chin, Shaksgam) for use on maps."""
import os as _os, glob as _glob
AB_ROOT = _os.environ.get("AB_ROOT", "/home/user/amrit-borii/")          # workspace root (brand/, fonts/, host/, render_tmp/)
PROJ = _os.path.join(AB_ROOT, _os.environ.get("AB_PROJECT", "new-axis"), "")  # current video project folder
MAPDATA = _os.environ.get("AB_MAPDATA") or next(iter(_glob.glob("/root/.claude/plugins/**/map-shorts/engine/data/", recursive=True)), "")
import json
from shapely.geometry import shape, box, LineString, mapping
from shapely.ops import unary_union, polygonize, nearest_points, split, linemerge
from shapely import wkt
GEO=MAPDATA + "countries10m.geojson"
C={f['properties']['ADM0_A3']:shape(f['geometry']).buffer(0) for f in json.load(open(GEO))['features'] if f['properties']['ADM0_A3'] in ('IND','PAK','CHN')}
OTH=[shape(f['geometry']).buffer(0) for f in json.load(open(GEO))['features'] if f['properties']['ADM0_A3'] in ('AFG','TJK','NPL')]
faces=[wkt.loads(s) for s in json.load(open('faces.json'))[0]]
add=shape(json.load(open('india_lines.json'))['to-add-ne'])
parts=list(getattr(add,'geoms',[add]))
# west (PoK) part = segments mostly inside Pakistan
west=[g for g in parts if C['PAK'].buffer(0.05).contains(g.centroid)]
wl=linemerge(unary_union(west)) if len(west)>1 else west[0]
wl=max(getattr(wl,'geoms',[wl]), key=lambda g:g.length)
pb=C['PAK'].boundary
from shapely.geometry import Point
c=list(wl.coords)
def ext(p,q,d=0.05):  # extend p away from q
    dx,dy=p[0]-q[0],p[1]-q[1]; n=(dx*dx+dy*dy)**.5 or 1; return (p[0]+dx/n*d,p[1]+dy/n*d)
def snap(p):
    q=nearest_points(Point(p),pb)[1]; return (q.x,q.y)
a=snap(c[0]); b=snap(c[-1])
print('ends',c[0],'->',a,' | ',c[-1],'->',b)
c=[ext(a,c[0]),a]+c+[b,ext(b,c[-1])]
cut=LineString(c)
pak=C['PAK']
pieces=list(split(pak,cut).geoms)
print('pak pieces',[round(p.area,2) for p in pieces])
# PoK piece = the one that touches India's border most and is north of 32.5
pok=[p for p in pieces if p.area<20 and p.centroid.y>33]
print('pok areas',[round(p.area,2) for p in pok])
extra=[f for f in faces if f.area in sorted([f.area for f in faces]) and False]
fx=[f for f in faces]
sel=[]
for f in fx:
    rp=f.representative_point()
    own='CHN' if C['CHN'].contains(rp) else 'PAK' if C['PAK'].contains(rp) else 'IND' if C['IND'].contains(rp) else 'OTHER' if any(C2.contains(rp) for C2 in OTH) else '-'
    if (own=='CHN' and f.area<5) or (own=='-' and f.area<0.25): sel.append(f)   # Aksai Chin (3.06), Shaksgam (0.51), gap (0.21)
print('extra faces', [round(f.area,2) for f in sel])
claim=unary_union([C['IND']]+pok+sel).buffer(0.002).buffer(-0.002)
pak_adm=C['PAK'].difference(claim); chn_adm=C['CHN'].difference(claim)
json.dump({'IND_OFFICIAL':mapping(claim),'PAK_MINUS':mapping(pak_adm),'CHN_MINUS':mapping(chn_adm)},open('india_official.geojson.json','w'))
print('India area', round(C['IND'].area,2),'->',round(claim.area,2))
