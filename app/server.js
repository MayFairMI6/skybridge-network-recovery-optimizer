const http = require('http');
const fs = require('fs');
const path = require('path');

const port = process.env.PORT || 3000;
const build = process.env.APP_BUILD || 'local';
const dataDir = path.join(__dirname, '..', 'data');
const networkData = {
  passengers: JSON.parse(fs.readFileSync(path.join(dataDir, 'passengers.json'), 'utf8')),
  flights: JSON.parse(fs.readFileSync(path.join(dataDir, 'flights.json'), 'utf8')),
  network: JSON.parse(fs.readFileSync(path.join(dataDir, 'network.json'), 'utf8'))
};

http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(`<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SkyBridge Network Recovery Optimizer</title>
  <style>
    :root { --ink:#ecf3ff; --muted:#aabbd5; --panel:#121f36; --line:#2c4164; --blue:#53a9ff; --mint:#4be1b1; --warn:#ffc465; --danger:#ff7184; }
    * { box-sizing:border-box } body { margin:0; background:#091426; color:var(--ink); font-family:Inter, ui-sans-serif,system-ui,-apple-system,sans-serif; }
    main { max-width:1300px; margin:auto; padding:28px; } header { display:flex; justify-content:space-between; gap:18px; align-items:flex-start; margin-bottom:25px }
    h1 { margin:0; font-size:clamp(1.7rem,4vw,2.7rem); letter-spacing:-.05em } h2 { margin:0 0 14px; font-size:1rem } .eyebrow { color:var(--mint); font-weight:700; text-transform:uppercase; letter-spacing:.12em; font-size:.72rem; margin:0 0 8px }
    .build { border:1px solid var(--line); padding:8px 12px; border-radius:20px; color:var(--muted); white-space:nowrap; font-size:.82rem }
    .grid { display:grid; grid-template-columns:1.15fr .85fr; gap:18px }.panel { background:linear-gradient(150deg,#152541,#101c31); border:1px solid var(--line); border-radius:18px; padding:20px; box-shadow:0 16px 35px #02071366 }
    .status { display:flex; align-items:center; gap:9px; color:#ffd28a; margin:7px 0 20px }.dot { width:9px; height:9px; border-radius:50%; background:var(--warn); box-shadow:0 0 12px var(--warn) }
    .route { display:flex; gap:10px; align-items:center; flex-wrap:wrap }.hub { padding:10px 13px; border-radius:10px; background:#193359; border:1px solid #3566a1; font-weight:700 }.arrow { color:var(--blue); font-size:1.25rem }.small { font-size:.84rem; color:var(--muted); line-height:1.55 }
    .metrics { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-top:20px }.metric { background:#0c182b; border-radius:11px; padding:12px }.metric b { display:block; font-size:1.18rem; margin-top:3px }.metric span { font-size:.72rem; color:var(--muted) }
    .controls { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:13px } label { font-size:.8rem;color:var(--muted) } input { width:100%; accent-color:var(--blue); margin-top:8px } select { margin-top:7px;width:100%;border-radius:8px;border:1px solid var(--line);background:#0b1729;color:var(--ink);padding:9px }
    button { background:linear-gradient(135deg,#308be9,#55b4ff); color:#06152a; border:0; border-radius:10px; padding:12px 15px; font-weight:800; cursor:pointer; margin-top:18px; width:100% } button:hover { filter:brightness(1.1) }
    .full { margin-top:18px }.recommend { border-left:4px solid var(--mint); background:#102d35; padding:15px; border-radius:0 12px 12px 0; margin-bottom:16px }.recommend strong { font-size:1.15rem; display:block }.recommend p { margin:6px 0 0; color:#c2d6e9; font-size:.88rem;line-height:1.45 }
    table { width:100%; border-collapse:collapse; font-size:.84rem } th { color:var(--muted); text-align:left; font-weight:600; font-size:.72rem; text-transform:uppercase; letter-spacing:.04em } td,th { padding:11px 8px; border-bottom:1px solid #263b5b } tr.best { background:#123d47 } .cost { font-weight:800 }.tag { padding:3px 7px;border-radius:20px;background:#243752;color:#c9dcf5;font-size:.72rem }.green { color:var(--mint) }.red { color:var(--danger) }
    .passengers { display:grid; grid-template-columns:repeat(2,1fr); gap:10px }.passenger { background:#0d1a2f;border:1px solid #203758;padding:12px;border-radius:11px }.passenger b { font-size:.86rem }.passenger div { margin-top:4px;font-size:.76rem;color:var(--muted) }.priority { color:#ffcf76;font-size:.7rem;text-transform:uppercase;font-weight:800 }.policy { display:grid;grid-template-columns:repeat(3,1fr);gap:10px }.policy div,.fare { background:#0c182b;border:1px solid #263d5d;border-radius:11px;padding:12px }.policy b,.fare b { display:block;margin:4px 0;font-size:1.05rem }.policy small,.fare small { color:var(--muted);line-height:1.35;display:block }.pricegrid { display:grid;grid-template-columns:repeat(7,1fr);gap:7px }.fare { padding:10px 7px }.fare.active { border-color:#4be1b1;background:#10343d }.fare strong { display:block;color:var(--mint);font-size:.92rem }.fare small { font-size:.67rem;margin-top:4px }.horizon { display:flex;gap:8px;flex-wrap:wrap;margin:0 0 12px }.horizon span { font-size:.72rem;border-radius:20px;padding:5px 9px;border:1px solid #2f476a;color:var(--muted) }.horizon .active { color:#061b21;background:var(--mint);border-color:var(--mint);font-weight:800 } @media(max-width:800px){.pricegrid{grid-template-columns:repeat(4,1fr)}.policy{grid-template-columns:1fr}}
    footer { color:#8295b2;font-size:.76rem;margin-top:16px;line-height:1.45 }.live { color:var(--mint);font-size:.78rem;margin-top:12px } @media(max-width:800px){.grid{grid-template-columns:1fr}.metrics{grid-template-columns:1fr 1fr}.passengers{grid-template-columns:1fr}main{padding:17px}}
  </style>
</head>
<body><main>
  <header><div><p class="eyebrow">Airline Operations Control · Decision-support simulation</p><h1>SkyBridge Network Recovery Optimizer</h1></div><div class="build">Jenkins build ${build}</div></header>
  <section class="grid">
    <div class="panel"><h2>Disruption scenario</h2><div class="status"><i class="dot"></i><b>Convective weather capacity restriction at JFK</b></div>
      <div class="route"><span class="hub">SFO</span><span class="arrow">→</span><span class="hub" id="routeHub">JFK · constrained hub</span><span class="arrow">→</span><span class="hub">LHR</span><span class="arrow">→</span><span class="hub">DEL</span></div>
      <p class="small">The optimizer evaluates an uncertain 2–6 hour weather event, reduced hub capacity, turbulence exposure, passenger connection feasibility, recovery inventory, and downstream revenue.</p><p class="live" id="liveWeather">● Live weather feed: loading…</p>
      <div class="metrics"><div class="metric"><span>Affected flights</span><b>8</b></div><div class="metric"><span>Protected itineraries</span><b>46</b></div><div class="metric"><span>High-risk connections</span><b>17</b></div></div>
    </div>
    <div class="panel"><h2>Optimizer settings</h2><div class="controls"><label>Disruption hub<select id="hub"><option>JFK — New York</option><option>ORD — Chicago</option><option>DFW — Dallas/Fort Worth</option><option>LHR — London Heathrow</option><option>DXB — Dubai</option><option>DOH — Doha</option><option>DEL — Delhi</option><option>SIN — Singapore</option><option>HKG — Hong Kong</option><option>NRT — Tokyo Narita</option><option>ICN — Seoul Incheon</option></select></label><label>Monte Carlo trials<select id="trials"><option value="250">250 trials</option><option value="500" selected>500 trials</option><option value="1000">1,000 trials</option></select></label><label>Risk aversion<input id="risk" type="range" min="0" max="1" step=".05" value=".55"><span id="riskLabel">55% tail-risk weight</span></label><label>Weather severity<input id="weather" type="range" min=".35" max="1" step=".05" value=".75"><span id="weatherLabel">75% forecast severity</span></label></div><button id="run">Run stochastic recovery optimization</button><p class="small">Every run resamples weather duration, connection failures, recovery-seat availability, and new-demand revenue.</p></div>
  </section>
  <section class="panel full"><h2>Network action recommendation</h2><div class="recommend" id="recommend"><strong>Calculating recovery policy…</strong><p>Run complete results will appear here.</p></div><table><thead><tr><th>Candidate policy</th><th>Expected cost</th><th>95th percentile</th><th>Risk-adjusted score</th><th>Protected itineraries</th><th>Decision</th></tr></thead><tbody id="results"></tbody></table></section>
  <section class="grid full"><div class="panel"><h2>Regulated overbooking & recovery inventory</h2><p class="small">The model protects critical international connections. It seeks volunteers before any involuntary action and prioritizes flexible, local, low-priority itineraries for reaccommodation.</p><div class="policy" id="overbook"></div></div><div class="panel"><h2>7-day recovery & revenue horizon</h2><div class="horizon"><span class="active">0–72 hours · active optimizer</span><span>Days 4–7 · controlled forecast</span></div><p class="small">During the first 72 hours, affected passengers receive fare protection while the system manages holds, rebooking, hotel and recovery seats. Days 4–7 use capped new-sale prices and inventory forecasts.</p><div class="pricegrid" id="pricing"></div></div></section>
  <section class="grid full"><div class="panel"><h2>Multi-leg passenger recovery queue</h2><div class="passengers" id="passengers"></div></div><div class="panel"><h2>How the model is non-linear</h2><p class="small">Missed-connection probability follows an S-curve as delay exceeds available connection time. Compensation rises faster after long delays, hotel cost jumps once overnight recovery is required, and tail-risk penalizes severe scenarios beyond the average.</p><p class="small">This prototype uses stochastic simulation and a non-linear risk-adjusted objective. It is not a production airline dispatch system and uses simulated inventory, passenger, and cost data.</p></div></section>
  <footer>Research framing: dynamic disruption management under airport operating uncertainty. This classroom prototype uses simulated data and does not make real flight, pricing, or passenger decisions.</footer>
</main>
<script>
const networkData = ${JSON.stringify(networkData)};
const pax=networkData.passengers;
document.querySelector('#passengers').innerHTML=pax.map(p=>'<article class="passenger"><span class="priority">'+p[3]+' priority</span><b>'+p[0]+'</b><div>'+p[1]+'</div><div>'+p[2]+'</div></article>').join('');
const hubCoords={JFK:[40.64,-73.78],ORD:[41.98,-87.90],DFW:[32.90,-97.04],LHR:[51.47,-.45],DXB:[25.25,55.36],DOH:[25.27,51.61],DEL:[28.56,77.10],SIN:[1.36,103.99],HKG:[22.31,113.91],NRT:[35.77,140.39],ICN:[37.46,126.44]};
async function updateLiveWeather(){const code=document.querySelector('#hub').value.split(' ')[0],coord=hubCoords[code];document.querySelector('#routeHub').textContent=code+' · constrained hub';try{const url='https://api.open-meteo.com/v1/forecast?latitude='+coord[0]+'&longitude='+coord[1]+'&current=temperature_2m,wind_gusts_10m,precipitation,weather_code&wind_speed_unit=mph';const data=await fetch(url).then(r=>r.json());const c=data.current||{};const liveRisk=Math.min(1,Math.max(.35,(c.wind_gusts_10m||0)/70+(c.precipitation||0)/8+((c.weather_code||0)>=80 ? .25 : 0)+((c.weather_code||0)>=95 ? .4 : 0)));document.querySelector('#weather').value=liveRisk.toFixed(2);document.querySelector('#weatherLabel').textContent=Math.round(liveRisk*100)+'% live forecast severity';document.querySelector('#liveWeather').textContent='● Live Open-Meteo feed: '+Math.round(c.temperature_2m||0)+'° · gusts '+Math.round(c.wind_gusts_10m||0)+' mph · precipitation '+(c.precipitation||0)+' mm';run();}catch(e){document.querySelector('#liveWeather').textContent='● Live weather unavailable — using simulated severity';}}
function money(n){return '$'+Math.round(n).toLocaleString()}
function logistic(x){return 1/(1+Math.exp(-x))}
function normal(){let u=0,v=0;while(!u)u=Math.random();while(!v)v=Math.random();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v)}
const policies=[
 {name:'Hold 90 minutes',type:'hold',hold:90},{name:'Hold 180 minutes',type:'hold',hold:180},{name:'Cancel + same-day rebook',type:'cancel'},{name:'Overnight protect + hotel',type:'hotel'},{name:'Hybrid: protect long-haul, rebook others',type:'hybrid'}
];
function sample(policy,severity){
 const duration=Math.max(1.5,2.1+severity*3.4+normal()*.85); const capacity=Math.max(.18,1-severity*.64+normal()*.09); const turbulence=Math.max(.15,severity*.72+normal()*.14); const inventory=Math.max(.12,.61-severity*.25+normal()*.13); const demand=Math.max(.1,.5+normal()*.22);
 let operational=0, passenger=0, hotel=0, partner=0, lost=0, recovered=0;
 if(policy.type==='hold'){ const h=policy.hold; operational=5600*Math.pow(h/60,1.35)*(1+.12*duration)+1700*turbulence; const missed=logistic((h-(65+inventory*105))/27); passenger=46*(110*Math.pow(h/60,1.42)+820*Math.pow(missed,1.35)); hotel=46*missed*logistic((duration-3.8)*1.7)*205; recovered=46*(1-missed*.55); lost=(1-inventory)*19000; }
 if(policy.type==='cancel'){ operational=12400+3300*(1-capacity); const unrebooked=1-inventory*.86; partner=46*inventory*(360+160*turbulence); passenger=46*(unrebooked*1175+230); hotel=46*unrebooked*.45*225; recovered=46*(1-unrebooked); lost=17500*(1-demand*.42); }
 if(policy.type==='hotel'){ operational=8400+1900*duration; hotel=46*235*(1+.18*duration); passenger=46*(420+190*Math.pow(duration,1.25)); recovered=46*.93; lost=13700*(1-demand*.38); }
 if(policy.type==='hybrid'){ const longhaul=18; const shorthaul=28; operational=9750+2900*Math.pow(duration,1.2); const longMiss=logistic((100-(70+inventory*110))/28); const shortUn=1-inventory*.9; passenger=longhaul*(560+850*Math.pow(longMiss,1.4))+shorthaul*(260+980*Math.pow(shortUn,1.25)); hotel=longhaul*longMiss*.52*235; partner=(longhaul*(1-longMiss)+shorthaul*inventory)*310; recovered=longhaul*(1-longMiss*.3)+shorthaul*(1-shortUn); lost=10600*(1-demand*.48); }
 // Lost sales are a benefit: protected passengers consume capacity, but unused recovery seats may sell at a non-linear price.
 const fareMultiplier=1+Math.min(.15,Math.pow(demand,1.35)*.16)-severity*.07;
 const resale=Math.pow(Math.max(0,inventory-.28),1.18)*demand*14200*fareMultiplier;
 // Voluntary offers and compensation rise non-linearly when constrained recovery seats create an overbooking conflict.
 const excess=Math.max(0,16*(1-inventory)-5); const regulatedReaccommodation=560*Math.pow(excess,1.32);
 const total=operational+passenger+hotel+partner+lost+regulatedReaccommodation-resale;
 return {total,recovered};
}
function quantile(a,q){const b=[...a].sort((x,y)=>x-y);return b[Math.floor((b.length-1)*q)]}
function run(){ const trials=+document.querySelector('#trials').value, severity=+document.querySelector('#weather').value, risk=+document.querySelector('#risk').value; const rows=policies.map(p=>{let vals=[],pro=[];for(let i=0;i<trials;i++){let s=sample(p,severity);vals.push(s.total);pro.push(s.recovered)}const mean=vals.reduce((a,b)=>a+b,0)/trials,p95=quantile(vals,.95),tail=vals.filter(x=>x>=p95).reduce((a,b)=>a+b,0)/Math.max(1,vals.filter(x=>x>=p95).length);return {...p,mean,p95,score:mean*(1-risk)+tail*risk,protected:pro.reduce((a,b)=>a+b,0)/trials};}).sort((a,b)=>a.score-b.score);
 const best=rows[0], hub=document.querySelector('#hub').value.split(' ')[0]; document.querySelector('#recommend').innerHTML='<strong>Recommend: '+best.name+'</strong><p>For the '+hub+' disruption scenario, this policy has the lowest risk-adjusted network cost at <b>'+money(best.score)+'</b>. It protects an expected <b>'+best.protected.toFixed(0)+' of 46 itineraries</b> while accounting for severe-delay tail scenarios.</p>';
 document.querySelector('#results').innerHTML=rows.map((r,i)=>'<tr class="'+(!i?'best':'')+'"><td><b>'+r.name+'</b></td><td class="cost">'+money(r.mean)+'</td><td>'+money(r.p95)+'</td><td class="'+(!i?'green':'')+'">'+money(r.score)+'</td><td>'+r.protected.toFixed(1)+' / 46</td><td>'+(i===0?'<span class="tag">Recommended</span>':'<span class="tag">Alternative</span>')+'</td></tr>').join(''); }
 const volunteer=Math.max(2,Math.round(3+severity*3-Math.random()*2)), protectedSeats=Math.round(14+severity*5), standby=Math.max(1,Math.round(7-severity*3));
 document.querySelector('#overbook').innerHTML='<div><small>1. Protect</small><b>'+protectedSeats+' priority seats</b><small>Multi-leg international, medical, premium and tight-connection passengers cannot be displaced.</small></div><div><small>2. Ask volunteers</small><b>'+volunteer+' offers</b><small>Offer voucher, hotel, or same-day alternate itinerary before any involuntary step.</small></div><div><small>3. Reaccommodate</small><b>'+standby+' flexible guests</b><small>Lowest priority, local, flexible itineraries are ranked for the next safe option; compensation is included.</small></div>';
 const days=['Today','Day 2','Day 3','Day 4','Day 5','Day 6','Day 7']; const base=420; document.querySelector('#pricing').innerHTML=days.map((d,i)=>{const active=i<3;const lastMinute=active?1:1+(.035*Math.max(0,7-i))+Math.random()*.035;const cap=active?1:1.15;const factor=Math.min(cap,lastMinute*(1-severity*.06));const fare=Math.round(base*factor/5)*5;const rule=active?'Protected recovery fare':'Capped new-sale fare';return '<div class="fare '+(active?'active':'')+'"><small>'+d+'</small><strong>'+money(fare)+'</strong><small>'+rule+'</small></div>'}).join(''); }
document.querySelector('#run').onclick=run;document.querySelector('#hub').onchange=updateLiveWeather;document.querySelector('#risk').oninput=e=>document.querySelector('#riskLabel').textContent=Math.round(e.target.value*100)+'% tail-risk weight';document.querySelector('#weather').oninput=e=>document.querySelector('#weatherLabel').textContent=Math.round(e.target.value*100)+'% forecast severity';run();updateLiveWeather();
</script></body></html>`);
}).listen(port, () => console.log(`Listening on ${port}`));
