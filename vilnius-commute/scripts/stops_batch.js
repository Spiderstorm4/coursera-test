const { chromium } = require('playwright'); const fs=require('fs');
// input JSON: [{key, from:[lat,lon], to:[lat,lon], time:"HH:MM", mode:"arr"|"dep"}]
(async()=>{const Q=JSON.parse(fs.readFileSync(process.argv[2]));const out={};
const br=await chromium.launch();
for(const q of Q){
  const p=await br.newPage();
  try{
  await p.goto(`https://www.stops.lt/vilnius/#plan/${q.from[0]};${q.from[1]}/${q.to[0]};${q.to[1]}`,{waitUntil:'networkidle',timeout:60000});
  await p.waitForTimeout(800);
  const opts=await p.$$eval('#inputDate option',o=>o.map(x=>[x.value,x.text]));
  const v=opts.find(o=>o[1].includes('2026-11-18')); await p.selectOption('#inputDate',v[0]);
  await p.selectOption('#inputReverse',q.mode==='arr'?'-1':'1'); await p.fill('#inputTime',q.time);
  await p.click('#buttonSearch'); await p.waitForTimeout(4500);
  out[q.key]=await p.$eval('#divContentPlannerResults',e=>e.innerText).catch(async()=>await p.evaluate(()=>document.body.innerText));
  }catch(e){out[q.key]='ERROR '+e.message}
  await p.close(); process.stdout.write(q.key+' ');
}
fs.writeFileSync(process.argv[3],JSON.stringify(out,null,1));await br.close();})();
