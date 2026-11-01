#!/usr/bin/env python3
"""Mobile-first watchlist with 50 editable starter symbols; no unverified price/order execution."""
from pathlib import Path

p=Path(__file__).resolve().parents[1]/"android/app/src/main/assets/index.html"
html=p.read_text(encoding="utf-8")
needle='<section id="watchlist" class="view">'
if needle not in html: raise SystemExit("Missing watchlist view")
if 'id="watchCards"' in html: raise SystemExit("Watchlist already upgraded")
start=html.index(needle)
end=html.index('</section>',start)+len('</section>')
new_view='''<section id="watchlist" class="view"><div class="sectionhead"><h3>My Watchlist</h3><span id="watchCount">50 starter companies</span></div>
<div class="market-strip"><div>NIFTY 50<strong>—</strong><small>Price not connected</small></div><div>NIFTY BANK<strong>—</strong><small>Price not connected</small></div><div>BSE SENSEX<strong>—</strong><small>Price not connected</small></div></div>
<div class="notice"><b>Market data: Not connected · Broker: Not connected.</b> Orders cannot be sent without authorised APIs.</div>
<div class="watch-toolbar"><label for="watchGroup">Watchlists</label><select id="watchGroup"></select><button id="newWatchGroup" class="btn" type="button">+ New list</button></div>
<div id="groupEditor" class="watch-edit" hidden><input id="groupName" maxlength="30" placeholder="New list name"><button id="makeGroup" class="btn primary" type="button">Create</button><button id="cancelGroup" class="btn" type="button">Cancel</button></div>
<div class="watch-toolbar"><input type="search" id="watchSearch" placeholder="Search company or symbol"><button id="openWatchAdd" class="btn primary" type="button">+ Add stock</button></div>
<div id="stockEditor" class="watch-edit" hidden><select id="stockExchange"><option value="NSE">NSE</option><option value="BSE">BSE</option></select><input id="stockSymbol" maxlength="22" placeholder="Stock symbol, e.g. TCS"><button id="addStock" class="btn primary" type="button">Add</button><button id="cancelAdd" class="btn" type="button">Cancel</button></div>
<div class="smallnote" id="watchStatus" role="status" aria-live="polite"></div><div id="watchCards" class="watch-cards"></div>
<div id="replaceEditor" class="watch-edit" hidden><input id="replacementSymbol" maxlength="28" placeholder="New symbol, e.g. NSE:TCS"><button id="saveReplacement" class="btn primary" type="button">Replace</button><button id="cancelReplacement" class="btn" type="button">Cancel</button></div>
<div id="orderPreview" class="watch-edit" hidden><b id="orderSymbol"></b><p>Order entry preview only. No live quote or broker API is connected. No trade can be placed.</p><label for="orderSide">Side</label><select id="orderSide"><option>BUY</option><option>SELL</option></select><label for="orderQuantity">Qty</label><input id="orderQuantity" type="number" min="1" value="1"><button class="btn" type="button" disabled>Place order — Unavailable</button><button id="closeOrderPreview" class="btn" type="button">Close</button></div>
<input id="watchInput" type="hidden"><button id="saveWatch" type="button" hidden>Legacy</button><p class="smallnote">Starter stocks are an editable example list. They are not live quotes or a claim about current index constituents.</p></section>'''
html=html[:start]+new_view+html[end:]
css='''<style>
.market-strip{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}.market-strip>div{padding:14px;background:white;color:#1b4e90;border-radius:14px;border:1px solid #bfcfe2;font-weight:800}.market-strip strong{display:block;font-size:25px;margin:4px 0}.market-strip small{color:#a54450;font-size:12px}
.watch-toolbar,.watch-edit{display:flex;flex-wrap:wrap;align-items:center;gap:9px;margin:14px 0}.watch-toolbar label{font-size:17px;font-weight:800}.watch-toolbar input,.watch-toolbar select,.watch-edit input,.watch-edit select{min-height:50px;min-width:100px;flex:1;border:1px solid #9aafc9;border-radius:10px;padding:10px;color:#173259;background:white;font-size:17px}.watch-edit[hidden]{display:none}
.watch-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}.watch-card{border-radius:17px;background:white;border:1px solid #d1dfee;padding:17px;box-shadow:0 3px 12px #344b6314}.watch-top{display:flex;justify-content:space-between;gap:15px}.watch-top strong{font-size:20px;color:#1c2c49}.watch-quote{text-align:right;font-size:23px;font-weight:850;color:#253d5f}.watch-quote small,.watch-exchange{display:block;font-size:13px;color:#6e7c92;margin-top:6px}.watch-buttons{display:flex;gap:7px;margin-top:16px}.watch-buttons button{min-height:45px;flex:1;font-size:14px;font-weight:800}
#orderPreview{border:1px solid #ccd8e9;background:white;border-radius:14px;padding:17px}#orderPreview p{width:100%;font-size:15px}#orderPreview button:disabled{opacity:.5}
@media(max-width:700px){.market-strip{grid-template-columns:1fr 1fr}.market-strip>div:last-child{grid-column:1/-1}.watch-cards{grid-template-columns:1fr}.watch-toolbar input[type=search]{flex:1 1 100%}}
</style>'''
html=html.replace("</head>",css+"</head>",1)
js=r'''
const defaultStocks=['RELIANCE','HDFCBANK','ICICIBANK','INFY','TCS','BHARTIARTL','SBIN','ITC','LT','AXISBANK','KOTAKBANK','HINDUNILVR','BAJFINANCE','ASIANPAINT','MARUTI','TITAN','SUNPHARMA','NTPC','POWERGRID','ULTRACEMCO','WIPRO','HCLTECH','TATAMOTORS','TATASTEEL','JSWSTEEL','ONGC','COALINDIA','INDUSINDBK','ADANIENT','ADANIPORTS','BAJAJFINSV','CIPLA','DRREDDY','EICHERMOT','GRASIM','HEROMOTOCO','HINDALCO','M&M','NESTLEIND','TECHM','BPCL','BRITANNIA','DIVISLAB','APOLLOHOSP','SHRIRAMFIN','TRENT','BEL','JIOFIN','SBILIFE','HDFCLIFE'];
function initWatchlists(){
 if(!Array.isArray(settings.watchlistGroups)||!settings.watchlistGroups.length){
  const seed=Array.isArray(settings.watchlist)&&settings.watchlist.length?settings.watchlist:defaultStocks.map(x=>'NSE:'+x);
  settings.watchlistGroups=[{name:'My Watchlist',symbols:seed}];settings.activeWatchIndex=0;
  localStorage.setItem('amiSettings',JSON.stringify(settings));
 }
 if(!Number.isInteger(settings.activeWatchIndex)||settings.activeWatchIndex<0||settings.activeWatchIndex>=settings.watchlistGroups.length)settings.activeWatchIndex=0;
}
function currentWatchlist(){initWatchlists();return settings.watchlistGroups[settings.activeWatchIndex]}
function validateCode(raw,exchange){
 let code=String(raw||'').trim().toUpperCase(),ex=exchange||'NSE';
 if(code.includes(':')){const a=code.split(':');ex=a[0];code=a[1]}
 return /^(NSE|BSE)$/.test(ex)&&/^[A-Z0-9&._-]{1,22}$/.test(code)?ex+':'+code:null;
}
function saveWatchlists(){
 settings.watchlist=currentWatchlist().symbols.slice();store();showWatchlists();
}
function showWatchlists(){
 const group=byId('watchGroup'),current=currentWatchlist(),q=byId('watchSearch').value.trim().toUpperCase();
 group.innerHTML='';settings.watchlistGroups.forEach((g,i)=>{let o=document.createElement('option');o.value=i;o.textContent=g.name;group.append(o)});
 group.value=settings.activeWatchIndex;byId('watchCount').textContent=current.symbols.length+' companies · '+current.name;
 let area=byId('watchCards');area.innerHTML='';
 const found=current.symbols.filter(x=>x.toUpperCase().includes(q));
 if(!found.length){let empty=document.createElement('p');empty.textContent='No matching companies. Use Add stock.';area.append(empty)}
 found.forEach(code=>{
  const symbol=validateCode(code);if(!symbol)return;
  const a=document.createElement('article');a.className='watch-card';
  const top=document.createElement('div');top.className='watch-top';
  const title=document.createElement('div'),price=document.createElement('div');price.className='watch-quote';
  const name=document.createElement('strong');name.textContent=symbol.split(':')[1];
  const ex=document.createElement('small');ex.className='watch-exchange';ex.textContent=symbol.split(':')[0]+' · EQ';
  title.append(name,ex);price.append(document.createTextNode('—'));
  const note=document.createElement('small');note.textContent='Not connected';price.append(note);
  top.append(title,price);a.append(top);
  const actions=document.createElement('div');actions.className='watch-buttons';
  [['ticket','Order ticket'],['replace','Replace'],['remove','Remove']].forEach(([action,label])=>{
    const btn=document.createElement('button');btn.type='button';btn.className=action==='ticket'?'btn primary':'btn';
    btn.dataset.action=action;btn.dataset.code=symbol;btn.textContent=label;actions.append(btn)
  });a.append(actions);area.append(a);
 });
}
let replaceCode=null;
byId('watchGroup').onchange=e=>{settings.activeWatchIndex=Number(e.target.value);saveWatchlists()};
byId('watchSearch').oninput=showWatchlists;
byId('newWatchGroup').onclick=()=>{byId('groupEditor').hidden=false};
byId('cancelGroup').onclick=()=>{byId('groupEditor').hidden=true};
byId('makeGroup').onclick=()=>{
 let name=byId('groupName').value.trim();
 if(!name||settings.watchlistGroups.some(x=>x.name.toLowerCase()===name.toLowerCase())){byId('watchStatus').textContent='Enter a unique list name.';return}
 settings.watchlistGroups.push({name:name.slice(0,30),symbols:[]});settings.activeWatchIndex=settings.watchlistGroups.length-1;
 byId('groupName').value='';byId('groupEditor').hidden=true;saveWatchlists();byId('watchStatus').textContent='List created.';
};
byId('openWatchAdd').onclick=()=>{byId('stockEditor').hidden=false};
byId('cancelAdd').onclick=()=>{byId('stockEditor').hidden=true};
byId('addStock').onclick=()=>{
 const code=validateCode(byId('stockSymbol').value,byId('stockExchange').value);
 if(!code){byId('watchStatus').textContent='Enter a valid NSE or BSE symbol.';return}
 if(currentWatchlist().symbols.includes(code)){byId('watchStatus').textContent='Already on watchlist.';return}
 currentWatchlist().symbols.push(code);byId('stockSymbol').value='';byId('stockEditor').hidden=true;saveWatchlists();byId('watchStatus').textContent=code+' added.';
};
byId('watchCards').onclick=e=>{
 const b=e.target.closest('button[data-action]');if(!b)return;
 const code=b.dataset.code,action=b.dataset.action,w=currentWatchlist();
 if(action==='remove'){w.symbols=w.symbols.filter(s=>s!==code);saveWatchlists();byId('watchStatus').textContent=code+' removed.'}
 if(action==='replace'){replaceCode=code;byId('replaceEditor').hidden=false;byId('replacementSymbol').focus()}
 if(action==='ticket'){byId('orderPreview').hidden=false;byId('orderSymbol').textContent=code+' · LTP unavailable'}
};
byId('saveReplacement').onclick=()=>{
 const code=validateCode(byId('replacementSymbol').value),w=currentWatchlist();
 if(!code||w.symbols.includes(code)){byId('watchStatus').textContent='Enter a different valid symbol.';return}
 const pos=w.symbols.indexOf(replaceCode);if(pos<0)return;
 w.symbols[pos]=code;replaceCode=null;byId('replaceEditor').hidden=true;saveWatchlists();
};
byId('cancelReplacement').onclick=()=>{replaceCode=null;byId('replaceEditor').hidden=true};
byId('closeOrderPreview').onclick=()=>byId('orderPreview').hidden=true;
document.querySelector('[data-page="watchlist"]').addEventListener('click',showWatchlists);
initWatchlists();showWatchlists();
'''
anchor='inputVals();render();schedule();if(settings.endpoint)refresh();'
if html.count(anchor)!=1: raise SystemExit("JS init point changed")
html=html.replace(anchor,js+'\n'+anchor,1)
p.write_text(html,encoding="utf-8")
print("Prepared 50-stock watchlist UI; order execution intentionally unavailable")
