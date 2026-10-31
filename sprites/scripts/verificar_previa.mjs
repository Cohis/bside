// Verifica a página local em uma sessão headless de teste, sem tocar no navegador pessoal.
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const root=new URL('../',import.meta.url);
const portFile=process.env.SPRITES_CDP_PORT_FILE??'/tmp/aoc-sprites-cdp/DevToolsActivePort';
const port=(await fs.readFile(portFile,'utf8')).split('\n')[0];
const version=await(await fetch(`http://127.0.0.1:${port}/json/version`)).json();
const ws=new WebSocket(version.webSocketDebuggerUrl);await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject});
let seq=0;const pending=new Map(),erros=[];
ws.onmessage=({data})=>{const m=JSON.parse(data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(new Error(JSON.stringify(m.error))):p.resolve(m.result)}else if(m.method==='Runtime.exceptionThrown')erros.push(m.params.exceptionDetails)};
function call(method,params={},sessionId){const id=++seq;return new Promise((resolve,reject)=>{pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params,sessionId}))})}
const {targetId}=await call('Target.createTarget',{url:'about:blank'});
const {sessionId}=await call('Target.attachToTarget',{targetId,flatten:true});
const c=(method,params)=>call(method,params,sessionId);
const ev=async expression=>{const r=await c('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw new Error(JSON.stringify(r.exceptionDetails));return r.result.value};
try{
 await c('Runtime.enable');await c('Page.enable');
 await c('Emulation.setDeviceMetricsOverride',{width:1200,height:1100,deviceScaleFactor:1,mobile:false});
 await c('Page.navigate',{url:new URL('final/previa.html',root).href});
 for(let t=0;t<50;t++){if(await ev("document.readyState==='complete' && typeof D!=='undefined'"))break;await new Promise(r=>setTimeout(r,100))}
 const carregadas=await ev("[...imagens.values()].filter(i=>i.complete&&i.naturalWidth>0).length");assert.equal(carregadas,144);
 assert.equal(await ev('fase'),0);
 await ev("document.getElementById('proximo').click()");assert.equal(await ev('fase'),1);assert.equal(await ev('pausado'),true);
 await ev("document.getElementById('anterior').click()");assert.equal(await ev('fase'),8);
 await ev("document.getElementById('pausa').click()");
 const fases=await ev("new Promise(resolve=>{const a=[];const id=setInterval(()=>a.push(fase),25);setTimeout(()=>{clearInterval(id);resolve(a)},1100)})");assert.ok(!fases.includes(0));assert.equal(new Set(fases).size,8);
 await ev("document.getElementById('pausa').click();document.getElementById('velocidade').value='0.25';tempo=0;document.getElementById('pausa').click()");
 const inicio=await ev('fase');await new Promise(r=>setTimeout(r,160));assert.equal(await ev('fase'),inicio);
 await ev("document.getElementById('pausa').click();document.getElementById('personagem').value='eva';document.getElementById('personagem').dispatchEvent(new Event('change'));document.getElementById('direcao').value='oeste';document.getElementById('direcao').dispatchEvent(new Event('change'));document.getElementById('modo').value='parado';document.getElementById('modo').dispatchEvent(new Event('change'))");assert.equal(await ev('fase'),0);
 const before=await ev('distancia');await ev("document.getElementById('deslocar').checked=true;document.getElementById('modo').value='andar';document.getElementById('modo').dispatchEvent(new Event('change'));document.getElementById('pausa').click()");await new Promise(r=>setTimeout(r,200));assert.ok(await ev('distancia')>before);
 await ev("document.getElementById('pausa').click();document.getElementById('modo').value='parado';document.getElementById('modo').dispatchEvent(new Event('change'));document.getElementById('personagem').value='icaro';document.getElementById('personagem').dispatchEvent(new Event('change'));document.getElementById('direcao').value='sul';document.getElementById('direcao').dispatchEvent(new Event('change'))");
 await new Promise(r=>setTimeout(r,100));const ss=await c('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});await fs.writeFile(new URL('registros/previa-testada.png',root),Buffer.from(ss.data,'base64'));
 await ev("document.getElementById('modo').value='andar';document.getElementById('modo').dispatchEvent(new Event('change'));document.getElementById('guias').checked=true");
 assert.equal(await ev("desenharRastreamento(D.personagens.icaro.sul,1,348,35)"),true);
 assert.equal(await ev("desenharRastreamento(D.personagens.eva.oeste,1,348,35)"),true);
 await new Promise(r=>setTimeout(r,60));assert.equal(await ev("document.getElementById('revisao').textContent.startsWith(D.personagens.icaro.sul.revisao.aprovado?'Ciclo aprovado.':'Ciclo ainda não aprovado.')"),true);
 assert.equal(erros.length,0);
 const r={imagens_carregadas:carregadas,quadros_loop:[...new Set(fases)].sort(),verificacoes:['carregamento PNG','parado fora do loop','avanço 0→1','retorno 1→8','pausa','ciclo com 8 fases','velocidade lenta','troca de personagem/direção','deslocamento no chão','rastreamento estimado do sul','pendências visíveis'],erros_javascript:erros};
 await fs.writeFile(new URL('registros/verificacao-previa.json',root),JSON.stringify(r,null,2)+'\n');console.log(JSON.stringify(r));
}finally{await call('Target.closeTarget',{targetId});ws.close()}
