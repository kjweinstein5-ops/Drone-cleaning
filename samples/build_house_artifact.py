"""Build the interactive 3D thermal-twin artifact from pipeline output.

    python -m sim.export_house_3d --write        # 1. regenerate the data
    python samples/build_house_artifact.py       # 2. rebuild the HTML

Reads samples/house_3d.json and writes samples/building_3d_artifact.html — a
single self-contained page (no external assets) suitable for publishing.

Headline counts are derived from the data, never typed in, so the page can't
drift from the pipeline that produced it.
"""

from __future__ import annotations

import json
from pathlib import Path

SAMPLES = Path(__file__).resolve().parent
DATA_PATH = SAMPLES / "house_3d.json"
OUT_PATH = SAMPLES / "building_3d_artifact.html"

TEMPLATE = r'''<title>PROPWASH — 3D Thermal Twin</title>
<style>
:root{--bg:#060c18;--card:#0f1d35;--card2:#152240;--bd:#1a2e50;--blue:#3b7ef8;--cyan:#06c0d8;
--green:#10d98a;--red:#f04040;--amber:#f5a623;--tx:#dde6f0;--mu:#5a7298;}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:var(--bg);color:var(--tx);font-family:-apple-system,Segoe UI,Roboto,sans-serif}
.wrap{max-width:1000px;margin:0 auto;padding:16px}
header{border-bottom:1px solid var(--bd);padding-bottom:12px;margin-bottom:14px}
h1{font-size:19px;font-weight:800;letter-spacing:.5px}
h1 span{color:var(--blue)}
.sub{font-size:12px;color:var(--mu);margin-top:3px}
.badge{display:inline-block;font-size:10px;font-weight:800;color:var(--cyan);
border:1px solid var(--cyan);padding:2px 7px;border-radius:3px;margin-top:7px;letter-spacing:.4px}
.grid{display:grid;grid-template-columns:1fr 300px;gap:14px}
@media(max-width:820px){.grid{grid-template-columns:1fr}}
.panel{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:14px}
canvas{width:100%;display:block;border-radius:8px;background:linear-gradient(180deg,#081226,#040a14);
cursor:grab;touch-action:none}
canvas:active{cursor:grabbing}
.modes{display:flex;gap:6px;margin-bottom:10px;flex-wrap:wrap}
.mode{flex:1;min-width:88px;border:1px solid var(--bd);background:var(--card2);color:var(--mu);
border-radius:7px;padding:8px 6px;font-size:11px;font-weight:800;cursor:pointer;letter-spacing:.3px}
.mode.on{background:var(--blue);color:#fff;border-color:var(--blue)}
.hint{font-size:11px;color:var(--mu);text-align:center;margin-top:8px}
.legend{margin-top:10px}
.bar{height:9px;border-radius:5px;background:linear-gradient(90deg,
rgb(30,64,175),rgb(6,182,212),rgb(16,185,129),rgb(234,179,8),rgb(249,115,22),rgb(239,68,68))}
.lab{display:flex;justify-content:space-between;font-size:10px;color:var(--mu);margin-top:3px}
.ttl{font-size:10px;text-transform:uppercase;letter-spacing:.7px;color:var(--mu);
font-weight:800;margin:14px 0 7px}
.ttl:first-child{margin-top:0}
.row{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--bd);font-size:12px}
.row span{color:var(--mu)}
.row b{font-variant-numeric:tabular-nums}
.zname{font-size:15px;font-weight:800}
.zsub{font-size:11px;color:var(--mu);margin-bottom:9px}
.chipwrap{display:flex;gap:5px;flex-wrap:wrap;margin-bottom:10px}
.chip{font-size:9px;font-weight:800;padding:3px 7px;border-radius:20px}
.chip.solar{background:rgba(245,166,35,.15);color:var(--amber)}
.chip.excl{background:rgba(240,64,64,.15);color:var(--red)}
.chip.ok{background:rgba(16,217,138,.15);color:var(--green)}
.ph{display:flex;align-items:center;gap:8px;padding:7px 0;border-bottom:1px solid var(--bd)}
.dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.phn{font-size:11px;font-weight:700;flex:1}
.phv{font-size:11px;color:var(--mu);font-variant-numeric:tabular-nums}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:12px}
.stat{background:var(--card2);border:1px solid var(--bd);border-radius:9px;padding:10px;text-align:center}
.sv{font-size:18px;font-weight:900;line-height:1}
.sl{font-size:9px;color:var(--mu);margin-top:4px;text-transform:uppercase;letter-spacing:.4px}
.note{font-size:11px;color:var(--mu);line-height:1.55;margin-top:12px;
padding:10px;background:rgba(59,126,248,.06);border:1px solid var(--bd);border-radius:8px}
.note b{color:var(--tx)}
.warn{background:rgba(245,166,35,.07);border-color:rgba(245,166,35,.3)}
footer{margin-top:16px;padding-top:12px;border-top:1px solid var(--bd);
font-size:11px;color:var(--mu);line-height:1.6}
</style>

<div class="wrap">
<header>
  <h1>PROPWASH <span>— 3D Thermal Twin</span></h1>
  <div class="sub">Single-family residence, Carlsbad CA — every surface classified and dirt-mapped from one drone scan</div>
  <div class="badge">LIVE PIPELINE OUTPUT · __FACES__ FACES · __ZONES__ ZONES · __PASSES__ TREATMENT PASSES</div>
</header>

<div class="grid">
  <div class="panel">
    <div class="modes">
      <button class="mode on" data-m="dirt">Dirt map</button>
      <button class="mode" data-m="surface">Surface type</button>
      <button class="mode" data-m="post">After clean</button>
      <button class="mode" data-m="thermal">Temperature</button>
    </div>
    <canvas id="c" width="1300" height="900"></canvas>
    <div class="hint">Drag to orbit · click a surface to inspect</div>
    <div class="legend" id="lg">
      <div class="bar"></div>
      <div class="lab"><span>Clean</span><span>Dirty</span></div>
    </div>
    <div class="stats">
      <div class="stat"><div class="sv" style="color:var(--blue)">__CLEAN__</div><div class="sl">Cleanable</div></div>
      <div class="stat"><div class="sv" style="color:var(--red)">__EXCL__</div><div class="sl">No-spray</div></div>
      <div class="stat"><div class="sv" style="color:var(--green)">__PASSES__</div><div class="sl">Passes</div></div>
    </div>
  </div>

  <div class="panel" id="side"></div>
</div>

<div class="note warn">
  <b>Concurrency finding:</b> deconfliction reports <b>max __MAXC__ aircraft</b> for this building — the
  zones sit too close together to fly two safely. A second drone would add nothing here.
  Multi-aircraft economics favour <b>large commercial and solar sites</b>, not compact properties.
</div>

<footer>
Geometry, surface classification, grime values and treatment passes are produced by the PROPWASH
pipeline, not hand-authored. Grime is a <b>proxy</b> derived from thermal +
RGB — not a spectral measurement. Pre-soak and rinse are water-only by construction; solar stays
DI-water-only under 2.0 bar in every phase.
</footer>
</div>

<script>
DATA=__DATA__;

var C=document.getElementById('c'),X=C.getContext('2d');
var az=-0.72, el=0.42, mode='dirt', sel=null, drag=null;

var RAMP=[[0,[30,64,175]],[.25,[6,182,212]],[.5,[16,185,129]],[.65,[234,179,8]],[.82,[249,115,22]],[1,[239,68,68]]];
function ramp(v){v=Math.max(0,Math.min(1,v));
 for(var i=1;i<RAMP.length;i++){if(v<=RAMP[i][0]){
  var t=(v-RAMP[i-1][0])/(RAMP[i][0]-RAMP[i-1][0]),a=RAMP[i-1][1],b=RAMP[i][1];
  return [a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,a[2]+(b[2]-a[2])*t];}}
 return [239,68,68];}

var SURF={solar_panel:[56,120,200],window_glass:[90,170,210],stucco:[200,190,170],
clay_tile:[190,110,80],composite_shingle:[130,110,95],exclusion:[90,107,130]};

// centre the model
var cx=0,cy=0,cz=0,n=0;
DATA.faces.forEach(function(f){f.v.forEach(function(p){cx+=p[0];cy+=p[1];cz+=p[2];n++;});});
cx/=n;cy/=n;cz/=n;

function proj(p,w,h,s){
 var x=p[0]-cx,y=p[1]-cy,z=p[2]-cz;
 var ca=Math.cos(az),sa=Math.sin(az);
 var rx=x*ca-y*sa, ry=x*sa+y*ca;
 var ce=Math.cos(el),se=Math.sin(el);
 var depth=ry*ce-z*se, up=ry*se+z*ce;
 return {x:w/2+rx*s, y:h/2-up*s, d:depth};
}

function outward(v,c){
 var nm=norm(v);
 var mid=[(v[0][0]+v[1][0]+v[2][0])/3,(v[0][1]+v[1][1]+v[2][1])/3,(v[0][2]+v[1][2]+v[2][2])/3];
 var away=[mid[0]-c[0],mid[1]-c[1],mid[2]-c[2]];
 if(nm[0]*away[0]+nm[1]*away[1]+nm[2]*away[2]<0){return [-nm[0],-nm[1],-nm[2]];}
 return nm;
}
function camDir(){
 var ca=Math.cos(az),sa=Math.sin(az),ce=Math.cos(el),se=Math.sin(el);
 return [-sa*ce,-ca*ce,se];   // scene → camera
}
function norm(v){
 var a=[v[1][0]-v[0][0],v[1][1]-v[0][1],v[1][2]-v[0][2]];
 var b=[v[2][0]-v[0][0],v[2][1]-v[0][1],v[2][2]-v[0][2]];
 var nx=a[1]*b[2]-a[2]*b[1],ny=a[2]*b[0]-a[0]*b[2],nz=a[0]*b[1]-a[1]*b[0];
 var L=Math.sqrt(nx*nx+ny*ny+nz*nz)||1;return [nx/L,ny/L,nz/L];
}

function faceColor(f){
 if(mode==='surface'){return SURF[f.surf]||[120,120,120];}
 if(mode==='thermal'){
   if(f.temp===null)return [90,107,130];
   return ramp((f.temp-28)/32);
 }
 if(f.excl)return [90,107,130];
 var g=(mode==='post')?0.05:f.g;
 return ramp(g);
}

function visible(){
 var w=C.width,h=C.height,s=Math.min(w,h)/16,cd=camDir();
 return DATA.faces.map(function(f){
   var pts=f.v.map(function(p){return proj(p,w,h,s);});
   return {f:f,pts:pts,d:(pts[0].d+pts[1].d+pts[2].d)/3,nm:outward(f.v,[cx,cy,cz])};
 }).filter(function(t){
   return t.nm[0]*cd[0]+t.nm[1]*cd[1]+t.nm[2]*cd[2] > -0.02;   // backface cull
 });
}

function draw(){
 X.clearRect(0,0,C.width,C.height);
 var tris=visible().sort(function(a,b){return b.d-a.d;});

 tris.forEach(function(t){
   var c=faceColor(t.f);
   // simple directional light
   var L=[0.4,-0.5,0.75], dot=Math.abs(t.nm[0]*L[0]+t.nm[1]*L[1]+t.nm[2]*L[2]);
   var sh=0.55+0.45*dot;
   var isSel=sel===t.f.zone;
   X.beginPath();
   X.moveTo(t.pts[0].x,t.pts[0].y);
   X.lineTo(t.pts[1].x,t.pts[1].y);
   X.lineTo(t.pts[2].x,t.pts[2].y);
   X.closePath();
   X.fillStyle='rgb('+(c[0]*sh|0)+','+(c[1]*sh|0)+','+(c[2]*sh|0)+')';
   X.fill();
   X.strokeStyle=isSel?'rgba(255,255,255,.95)':'rgba(255,255,255,.10)';
   X.lineWidth=isSel?3:1;
   X.stroke();
 });

 // zone labels — largest visible face per zone, skipping collisions
 var done={},placed=[],best={};
 tris.forEach(function(t){
   var p=t.pts;
   var ar=Math.abs((p[1].x-p[0].x)*(p[2].y-p[0].y)-(p[2].x-p[0].x)*(p[1].y-p[0].y))/2;
   if(!best[t.f.zone]||ar>best[t.f.zone].ar)best[t.f.zone]={t:t,ar:ar};
 });
 Object.keys(best).map(function(k){return best[k];})
  .sort(function(a,b){return b.ar-a.ar;})
  .forEach(function(e){
   var t=e.t;
   if(done[t.f.zone])return;
   var m={x:(t.pts[0].x+t.pts[1].x+t.pts[2].x)/3,y:(t.pts[0].y+t.pts[1].y+t.pts[2].y)/3};
   for(var i=0;i<placed.length;i++){
     if(Math.abs(placed[i].x-m.x)<95&&Math.abs(placed[i].y-m.y)<30)return;
   }
   placed.push(m); done[t.f.zone]=1;
   X.font='700 20px -apple-system,sans-serif';
   X.textAlign='center';
   X.fillStyle='rgba(0,0,0,.65)';
   X.fillText(t.f.zone,m.x+1.5,m.y+1.5);
   X.fillStyle=t.f.excl?'#ffb3b3':'#ffffff';
   X.fillText(t.f.zone,m.x,m.y);
   if(t.f.excl){
     X.font='700 15px -apple-system,sans-serif';
     X.fillStyle='#ff8080';
     X.fillText('NO SPRAY',m.x,m.y+21);
   }
 });
}

function pick(mx,my){
 var tris=visible().sort(function(a,b){return a.d-b.d;});
 for(var i=0;i<tris.length;i++){
   var p=tris[i].pts;
   var d1=sign(mx,my,p[0],p[1]),d2=sign(mx,my,p[1],p[2]),d3=sign(mx,my,p[2],p[0]);
   var neg=(d1<0)||(d2<0)||(d3<0), pos=(d1>0)||(d2>0)||(d3>0);
   if(!(neg&&pos))return tris[i].f.zone;
 }
 return null;
}
function sign(px,py,a,b){return (px-b.x)*(a.y-b.y)-(a.x-b.x)*(py-b.y);}

var PH={pre_soak:['#06c0d8','Pre-soak'],chemical:['#f5a623','Chemical'],rinse:['#10d98a','Rinse']};

function side(){
 var el2=document.getElementById('side');
 if(!sel){
   var rows=Object.keys(DATA.zones).map(function(z){
     var d=DATA.zones[z];
     var col=d.excl?'#5a6b82':'rgb('+ramp(d.g).map(function(x){return x|0;}).join(',')+')';
     return '<div class="ph"><div class="dot" style="background:'+col+'"></div>'+
       '<div class="phn">'+z+'</div><div class="phv">'+
       (d.excl?'no spray':Math.round(d.g*100)+'% grime')+'</div></div>';
   }).join('');
   var gain=DATA.schedule['1']-DATA.schedule['2'];
   var fleet=['1','2','3'].map(function(k){
     var ideal=DATA.scheduleIdeal[k], real=DATA.schedule[k];
     var strike=(ideal<real)?' <s style="opacity:.5">'+ideal+'</s>':'';
     return '<div class="row"><span>'+k+' aircraft</span><b>'+real+' min'+strike+'</b></div>';
   }).join('');
   var verdict = gain>0.5
     ? 'Extra aircraft pipeline through chemical <b>dwell</b> — the throughput gain is real here.'
     : 'Struck-through figures are what the phase scheduler could reach if geometry allowed. '+
       'On this house deconfliction caps it at <b>'+DATA.maxConcurrent+' aircraft</b>, so a second '+
       'drone buys nothing. Safety is not tradeable for throughput.';
   el2.innerHTML='<div class="ttl">All zones</div>'+rows+
     '<div class="ttl">Job time by fleet</div>'+fleet+
     '<div class="note">'+verdict+'</div>';
   return;
 }
 var d=DATA.zones[sel];
 var ph=DATA.phases[sel]||[];
 var chips='';
 if(d.solar)chips+='<span class="chip solar">SOLAR · DI WATER · 2.0 BAR MAX</span>';
 if(d.excl)chips+='<span class="chip excl">EXCLUSION · NO SPRAY</span>';
 else chips+='<span class="chip ok">SAFETY-GATED</span>';

 var rows='<div class="row"><span>Surface</span><b>'+d.surf.replace(/_/g,' ')+'</b></div>'+
   '<div class="row"><span>Grime (proxy)</span><b>'+Math.round(d.g*100)+'%</b></div>'+
   (d.temp!==null?'<div class="row"><span>Temperature</span><b>'+d.temp+' °C</b></div>':'')+
   '<div class="row"><span>Pitch</span><b>'+d.pitch+'°</b></div>'+
   '<div class="row"><span>Classifier conf.</span><b>'+Math.round(d.conf*100)+'%</b></div>';

 var phase='';
 if(ph.length){
   phase='<div class="ttl">Treatment passes</div>'+ph.map(function(p){
     var m=PH[p.ph];
     return '<div class="ph"><div class="dot" style="background:'+m[0]+'"></div>'+
       '<div class="phn">'+m[1]+'</div><div class="phv">'+p.p+' bar · '+
       p.c.replace(/_/g,' ')+'</div></div>';
   }).join('');
 }

 el2.innerHTML='<div class="zname">'+sel+'</div>'+
   '<div class="zsub">'+d.surf.replace(/_/g,' ')+'</div>'+
   '<div class="chipwrap">'+chips+'</div>'+rows+phase+
   '<div class="note">'+d.reason+'</div>';
}

// interaction
function xy(e){var r=C.getBoundingClientRect(),t=e.touches?e.touches[0]:e;
 return {x:(t.clientX-r.left)/r.width*C.width,y:(t.clientY-r.top)/r.height*C.height};}
function down(e){var p=xy(e);drag={x:p.x,y:p.y,az:az,el:el,moved:0};}
function move(e){if(!drag)return;e.preventDefault();var p=xy(e);
 var dx=p.x-drag.x,dy=p.y-drag.y;drag.moved+=Math.abs(dx)+Math.abs(dy);
 az=drag.az+dx*0.005; el=Math.max(0.12,Math.min(1.45,drag.el+dy*0.004)); draw();}
function up(e){
 if(drag&&drag.moved<6){var p=xy(e);
  var z=pick(p.x,p.y); sel=(z===sel)?null:z; draw(); side();}
 drag=null;}
C.addEventListener('mousedown',down);
window.addEventListener('mousemove',move);
window.addEventListener('mouseup',up);
C.addEventListener('touchstart',down,{passive:true});
C.addEventListener('touchmove',move,{passive:false});
C.addEventListener('touchend',function(e){
 if(drag&&drag.moved<6){var r=C.getBoundingClientRect(),t=e.changedTouches[0];
  var z=pick((t.clientX-r.left)/r.width*C.width,(t.clientY-r.top)/r.height*C.height);
  sel=(z===sel)?null:z; draw(); side();}
 drag=null;});

[].forEach.call(document.querySelectorAll('.mode'),function(b){
 b.onclick=function(){
  [].forEach.call(document.querySelectorAll('.mode'),function(o){o.classList.remove('on');});
  b.classList.add('on'); mode=b.dataset.m;
  var lg=document.getElementById('lg');
  lg.style.visibility=(mode==='surface')?'hidden':'visible';
  var lab=lg.querySelector('.lab');
  if(mode==='thermal')lab.innerHTML='<span>Cool 28°C</span><span>Hot 60°C</span>';
  else lab.innerHTML='<span>Clean</span><span>Dirty</span>';
  draw();};
});

draw(); side();
</script>'''


def build() -> str:
    data = json.loads(DATA_PATH.read_text())
    c = data["counts"]
    html = TEMPLATE
    for token, value in {
        "__DATA__": json.dumps(data, separators=(",", ":")),
        "__FACES__": c["faces"],
        "__ZONES__": c["zones"],
        "__PASSES__": c["passes"],
        "__CLEAN__": c["clean"],
        "__EXCL__": c["excl"],
        "__MAXC__": data["maxConcurrent"],
    }.items():
        html = html.replace(token, str(value))
    return html


if __name__ == "__main__":
    html = build()
    OUT_PATH.write_text(html)
    print(f"wrote {OUT_PATH}  {len(html):,} bytes")
