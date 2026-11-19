// 铅笔素描本 · SK kit（GSAP）。横竖屏通用：画布尺寸读 <svg> 的 width/height。
// 用法：SK.page(svg, {accent}) → 建时间轴 → SK.draw/write/show/drop/pop/cam/boil → SK.mount(tl, D)
// 渲染：scripts/sk_render.mjs 逐帧调用 window.render(t)，时长读 window.DUR
(function(g){
var SK={};
SK.G='#07C160';            // 唯一彩色（重音）。默认鲜绿；其他项目可在 SK.page 里传 accent
SK.INK='#34322E'; SK.DIM='#6B675E'; SK.LEAD='#3E3C38'; SK.PAPER='#F6F3EA';
SK.W=1080; SK.H=1920;
// ── 画风预设 ───────────────────────────────────────────────
// 同一个镜头换一个 style 就是另一种画风。说明和适用场景见 references/sketch-styles.md
// wob: 线条抖动强度（0 = 干净矢量）  grain: 线条有没有石墨/粉笔颗粒  fill: 色块怎么上
SK.STYLES={
 pencil:{name:'铅笔素描本',paper:'#F6F3EA',ink:'#34322E',lead:'#3E3C38',dim:'#6B675E',C:['#07C160'],bg:'notebook',wob:1,grain:1,fill:'hatch',lw:5,font:'"Hannotate SC","Wawati SC",cursive',body:'line'},
 journal:{name:'手账平涂',paper:'#FBF7EF',ink:'#2E2C2A',lead:'#2E2C2A',dim:'#8A847A',C:['#F6C85F','#8FD3B6','#F4A6A6','#8DB8E8'],bg:'dots',wob:.3,grain:0,fill:'flat',lw:4.5,shadow:1,font:'"Alimama FangYuanTi VF","Yuanti SC","PingFang SC",sans-serif',weight:700,body:'block'},
 kraft:{name:'牛皮纸涂鸦',paper:'#F1E8D5',ink:'#4A4235',lead:'#4A4235',dim:'#8C7F68',C:['#D49A3F','#C0533A','#7E9C7A','#E8C66E'],bg:'kraft',wob:1.1,grain:0,fill:'offset',lw:6,font:'"Hannotate SC","Wawati SC",cursive',body:'line'},
 mono:{name:'单色圆角',paper:'#F2E9DE',ink:'#5A3A26',lead:'#5A3A26',dim:'#A08670',C:['#5A3A26','#C9814A'],bg:'vignette',wob:0,grain:0,fill:'solid',lw:8,font:'"Alimama FangYuanTi VF","Yuanti SC","PingFang SC",sans-serif',weight:700,body:'line'},
 chalk:{name:'黑板粉笔',paper:'#232C29',ink:'#ECEAE2',lead:'#ECEAE2',dim:'#98A29C',C:['#F2D06B','#F29C8E','#9ED7C3'],bg:'board',wob:.9,grain:1,fill:'hatch',lw:5,font:'"Hannotate SC","Wawati SC",cursive',body:'line'}
};
SK.ST=SK.STYLES.pencil; SK.C=SK.ST.C.slice(); SK.FONT=SK.ST.font;
SK.page=function(svg,opt){
  opt=opt||{};
  var st=SK.ST=Object.assign({},SK.STYLES[opt.style||'pencil']||SK.STYLES.pencil,opt.override||{});
  SK.PAPER=st.paper; SK.INK=st.ink; SK.LEAD=st.lead; SK.DIM=st.dim; SK.FONT=st.font;
  SK.C=(opt.accents||st.C).slice(); if(opt.accent) SK.C[0]=opt.accent; SK.G=SK.C[0];
  var W=SK.W=+svg.getAttribute('width')||1080, H=SK.H=+svg.getAttribute('height')||1920;
  var fx='filterUnits="userSpaceOnUse" x="-400" y="-400" width="'+(W+800)+'" height="'+(H+800)+'"';
  var w=st.wob, full='x="-400" y="-400" width="'+(W+800)+'" height="'+(H+800)+'"';
  var grain=st.grain?'<feTurbulence type="fractalNoise" baseFrequency="1.1" numOctaves="2" seed="1" result="g"/><feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.4 1.15" result="gm"/><feComposite in="d" in2="gm" operator="in"/>':'';
  var bg='';
  if(st.bg==='notebook'||st.bg==='dots'){
    var dc=st.bg==='dots'?'#DCD4C6':'#C9C3B4', sp=st.bg==='dots'?32:36;
    bg='<rect '+full+' fill="'+st.paper+'"/><rect '+full+' fill="url(#grid)"/><rect '+full+' filter="url(#paper)"/>';
    if(st.bg==='notebook'){var ring=[]; for(var y=200;y<H;y+=260) ring.push('<path d="M0 '+y+' q34 -10 34 20 q0 26 -34 18"/>'); bg+='<g fill="none" stroke="#9A968C" stroke-width="5">'+ring.join('')+'</g>';}
  } else if(st.bg==='kraft'){
    bg='<rect '+full+' fill="'+st.paper+'"/><rect '+full+' filter="url(#paper)"/><rect '+full+' filter="url(#fiber)"/>';
  } else if(st.bg==='vignette'){
    bg='<rect '+full+' fill="'+st.paper+'"/><rect '+full+' fill="url(#vig)"/>';
  } else if(st.bg==='board'){
    bg='<rect '+full+' fill="'+st.paper+'"/><rect '+full+' filter="url(#smudge)"/><rect '+full+' filter="url(#paper)" opacity=".6"/>';
  } else bg='<rect '+full+' fill="'+st.paper+'"/>';
  var dc2=st.bg==='dots'?'#D6CEBF':'#C9C3B4', sp2=st.bg==='dots'?32:36;
  var paperMx=st.bg==='board'?'0 0 0 0 .9  0 0 0 0 .9  0 0 0 0 .88  0 0 0 .05 0':st.bg==='kraft'?'0 0 0 0 .35  0 0 0 0 .28  0 0 0 0 .18  0 0 0 .16 0':'0 0 0 0 .3  0 0 0 0 .28  0 0 0 0 .24  0 0 0 .08 0';
  svg.insertAdjacentHTML('afterbegin',
  '<defs>'+
  '<pattern id="grid" width="'+sp2+'" height="'+sp2+'" patternUnits="userSpaceOnUse"><circle cx="'+sp2/2+'" cy="'+sp2/2+'" r="2" fill="'+dc2+'"/></pattern>'+
  '<filter id="paper" x="0" y="0" width="'+W+'" height="'+H+'" filterUnits="userSpaceOnUse"><feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="3" seed="4"/><feColorMatrix type="matrix" values="'+paperMx+'"/></filter>'+
  '<filter id="fiber" x="0" y="0" width="'+W+'" height="'+H+'" filterUnits="userSpaceOnUse"><feTurbulence type="fractalNoise" baseFrequency=".012 .09" numOctaves="2" seed="9"/><feColorMatrix type="matrix" values="0 0 0 0 .45  0 0 0 0 .36  0 0 0 0 .22  0 0 0 .22 -.04"/></filter>'+
  '<filter id="smudge" x="0" y="0" width="'+W+'" height="'+H+'" filterUnits="userSpaceOnUse"><feTurbulence type="fractalNoise" baseFrequency=".004 .012" numOctaves="3" seed="12"/><feColorMatrix type="matrix" values="0 0 0 0 .9  0 0 0 0 .92  0 0 0 0 .9  0 0 0 .16 -.03"/></filter>'+
  '<radialGradient id="vig" cx="50%" cy="46%" r="75%"><stop offset="55%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#5A3A26" stop-opacity=".13"/></radialGradient>'+
  '<filter id="pencil" '+fx+'><feTurbulence type="fractalNoise" baseFrequency=".035" numOctaves="2" seed="7" result="w"/><feDisplacementMap in="SourceGraphic" in2="w" scale="'+(4*w)+'" result="d"/>'+grain+'</filter>'+
  '<filter id="pencil2" '+fx+'><feTurbulence type="fractalNoise" baseFrequency=".02" numOctaves="2" seed="31" result="w"/><feDisplacementMap in="SourceGraphic" in2="w" scale="'+(7*w)+'"/></filter>'+
  '<filter id="pen" '+fx+'><feTurbulence type="fractalNoise" baseFrequency=".05" numOctaves="2" seed="3"/><feDisplacementMap in="SourceGraphic" scale="'+(3*w)+'"/></filter>'+
  '<filter id="shadow" x="-10%" y="-10%" width="130%" height="130%"><feDropShadow dx="4" dy="8" stdDeviation="6" flood-opacity=".18"/></filter>'+
  '<pattern id="hatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(40)"><path d="M0 0v10" stroke="'+(st.bg==='board'?'#ECEAE2':'#55534E')+'" stroke-width="2.2"/></pattern>'+
  '<pattern id="ghatch" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)"><path d="M0 0v12" stroke="'+SK.G+'" stroke-width="3"/></pattern>'+
  '</defs>'+bg);
  SK._svg=svg;
};
// ── 通用画形：一套写法，按当前画风自动上色 ─────────────────────
SK.NS='http://www.w3.org/2000/svg';
SK.el=function(tag,a,parent){var n=document.createElementNS(SK.NS,tag);for(var k in a)n.setAttribute(k,a[k]);if(parent)parent.appendChild(n);return n;};
SK.rr=function(x,y,w,h,r){r=r||0;return 'M'+(x+r)+' '+y+' H'+(x+w-r)+' Q'+(x+w)+' '+y+' '+(x+w)+' '+(y+r)+' V'+(y+h-r)+' Q'+(x+w)+' '+(y+h)+' '+(x+w-r)+' '+(y+h)+' H'+(x+r)+' Q'+x+' '+(y+h)+' '+x+' '+(y+h-r)+' V'+(y+r)+' Q'+x+' '+y+' '+(x+r)+' '+y+' Z';};
SK.circ=function(cx,cy,r){return 'M'+(cx-r)+' '+cy+' a'+r+' '+r+' 0 1 0 '+(2*r)+' 0 a'+r+' '+r+' 0 1 0 '+(-2*r)+' 0 Z';};
SK._pat={};
SK.pat=function(color){ // 某个颜色的排线
  if(SK._pat[color]) return SK._pat[color];
  var id='h'+Object.keys(SK._pat).length, d=SK._svg.querySelector('defs');
  d.insertAdjacentHTML('beforeend','<pattern id="'+id+'" width="11" height="11" patternUnits="userSpaceOnUse" patternTransform="rotate(-38)"><path d="M0 0v11" stroke="'+color+'" stroke-width="'+(SK.ST.bg==='board'?3.4:3)+'"/></pattern>');
  return SK._pat[color]='url(#'+id+')';
};
// SK.shape(parent, d, {fill, lw, id, cls, shadow, noLine})
//   → {g, fill, ol}。ol 是轮廓（交给 SK.draw 一笔画出来），fill 是色块（SK.fillIn 显出来）
SK.shape=function(parent,d,o){
  o=o||{}; if(typeof parent==='string') parent=document.querySelector(parent);
  var st=SK.ST, g=SK.el('g',o.id?{id:o.id}:{},parent), f=null, sh=null;
  var wob=st.wob>0?'url(#pencil)':'none';
  if(o.shadow&&st.shadow) sh=SK.el('path',{d:d,fill:st.ink,transform:'translate(7 7)','class':'fl'},g);
  if(o.fill){
    if(st.fill==='hatch'){ SK.el('path',{d:d,fill:st.paper},g); f=SK.el('path',{d:d,fill:SK.pat(o.fill),opacity:.85,filter:wob,'class':'fl'},g); }
    else if(st.fill==='offset'){ SK.el('path',{d:d,fill:st.paper},g); f=SK.el('path',{d:d,fill:o.fill,transform:'translate(9 -7)','class':'fl'},g); }
    else f=SK.el('path',{d:d,fill:o.fill,'class':'fl'},g);
  } else if(o.paper!==false) SK.el('path',{d:d,fill:st.paper},g);
  var ol=o.noLine?null:SK.el('path',{d:d,fill:'none',stroke:o.stroke||st.ink,'stroke-width':o.lw||st.lw,'stroke-linecap':'round','stroke-linejoin':'round',filter:wob,'class':'ol '+(o.cls||'')},g);
  return {g:g,fill:f,ol:ol,shadow:sh};
};
// 一条线（箭头、下划线、对勾）
SK.line=function(parent,d,o){o=o||{}; if(typeof parent==='string') parent=document.querySelector(parent);
  return SK.el('path',{d:d,fill:'none',stroke:o.color||SK.INK,'stroke-width':o.lw||SK.ST.lw,'stroke-linecap':'round','stroke-linejoin':'round',filter:SK.ST.wob>0?'url(#pen)':'none','class':o.cls||'',id:o.id||''},parent);};
// 写字：字体跟画风走
SK.text=function(parent,x,y,str,o){o=o||{}; if(typeof parent==='string') parent=document.querySelector(parent);
  var g=SK.el('g',{filter:SK.ST.wob>0?'url(#pen)':'none'},parent);
  var t=SK.el('text',{x:x,y:y,'font-size':o.size||48,'font-weight':o.weight||SK.ST.weight||700,fill:o.color||SK.INK,'text-anchor':o.anchor||'start','class':o.cls||'',id:o.id||''},g);
  t.style.fontFamily=SK.FONT; if(o.rotate) t.setAttribute('transform','rotate('+o.rotate+' '+x+' '+y+')'); t.textContent=str; return t;};
// 色块显出来：手绘画风一拍二闪现，单色画风从中心长出来
SK.fillIn=function(tl,els,t,dur){
  els=[].concat(els).filter(Boolean);
  els.forEach(function(e,i){
    if(SK.ST.fill==='solid') tl.fromTo(e,{opacity:0,scale:.6,transformOrigin:'50% 50%',transformBox:'fill-box'},{opacity:1,scale:1,duration:dur||.35,ease:'power3.out'},t+i*.06);
    else tl.fromTo(e,{opacity:0},{opacity:1,duration:dur||.25,ease:'steps(3)'},t+i*.06);
  });
};
// 线一笔一笔画出来（path / ellipse / rect / line）
SK.$=function(sel){return typeof sel==='string'?document.querySelectorAll(sel):[].concat(sel).filter(Boolean);};
SK.draw=function(tl,sel,t,dur,stagger){
  SK.$(sel).forEach(function(p,i){
    var L=(p.getTotalLength?p.getTotalLength():1000)+4;
    p.style.strokeDasharray=L; p.style.strokeDashoffset=L;
    tl.to(p,{strokeDashoffset:0,duration:dur,ease:'power1.inOut'},t+i*(stagger||0));
  });
};
// 手写字从左往右写出来（clip-path，按 12fps 跳步，像一笔笔写）
SK.write=function(tl,sel,t,dur,stagger){
  SK.$(sel).forEach(function(el,i){
    tl.fromTo(el,{clipPath:'inset(-30% 100% -30% -2%)'},{clipPath:'inset(-30% -2% -30% -2%)',duration:dur,ease:'steps('+Math.max(4,Math.round(dur*12))+')'},t+i*(stagger||0));
  });
};
// 出现（一拍二）
SK.show=function(tl,sel,t,dur,to){
  tl.fromTo(sel,{opacity:0},{opacity:to==null?1:to,duration:dur||.25,ease:'steps(3)'},t);
};
// 纸片 / 截图贴上来：轻落 + 旋转
SK.drop=function(tl,sel,t,rot){
  tl.fromTo(sel,{opacity:0,y:-60,rotation:(rot||0)-6,transformOrigin:'50% 50%'},{opacity:1,y:0,rotation:rot||0,duration:.45,ease:'back.out(1.6)'},t);
};
// 小人弹出（只给整期第一次出场用）
SK.pop=function(tl,sel,t){
  tl.fromTo(sel,{scale:0,transformOrigin:'50% 100%'},{scale:1,duration:.4,ease:'back.out(2)'},t);
};
// 铅笔颤动：每 2 帧换一次噪声 seed（必须调用）
SK.boil=function(tl,D){
  var tur=['pencil','pen','pencil2'].map(function(id){return document.querySelector('#'+id+' feTurbulence')}).filter(Boolean);
  var base=tur.map(function(x){return +x.getAttribute('seed')});
  var o={t:0}; tl.to(o,{t:D,duration:D,ease:'none',onUpdate:function(){var k=Math.floor(o.t*15)%4;tur.forEach(function(x,i){x.setAttribute('seed',base[i]+k*7)})}},0);
};
// 镜头：把世界坐标 (cx,cy) 放到画面中心、缩放 s。cam.to({cx,cy,s}, dur, ease, at)
SK.cam=function(tl,sel,init){
  var el=document.querySelector(sel), st=Object.assign({cx:SK.W/2,cy:SK.H/2,s:1},init);
  function ap(){el.setAttribute('transform','translate('+(SK.W/2-st.cx*st.s)+','+(SK.H/2-st.cy*st.s)+') scale('+st.s+')')}
  ap(); return {to:function(tg,dur,ease,at){tl.to(st,Object.assign({duration:dur,ease:ease||'power2.inOut',onUpdate:ap},tg),at)}};
};
// 最后调用：撑满时长、暴露 render(t) / DUR / W / H 给渲染器
SK.mount=function(tl,D){ tl.to({},{duration:D},0); tl.pause(0);
  g.render=function(t){ tl.seek(Math.min(t,D-0.001),false); }; g.DUR=D; g.W=SK.W; g.H=SK.H; };
g.SK=SK;
})(window);
