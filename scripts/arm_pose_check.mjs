#!/usr/bin/env node
// Scan LDD stick-figure geometry at 30 fps. This does NOT replace visual review.
// node arm_pose_check.mjs shot.html --out report.json
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';

const args = process.argv.slice(2);
if (args.length !== 3 || args[1] !== '--out') {
  console.error('usage: node arm_pose_check.mjs shot.html --out report.json');
  process.exit(2);
}
const shot = path.resolve(args[0]), out = path.resolve(args[2]);
const report = {
  shot, fps: 30, geometry_status: 'UNAVAILABLE', needs_visual_review: true,
  note: 'Geometry is only a risk screen. Inspect rendered poses, transitions and hand/prop contact before acceptance.',
  risks: [], unavailable_reasons: [], page_errors: []
};
function loadPW() {
  const tries = [process.env.PLAYWRIGHT_DIR, process.env.HYPERFRAMES_DIR, process.cwd()];
  try { tries.push(execSync('npm root -g', { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim().replace(/\/node_modules$/, '')); } catch {}
  for (const d of tries.filter(Boolean)) {
    try { return createRequire(path.join(d, 'package.json'))('playwright-core'); } catch {}
  }
  throw new Error('playwright-core unavailable; set PLAYWRIGHT_DIR to its parent package directory');
}
let browser;
try {
  const { chromium } = loadPW();
  const launchOptions = { args: ['--allow-file-access-from-files'] };
  if (process.env.CHROME) launchOptions.executablePath = process.env.CHROME;
  browser = await chromium.launch(launchOptions);
  const page = await browser.newPage({ viewport: { width: 1440, height: 1080 } });
  page.on('pageerror', e => report.page_errors.push(e.message));
  await page.goto(pathToFileURL(shot).href);
  await page.evaluate(() => document.fonts.ready);
  const size = await page.evaluate(() => ({ width: window.W, height: window.H }));
  if (Number.isFinite(size.width) && Number.isFinite(size.height)) await page.setViewportSize(size);
  const scan = await page.evaluate(() => {
    const fps = 30, duration = window.DUR;
    if (typeof window.render !== 'function' || !Number.isFinite(duration) || duration <= 0)
      return { unavailable_reasons: ['Requires window.render(t) and a positive window.DUR'] };
    if (!Array.isArray(window.LDD_ACTORS) || !window.LDD_ACTORS.length)
      return { duration, unavailable_reasons: ['No LDD_ACTORS; this checker cannot evaluate the character rig'] };
    const frames = Math.ceil(duration * fps), hits = [], missing = new Set(), actorIds = new Set();
    let checkedArmFrames = 0, maxReachRatio = 0;
    const finite = p => p && Number.isFinite(p.x) && Number.isFinite(p.y);
    const map = (p, m) => ({ x: p.x * m.a + p.y * m.c + m.e, y: p.x * m.b + p.y * m.d + m.f });
    const distance = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
    function project(p, a, b) {
      const dx = b.x - a.x, dy = b.y - a.y, len2 = dx * dx + dy * dy;
      const u = len2 ? Math.max(0, Math.min(1, ((p.x-a.x)*dx+(p.y-a.y)*dy)/len2)) : 0;
      const q = { x: a.x+u*dx, y: a.y+u*dy };
      return { distance: distance(p,q), q, dx, dy };
    }
    function nearest(p, body) {
      let best = { distance: Infinity };
      for (let j=1; j<body.length; j++) { const q=project(p,body[j-1],body[j]); if(q.distance<best.distance)best=q; }
      return best;
    }
    function visible(node) {
      for(let n=node; n && n.nodeType===1; n=n.parentNode) {
        const s=getComputedStyle(n);
        if(s.display==='none'||s.visibility==='hidden'||Number(s.opacity)<.05)return false;
      }
      return true;
    }
    function risk(frame, actor, arm, code, evidence) { hits.push({ frame, actor, arm, code, evidence }); }
    for(let frame=0; frame<frames; frame++) {
      const t=Math.min(frame/fps,duration-.0001);
      try { window.render(t); } catch(e) { missing.add(`render failed at ${t.toFixed(3)}s: ${e.message}`); break; }
      for(let ai=0; ai<window.LDD_ACTORS.length; ai++) {
        const actor=window.LDD_ACTORS[ai], id=actor?.group?.id||`actor-${ai}`;actorIds.add(id);
        if(!actor?.group||!actor.body||!actor.head||!actor.arms||!actor.metrics) { missing.add(`${id}: unsupported LDD rig`);continue; }
        if(!visible(actor.group))continue;
        const matrix=actor.group.getScreenCTM(), bodyPath=actor.body.querySelector('path'), head=actor.head.querySelector('circle');
        const bodyMatrix=bodyPath?.getScreenCTM(), headMatrix=head?.getScreenCTM();
        if(!matrix||!bodyMatrix||!headMatrix||!bodyPath||!head) { missing.add(`${id}: missing body/head geometry`);continue; }
        const bodyLength=bodyPath.getTotalLength(), body=[];
        for(let j=0;j<=60;j++)body.push(map(bodyPath.getPointAtLength(bodyLength*j/60),bodyMatrix));
        const armPaths=Array.from(actor.arms.children).filter(n=>n.tagName.toLowerCase()==='path');
        const scale=Math.sqrt(Math.abs(matrix.a*matrix.d-matrix.b*matrix.c));
        const bodyStroke=Number.parseFloat(getComputedStyle(bodyPath).strokeWidth)||7;
        const nearPx=Math.max(5,bodyStroke*scale*1.35);
        const headInverse=headMatrix.inverse(), center={x:Number(head.getAttribute('cx')||0),y:Number(head.getAttribute('cy')||0)}, radius=Number(head.getAttribute('r'));
        for(const [ki,arm] of ['L','R'].entries()) {
          const m=actor.metrics[arm], armPath=armPaths[ki];
          if(!m||!finite(m.elbow)||!Number.isFinite(m.limit)||m.limit<=0||!Number.isFinite(m.reach)) { missing.add(`${id}/${arm}: incomplete metrics`);continue; }
          let shoulder=m.shoulder, wrist=m.wrist;
          // Older kit exports only elbow/reach/limit. Recover its shoulder path start
          // and its hand() coordinates, then express both in actor-local coordinates.
          if(!finite(shoulder)&&armPath) {
            const am=armPath.getScreenCTM();
            if(am)shoulder=map(map(armPath.getPointAtLength(0),am),matrix.inverse());
          }
          if(!finite(wrist)&&typeof actor.hand==='function'&&actor.s&&Number.isFinite(actor.scale)&&actor.scale!==0) {
            const h=actor.hand(arm);
            if(finite(h))wrist={x:(h.x-actor.s.x)/actor.scale,y:(h.y-actor.s.y)/actor.scale};
          }
          if(!finite(shoulder)||!finite(wrist)) { missing.add(`${id}/${arm}: cannot recover shoulder/wrist`);continue; }
          checkedArmFrames++;
          const sh=map(shoulder,matrix), el=map(m.elbow,matrix), wr=map(wrist,matrix);
          let close=0, minGap=Infinity, sampleCount=14;
          for(let j=0;j<sampleCount;j++) {
            const u=.20+.65*j/(sampleCount-1), p={x:sh.x+(el.x-sh.x)*u,y:sh.y+(el.y-sh.y)*u};
            const gap=nearest(p,body).distance;minGap=Math.min(minGap,gap);if(gap<nearPx)close++;
          }
          if(close/sampleCount>=.5)risk(frame,id,arm,'UPPER_ARM_TORSO_OVERLAP',{close_fraction:close/sampleCount,min_gap_px:minGap,near_threshold_px:nearPx});
          const nb=nearest(el,body), len=Math.hypot(nb.dx,nb.dy)||1;
          // Body path runs from hip toward neck; its clockwise normal points right.
          const signed=((el.x-nb.q.x)*(-nb.dy)+(el.y-nb.q.y)*nb.dx)/len;
          const wrongSide=arm==='L'?signed:-signed;
          if(wrongSide>Math.max(4,bodyStroke*scale*.6))risk(frame,id,arm,'ELBOW_CROSSES_TORSO',{wrong_side_distance_px:wrongSide});
          const hp=[sh,el,wr].map(p=>map(p,headInverse));
          const headGap=Math.min(project(center,hp[0],hp[1]).distance,project(center,hp[1],hp[2]).distance)-radius;
          if(headGap<=3.5)risk(frame,id,arm,'ARM_TOUCHES_HEAD',{clearance_head_local_px:headGap});
          const reach=m.reach/m.limit;maxReachRatio=Math.max(maxReachRatio,reach);
          if(reach>.93)risk(frame,id,arm,'ARM_NEAR_FULL_EXTENSION',{reach_ratio:reach});
        }
      }
    }
    return { duration, size:[window.W||1440,window.H||1080], frames, actor_ids:[...actorIds], checked_arm_frames:checkedArmFrames, max_reach_ratio:maxReachRatio, hits, unavailable_reasons:[...missing] };
  });
  const { hits=[], ...summary }=scan;Object.assign(report,summary);
  const groups=new Map();
  for(const hit of hits) {
    const key=`${hit.actor}/${hit.arm}/${hit.code}`;
    if(!groups.has(key))groups.set(key,[]);groups.get(key).push(hit);
  }
  const minimumFrames={UPPER_ARM_TORSO_OVERLAP:6,ELBOW_CROSSES_TORSO:3,ARM_TOUCHES_HEAD:1,ARM_NEAR_FULL_EXTENSION:1};
  for(const list of groups.values()) {
    let block=[];
    const flush=()=>{
      if(block.length>=(minimumFrames[block[0]?.code]||1)) {
        const first=block[0], last=block.at(-1), middle=block[Math.floor(block.length/2)];
        report.risks.push({code:first.code,actor:first.actor,arm:first.arm,start_seconds:+(first.frame/30).toFixed(3),end_seconds:+Math.min(report.duration,(last.frame+1)/30).toFixed(3),frame_count:block.length,representative_seconds:+(middle.frame/30).toFixed(3),evidence:middle.evidence});
      }
      block=[];
    };
    for(const item of list) {if(block.length&&item.frame!==block.at(-1).frame+1)flush();block.push(item);}flush();
  }
  report.risks.sort((a,b)=>a.start_seconds-b.start_seconds||a.code.localeCompare(b.code));
  if(!report.checked_arm_frames)report.unavailable_reasons.push('No visible, supported arm frames were evaluated');
  if(report.page_errors.length)report.unavailable_reasons.push('The page emitted JavaScript errors; the scan may be incomplete');
  report.geometry_status=report.unavailable_reasons.length?'UNAVAILABLE':report.risks.length?'REVIEW':'PASS';
} catch(error) {
  report.unavailable_reasons.push(error.message);
} finally {
  if(browser)await browser.close();
  fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({geometry_status:report.geometry_status,needs_visual_review:true,risk_count:report.risks.length,report:out,unavailable_reasons:report.unavailable_reasons}));
}
