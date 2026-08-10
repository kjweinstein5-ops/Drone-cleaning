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
.stage{position:relative}
.zoom-ctl{position:absolute;right:10px;bottom:10px;display:flex;flex-direction:column;gap:5px}
.zoom-ctl button{width:34px;height:34px;border-radius:9px;cursor:pointer;
border:1px solid var(--bd);background:rgba(10,20,40,.85);color:var(--tx);
font-size:18px;font-weight:700;line-height:1;display:flex;align-items:center;justify-content:center}
.zoom-ctl button:hover{background:rgba(59,126,248,.35);border-color:var(--blue)}
.zoom-ctl button:focus-visible{outline:2px solid var(--blue);outline-offset:2px}
.zoom-badge{position:absolute;left:12px;top:12px;font-size:11px;font-weight:800;
color:var(--mu);background:rgba(10,20,40,.7);border:1px solid var(--bd);
border-radius:6px;padding:3px 8px;font-variant-numeric:tabular-nums}
.stretch{display:flex;align-items:center;gap:9px;width:100%;margin-top:10px;padding:9px 11px;
text-align:left;cursor:pointer;border:1px solid var(--bd);border-radius:9px;
background:var(--card2);color:var(--mu);font-size:12px;font-weight:700}
.stretch:hover{border-color:var(--blue)}
.stretch:focus-visible{outline:2px solid var(--blue);outline-offset:2px}
.stretch.on{color:var(--tx);border-color:var(--cyan);background:rgba(6,192,216,.08)}
.sdot{width:10px;height:10px;border-radius:50%;border:1px solid var(--mu);flex-shrink:0}
.stretch.on .sdot{background:var(--cyan);border-color:var(--cyan)}
.snote{margin-left:auto;font-weight:500;font-size:10px;color:var(--mu);text-align:right}
.patch{display:flex;align-items:center;gap:9px;margin:10px 0 2px;padding:9px 10px;
border:1px solid var(--bd);border-radius:9px;background:rgba(6,192,216,.06)}
.psw{width:28px;height:28px;border-radius:6px;flex-shrink:0}
.ptx{font-size:11px;color:var(--mu);line-height:1.5}
.ptx b{color:var(--tx)}
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
    <div class="stage">
      <canvas id="c" width="1300" height="900"></canvas>
      <div class="zoom-ctl">
        <button id="zin" aria-label="Zoom in">+</button>
        <button id="zout" aria-label="Zoom out">&minus;</button>
        <button id="zres" aria-label="Reset view">&#10530;</button>
      </div>
      <div class="zoom-badge" id="zb">1.0&times;</div>
    </div>
    <div class="hint">Drag to orbit · scroll or pinch to zoom · shift-drag to pan · click a surface to inspect</div>
    <button class="stretch" id="st" aria-pressed="false">
      <span class="sdot"></span>Boost contrast
      <span class="snote" id="sn">colours on the absolute 0&ndash;100% scale</span>
    </button>
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
var az=-0.72, el=0.42, mode='dirt', sel=null, selFace=null, drag=null, pinch=null;
// 1.0 frames the structure; 9x resolves an individual mesh face, which is the
// resolution the grime layer is actually computed at.
var ZMIN=1.0, ZMAX=9.0, ZSTEP=1.6;
var zoom=1, panX=0, panY=0, stretch=false;

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
 var k=s*zoom;
 return {x:w/2+panX+rx*k, y:h/2+panY-up*k, d:depth};
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

function faceColor(f,remap){
 if(mode==='surface'){return SURF[f.surf]||[120,120,120];}
 if(mode==='thermal'){
   if(f.temp===null)return [90,107,130];
   return ramp(remap((f.temp-28)/32));
 }
 if(f.excl)return [90,107,130];
 return ramp(mode==='post' ? 0.05 : remap(f.g));
}

function visible(){
 var w=C.width,h=C.height,s=Math.min(w,h)/16,cd=camDir();
 return DATA.faces.map(function(f){
   var pts=f.v.map(function(p){return proj(p,w,h,s);});
   return {f:f,pts:pts,d:(pts[0].d+pts[1].d+pts[2].d)/3,nm:outward(f.v,[cx,cy,cz])};
 }).filter(function(t){
   if(t.nm[0]*cd[0]+t.nm[1]*cd[1]+t.nm[2]*cd[2] <= -0.02) return false;  // backface
   var p=t.pts;                                                          // off-canvas
   var x0=Math.min(p[0].x,p[1].x,p[2].x), x1=Math.max(p[0].x,p[1].x,p[2].x);
   var y0=Math.min(p[0].y,p[1].y,p[2].y), y1=Math.max(p[0].y,p[1].y,p[2].y);
   return x1>=0 && x0<=w && y1>=0 && y0<=h;
 });
}

