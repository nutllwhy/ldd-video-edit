// Shared pencil stick figure, derived from the approved stick-sort shot.
(function(g){
const NS='http://www.w3.org/2000/svg';let INK='#2B2826',PAPER='#F6F3EA';
function el(tag,attrs={},parent){const n=document.createElementNS(NS,tag);for(const[k,v]of Object.entries(attrs))n.setAttribute(k,v);if(parent)parent.appendChild(n);return n;}
const q=n=>Number(n).toFixed(2);
function create(parent,opt={}){
 if(typeof parent==='string')parent=document.querySelector(parent);
 const id=opt.id||'actor',scale=opt.scale||1,ST=(g.SK&&g.SK.ST)||{};
 // 颜色、线宽、抖动跟当前画风走（SK.page 先调）。opt.body:'line' 线身体 | 'block' 色块身体（手账风）
 INK=opt.ink||(g.SK&&ST.ink)||'#2B2826';PAPER=opt.paper||(g.SK&&ST.paper)||'#F6F3EA';
 const LW=opt.lw||7,FIL=opt.filter||(ST.wob===0?'none':'url(#pen)'),BODY=opt.body||ST.body||'line',TW=opt.torsoW||104,SX=BODY==='block'?TW/2-12:14,TC=opt.color||(g.SK&&g.SK.C&&g.SK.C[2])||'#F4A6A6';
 const s={x:opt.x||600,y:opt.y||780,lean:0,tilt:0,hop:0,lx:0,ly:0,blink:0,happy:0,wide:0,mo:0,L:{x:-70,y:20},R:{x:70,y:20}};
 const off=[...id].reduce((a,c)=>a+c.charCodeAt(0),0)%7*.13;const group=el('g',{id},parent),body=el('g',{fill:'none',stroke:INK,'stroke-width':LW,'stroke-linecap':'round','stroke-linejoin':'round',filter:FIL},group);
 // 第一条 path 必须是脊柱（髋→脖子），arm_pose_check 靠它判断肘在哪一侧；色块身体时脊柱不可见
 el('path',{d:'M0 0 C2 -70 -2 -140 0 -200',stroke:BODY==='block'?'none':INK},body);
 if(BODY==='block'){const x=-TW/2,y=-206,w=TW,h=206,r=30;el('path',{d:`M${x+r} ${y} H${x+w-r} Q${x+w} ${y} ${x+w} ${y+r} V${y+h-14} Q${x+w} ${y+h} ${x+w-14} ${y+h} H${x+14} Q${x} ${y+h} ${x} ${y+h-14} V${y+r} Q${x} ${y} ${x+r} ${y} Z`,fill:TC,'stroke-width':LW*.75},body);}
 else{el('path',{d:'M-14 -168 L14 -168','stroke-width':LW*.86},body);}
 if(opt.legs)el('path',{d:BODY==='block'?`M${-TW/4} -6 L${-TW/4-6} 140 M${TW/4} -6 L${TW/4+6} 140`:'M0 0 Q-30 80 -60 145 M0 0 Q35 75 65 145'},body);

 const head=el('g',{},body);el('circle',{r:62,fill:PAPER},head);
 const eyes=el('g',{fill:INK,stroke:'none'},head);for(const x of [-22,22])el('circle',{cx:x,cy:-4,r:7},eyes);
 const close=el('path',{d:'M-30 -3 Q-22 2 -14 -3 M14 -3 Q22 2 30 -3','stroke-width':5},head);
 const happy=el('path',{d:'M-31 0 Q-22 -13 -13 0 M13 0 Q22 -13 31 0','stroke-width':5},head);
 const mouth=el('path',{transform:'translate(0 24)','stroke-width':5},head);
 const arms=el('g',{fill:'none',stroke:INK,'stroke-width':LW,'stroke-linecap':'round','stroke-linejoin':'round',filter:FIL},group);
 const paths={},dots={},hands={},metrics={};for(const k of ['L','R']){paths[k]=el('path',{},arms);dots[k]=el('circle',{r:9,fill:INK,stroke:'none'},arms);}
 function pt(x,y,breath,ln){const a=(ln===undefined?s.lean:ln)*Math.PI/180;return {x:x*Math.cos(a)-y*Math.sin(a),y:x*Math.sin(a)+y*Math.cos(a)+s.hop+breath};}
 function draw(t){
  const breath=Math.sin(t*2*Math.PI/2.6)*2.2,Lr=window.ARM_L||opt.armLength||110;
  // 够不着就让身体自己往那边探（真人伸手也是这样），胳膊最多伸到 86%，肘一直看得见
  const rk=(k,ln)=>{const sh=pt(k==='L'?-SX:SX,-168,breath,ln),tg=s[k];return [Math.hypot(tg.x-sh.x,tg.y-sh.y)/(2*Lr),Math.sign(tg.x-sh.x)]};
  let le=s.lean;for(let it=0;it<3;it++){let ex=0;for(const k of ['L','R']){const [r,dir]=rk(k,le);ex+=dir*Math.max(0,r-.82)*120;}le=s.lean+Math.max(-16,Math.min(16,(le-s.lean)*.5+ex*.5));}
  s.leanEff=le;
  group.setAttribute('transform',`translate(${q(s.x)} ${q(s.y)}) scale(${scale})`);
  body.setAttribute('transform',`translate(0 ${q(s.hop+breath)}) rotate(${q(le)})`);
  head.setAttribute('transform',`translate(0 -200) rotate(${q(s.tilt)}) translate(0 -66)`);
  let auto=0;for(const at of [.8,3.4,6.2].map(v=>v+off))auto=Math.max(auto,Math.max(0,1-Math.abs(t-at)/.08));
  const shut=Math.max(s.blink,auto)>.6,joy=s.happy>.5;
  eyes.setAttribute('transform',`translate(${q(s.lx*19)} ${q(s.ly*13)})`);eyes.setAttribute('opacity',shut||joy?0:1);
  for(const e of eyes.children)e.setAttribute('r',q(7*(1+s.wide*.4)));
  close.setAttribute('opacity',shut&&!joy?1:0);happy.setAttribute('opacity',joy?1:0);
  const m=Math.round(s.mo);mouth.setAttribute('transform',`translate(${q(s.lx*13)} ${q(24+s.ly*7)})`);close.setAttribute('transform',`translate(${q(s.lx*19)} ${q(s.ly*13)})`);happy.setAttribute('transform',`translate(${q(s.lx*15)} ${q(s.ly*9)})`);mouth.setAttribute('d',m===1?'M-7 4 a7 9 0 1 0 14 0 a7 9 0 1 0 -14 0':m===2?'M-17 -2 Q0 22 17 -2 Z':m===3?'M-12 7 Q0 -4 12 7':m===4?'M-12 3 Q0 1 12 3':'M-12 0 Q0 9 12 0');mouth.setAttribute('fill',m===2?INK:'none');
  for(const k of ['L','R']){
   const sh=pt(k==='L'?-SX:SX,-168,breath,le),tg=s[k],dx=tg.x-sh.x,dy=tg.y-sh.y,d=Math.hypot(dx,dy)||1,L=window.ARM_L||opt.armLength||110,dm=Math.max(1,Math.min(d,L*2-1)),th=Math.atan2(dy,dx),a=Math.acos(dm/(2*L)),side=k==='L'?-1:1,fix=k==='L'?opt.bendL:opt.bendR;
   // 肘往哪边弯：没指定就自动挑——肘朝外、朝下（举手指东西时肘在下面，垂手时肘在外侧）
   const eo=b=>({x:sh.x+L*Math.cos(th+b*a),y:sh.y+L*Math.sin(th+b*a)}),sc=e=>e.x*side+e.y*.5,bend=fix!=null?fix:(sc(eo(1))>=sc(eo(-1))?1:-1);
   const e=eo(bend),w={x:sh.x+dx/d*dm,y:sh.y+dy/d*dm};
   const rc=(a,b,r)=>{const dx=b.x-a.x,dy=b.y-a.y,l=Math.hypot(dx,dy)||1,m=Math.min(r,l*.4);return {x:b.x-dx/l*m,y:b.y-dy/l*m}},e1=rc(sh,e,18),e2=rc(w,e,18);paths[k].setAttribute('d',`M${q(sh.x)} ${q(sh.y)} L${q(e1.x)} ${q(e1.y)} Q${q(e.x)} ${q(e.y)} ${q(e2.x)} ${q(e2.y)} L${q(w.x)} ${q(w.y)}`);dots[k].setAttribute('cx',q(w.x));dots[k].setAttribute('cy',q(w.y));
   hands[k]={x:s.x+w.x*scale,y:s.y+w.y*scale};metrics[k]={reach:d,limit:L*2,shoulder:sh,elbow:e,wrist:w,armLength:L};
  }
 }
 const A={s,group,body,head,arms,draw,hand:k=>hands[k],metrics,scale,world:(x,y)=>({x:s.x+x*scale,y:s.y+y*scale})};(g.LDD_ACTORS=g.LDD_ACTORS||[]).push(A);return A;
}
function label(parent,{id,x,y,text,size=56,color='#2F8B78',rotate=-3}){
 if(typeof parent==='string')parent=document.querySelector(parent);
 const defs=document.querySelector('svg defs'),cp=el('clipPath',{id:id+'Clip',clipPathUnits:'userSpaceOnUse'},defs),rect=el('rect',{x:-12,y:-size*1.8,width:0,height:size*2.8},cp);
 const group=el('g',{id,transform:`translate(${x} ${y}) rotate(${rotate})`,filter:(g.SK&&g.SK.ST&&g.SK.ST.wob===0)?'none':'url(#pen)'},parent),clip=el('g',{'clip-path':`url(#${id}Clip)`},group),node=el('text',{x:0,y:0,'font-family':(g.SK&&g.SK.FONT)||'Hannotate SC','font-size':size,'font-weight':700,fill:color},clip);node.textContent=text;
 return {group,rect,width:node.getBBox().width+30};
}
function write(tl,label,at,dur=.45){tl.to(label.rect,{attr:{width:label.width},duration:dur,ease:'steps(6)'},at);}
g.LDD={create,label,write,el,q};
})(window);