// Contrast stretch: remap the ramp across the range actually on screen. Grime
// varies within a zone by ~15 points, so on the absolute ramp real structure
// renders as one flat-looking band. This is an ANALYSIS aid — every number
// printed elsewhere stays absolute.
function remapper(all){
 var lo=0, hi=1;
 if(stretch && (mode==='dirt'||mode==='thermal')){
   var vals=all.filter(function(t){return !t.f.excl;})
               .map(function(t){return mode==='thermal'?(t.f.temp-28)/32:t.f.g;});
   if(vals.length){
     lo=Math.min.apply(null,vals); hi=Math.max.apply(null,vals);
     if(hi-lo<0.04){lo=0;hi=1;}
   }
 }
 return function(v){return (hi>lo)?Math.max(0,Math.min(1,(v-lo)/(hi-lo))):v;};
}

function draw(){
 var w=C.width,h=C.height;
 X.clearRect(0,0,w,h);
 var all=visible();
 var remap=remapper(all);
 // Mesh edges only read as facets once faces are big enough; at 1x they just
 // grey the model out.
 var edges = zoom>=2.2;
 var tris=all.slice().sort(function(a,b){return b.d-a.d;});

 tris.forEach(function(t){
   var c=faceColor(t.f,remap);
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
   if(isSel||edges){
     X.strokeStyle=isSel?'rgba(255,255,255,.9)':'rgba(255,255,255,.07)';
     X.lineWidth=isSel?2:1;
   } else {
     X.strokeStyle=X.fillStyle; X.lineWidth=1;   // closes seams between triangles
   }
   X.stroke();
 });

 // zone labels — largest visible face per zone, skipping collisions
 var placed=[],best={};
 tris.forEach(function(t){
   var p=t.pts;
   var mx=(p[0].x+p[1].x+p[2].x)/3, my=(p[0].y+p[1].y+p[2].y)/3;
   // Anchor on a face whose centroid is on screen, or the label vanishes as soon
   // as you zoom past the edge of its biggest facet.
   if(mx<40||mx>w-40||my<30||my>h-30)return;
   var ar=Math.abs((p[1].x-p[0].x)*(p[2].y-p[0].y)-(p[2].x-p[0].x)*(p[1].y-p[0].y))/2;
   if(!best[t.f.zone]||ar>best[t.f.zone].ar)best[t.f.zone]={t:t,ar:ar,m:{x:mx,y:my}};
 });
 Object.keys(best).map(function(k){return best[k];})
  .sort(function(a,b){return b.ar-a.ar;})
  .forEach(function(e){
   var t=e.t, m=e.m;
   for(var i=0;i<placed.length;i++){
     if(Math.abs(placed[i].x-m.x)<130&&Math.abs(placed[i].y-m.y)<32)return;
   }
   placed.push(m);
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
   if(!(neg&&pos))return tris[i].f;
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
 var spread=(d.gMax||0)-(d.gMin||0);
 var patch='';
 if(selFace && !d.excl){
   var rel = selFace.g>d.g+0.01 ? Math.round((selFace.g-d.g)*100)+' pts above'
           : selFace.g<d.g-0.01 ? Math.round((d.g-selFace.g)*100)+' pts below'
           : 'level with';
   patch='<div class="patch"><div class="psw" style="background:rgb('+
     ramp(selFace.g).map(function(x){return x|0;}).join(',')+')"></div><div class="ptx">'+
     '<b>This patch: '+Math.round(selFace.g*100)+'% grime</b> &mdash; '+rel+
     ' the zone mean.<br>Measured on one mesh face at '+selFace.temp+
     ' &deg;C, not the zone average.</div></div>';
 }
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
   '<div class="chipwrap">'+chips+'</div>'+patch+rows+
   (spread>0.02 ? '<div class="row"><span>Spread across '+d.faces+
     ' faces</span><b>'+Math.round(d.gMin*100)+'&ndash;'+Math.round(d.gMax*100)+
     '%</b></div>' : '')+phase+
   '<div class="note">'+d.reason+'</div>';
}

// ── view controls ────────────────────────────────────────────────────────────
function clampPan(){
 var mx=C.width*0.45*(zoom-1)+C.width*0.25, my=C.height*0.45*(zoom-1)+C.height*0.25;
 panX=Math.max(-mx,Math.min(mx,panX)); panY=Math.max(-my,Math.min(my,panY));
}
// Zoom about a fixed screen point so whatever is under the cursor stays put.
function zoomAbout(f,px,py){
 var next=Math.max(ZMIN,Math.min(ZMAX,zoom*f));
 if(next===zoom)return;
 var ax=(px==null)?C.width/2:px, ay=(py==null)?C.height/2:py, k=next/zoom;
 panX=ax-C.width/2-(ax-C.width/2-panX)*k;
 panY=ay-C.height/2-(ay-C.height/2-panY)*k;
 zoom=next;
 if(zoom<=ZMIN+1e-6){panX=0;panY=0;}
 clampPan();
 document.getElementById('zb').innerHTML=zoom.toFixed(1)+'&times;';
 draw();
}
document.getElementById('zin').onclick=function(){zoomAbout(ZSTEP);};
document.getElementById('zout').onclick=function(){zoomAbout(1/ZSTEP);};
document.getElementById('zres').onclick=function(){
 zoom=1;panX=0;panY=0;
 document.getElementById('zb').innerHTML='1.0&times;';draw();};

var stBtn=document.getElementById('st');
stBtn.onclick=function(){
 stretch=!stretch;
 stBtn.classList.toggle('on',stretch);
 stBtn.setAttribute('aria-pressed',String(stretch));
 document.getElementById('sn').innerHTML = stretch
   ? 'colours stretched to the visible range &mdash; figures stay absolute'
   : 'colours on the absolute 0&ndash;100% scale';
 draw();
};

// ── pointer interaction ──────────────────────────────────────────────────────
function xy(e){var r=C.getBoundingClientRect(),t=e.touches?e.touches[0]:e;
 return {x:(t.clientX-r.left)/r.width*C.width,y:(t.clientY-r.top)/r.height*C.height};}
function touchMid(t){var r=C.getBoundingClientRect();
 return {x:((t[0].clientX+t[1].clientX)/2-r.left)/r.width*C.width,
         y:((t[0].clientY+t[1].clientY)/2-r.top)/r.height*C.height,
         d:Math.hypot(t[0].clientX-t[1].clientX,t[0].clientY-t[1].clientY)};}

function down(e){
 if(e.touches&&e.touches.length===2){pinch=touchMid(e.touches);drag=null;return;}
 var p=xy(e);
 drag={x:p.x,y:p.y,az:az,el:el,panX:panX,panY:panY,moved:0,pan:!!e.shiftKey};
}
function move(e){
 if(e.touches&&e.touches.length===2&&pinch){
   if(e.cancelable)e.preventDefault();
   var m=touchMid(e.touches);
   zoomAbout(m.d/pinch.d,m.x,m.y);
   panX+=m.x-pinch.x; panY+=m.y-pinch.y; clampPan(); pinch=m; draw();
   return;
 }
 if(!drag)return;
 if(e.cancelable)e.preventDefault();
 var p=xy(e),dx=p.x-drag.x,dy=p.y-drag.y;
 drag.moved+=Math.abs(dx)+Math.abs(dy);
 if(drag.pan){ panX=drag.panX+dx; panY=drag.panY+dy; clampPan(); }
 else { az=drag.az+dx*0.005; el=Math.max(0.12,Math.min(1.45,drag.el+dy*0.004)); }
 draw();
}
function up(e){
 pinch=null;
 var d=drag; drag=null;
 if(!d||d.moved>=6||d.pan)return;
 var p=xy(e.changedTouches?{touches:e.changedTouches}:e);
 var f=pick(p.x,p.y);
 if(!f){ sel=null; selFace=null; }
 else if(sel===f.zone && selFace===f){ sel=null; selFace=null; }
 else { sel=f.zone; selFace=f; }
 draw(); side();
}
C.addEventListener('mousedown',down);
window.addEventListener('mousemove',move);
window.addEventListener('mouseup',up);
C.addEventListener('wheel',function(e){
 e.preventDefault(); var p=xy(e);
 zoomAbout(Math.pow(ZSTEP,-e.deltaY/300),p.x,p.y);
},{passive:false});
C.addEventListener('touchstart',down,{passive:true});
C.addEventListener('touchmove',move,{passive:false});
C.addEventListener('touchend',up);

[].forEach.call(document.querySelectorAll('.mode'),function(b){
 b.onclick=function(){
  [].forEach.call(document.querySelectorAll('.mode'),function(o){o.classList.remove('on');});
  b.classList.add('on'); mode=b.dataset.m;
  document.getElementById('st').style.display=
    (mode==='dirt'||mode==='thermal')?'flex':'none';
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
