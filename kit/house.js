/* House kit for knowledge videos (cut-paper / dossier / sketchbook).
 * Needs gsap. Every helper adds tweens to a paused timeline so HyperFrames can seek it.
 *
 *   House.defs(svgEl, "paper"|"dossier"|"sketch")   inject SVG filters & patterns
 *   House.twos(ease, dur)        ease that steps at 12 fps (animate "on twos")
 *   House.cam(tl, worldSel)      camera: put world point (cx,cy) at screen centre with scale s
 *   House.slap(tl, sel, t, o)    paper piece lands: drop + overshoot + settle, on twos
 *   House.pop(tl, sel, t, o)     character rises from behind something, squash & stretch
 *   House.draw(tl, sel, t, dur)  stroke draws on (paths/ellipses), on twos
 *   House.wipe(tl, sel, t, dur)  left-to-right reveal (highlighter, handwriting)
 *   House.flip(tl, sel, t, o)    a page / flap opens around a hinge
 *   House.boil(tl, ids, D)       swap noise seeds every 2 frames (line boil) for D seconds
 *   House.loop(tl, sel, D, o)    small background life (steam, sway) for D seconds
 *   House.blink(tl, eyesSel, t)  one blink
 */
(function (g) {
  var NS = "http://www.w3.org/2000/svg";
  var H = {};
  var FILTERS = {
    paper:
      '<filter id="torn" filterUnits="userSpaceOnUse" x="-50" y="-50" width="1540" height="1180"><feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="3" seed="3"/><feDisplacementMap in="SourceGraphic" scale="9"/></filter>' +
      '<filter id="torn2" filterUnits="userSpaceOnUse" x="-50" y="-50" width="1540" height="1180"><feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="3" seed="8"/><feDisplacementMap in="SourceGraphic" scale="10"/></filter>' +
      '<filter id="sh" filterUnits="userSpaceOnUse" x="-50" y="-50" width="1540" height="1180"><feDropShadow dx="5" dy="7" stdDeviation="1.6" flood-color="#0c1f1d" flood-opacity=".45"/></filter>' +
      '<filter id="crayon" filterUnits="userSpaceOnUse" x="-50" y="-50" width="1540" height="1180"><feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="1" seed="5"/><feDisplacementMap in="SourceGraphic" scale="3"/></filter>' +
      '<filter id="grain" filterUnits="userSpaceOnUse" x="0" y="0" width="1440" height="1080"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="2"/><feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .5 0"/><feComposite in2="SourceGraphic" operator="in"/></filter>' +
      '<pattern id="stripe" width="22" height="22" patternUnits="userSpaceOnUse"><rect width="22" height="22" fill="#E8B83E"/><rect width="22" height="9" fill="#F4E3B0"/></pattern>' +
      '<pattern id="dots" width="34" height="34" patternUnits="userSpaceOnUse"><rect width="34" height="34" fill="#C99A6B"/><circle cx="8" cy="8" r="4" fill="#B5845A"/><circle cx="25" cy="25" r="4" fill="#B5845A"/></pattern>' +
      '<pattern id="wallp" width="120" height="120" patternUnits="userSpaceOnUse"><rect width="120" height="120" fill="#2F6A64"/><path d="M0 60h120M60 0v120" stroke="#2A615B" stroke-width="3"/></pattern>' +
      '<pattern id="lines" width="10" height="34" patternUnits="userSpaceOnUse"><rect width="10" height="34" fill="#F8F4EA"/><rect y="32" width="10" height="1.5" fill="#DCD3BF"/></pattern>',
    dossier:
      '<filter id="rough" filterUnits="userSpaceOnUse" x="0" y="0" width="1440" height="1080"><feTurbulence type="fractalNoise" baseFrequency="0.06" numOctaves="2" seed="4"/><feDisplacementMap in="SourceGraphic" scale="5"/></filter>' +
      '<filter id="g" filterUnits="userSpaceOnUse" x="0" y="0" width="1440" height="1080"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="3" seed="9"/><feColorMatrix type="saturate" values="0"/></filter>',
    sketch:
      '<pattern id="grid" width="36" height="36" patternUnits="userSpaceOnUse"><circle cx="18" cy="18" r="1.6" fill="#C9C3B4"/></pattern>' +
      '<filter id="pencil" filterUnits="userSpaceOnUse" x="0" y="0" width="1440" height="1080"><feTurbulence type="fractalNoise" baseFrequency=".035" numOctaves="2" seed="7" result="w"/><feDisplacementMap in="SourceGraphic" in2="w" scale="4" result="d"/><feTurbulence type="fractalNoise" baseFrequency="1.1" numOctaves="2" seed="1" result="g"/><feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.4 1.15" result="gm"/><feComposite in="d" in2="gm" operator="in"/></filter>' +
      '<filter id="pencil2" filterUnits="userSpaceOnUse" x="0" y="0" width="1440" height="1080"><feTurbulence type="fractalNoise" baseFrequency=".02" numOctaves="2" seed="31" result="w"/><feDisplacementMap in="SourceGraphic" in2="w" scale="7"/></filter>' +
      '<filter id="pen" filterUnits="userSpaceOnUse" x="0" y="0" width="1440" height="1080"><feTurbulence type="fractalNoise" baseFrequency=".05" numOctaves="2" seed="3"/><feDisplacementMap in="SourceGraphic" scale="3"/></filter>' +
      '<pattern id="hatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(40)"><path d="M0 0v10" stroke="#55534E" stroke-width="2.2"/></pattern>' +
      '<filter id="paper" filterUnits="userSpaceOnUse" x="0" y="0" width="1440" height="1080"><feTurbulence type="fractalNoise" baseFrequency=".5" numOctaves="3" seed="21"/><feColorMatrix values="0 0 0 0 .4  0 0 0 0 .37  0 0 0 0 .3  0 0 0 .16 0"/></filter>'
  };
  H.defs = function (svg, style) {
    var d = svg.querySelector("defs") || svg.insertBefore(document.createElementNS(NS, "defs"), svg.firstChild);
    d.insertAdjacentHTML("beforeend", FILTERS[style] || "");
  };

  // 12 fps steps for element motion; camera stays smooth (use normal eases for H.cam).
  H.twos = function (ease, dur) {
    var e = gsap.parseEase(ease || "power3.out"), st = (1 / 12) / Math.max(dur, 1 / 12);
    return function (p) { return p >= 1 ? 1 : e(Math.floor(p / st) * st); };
  };

  H.cam = function (tl, sel, init) {
    var el = document.querySelector(sel), st = { cx: 720, cy: 540, s: 1 };
    Object.assign(st, init || {});
    function apply() { el.style.transform = "translate(" + (720 - st.cx * st.s) + "px," + (540 - st.cy * st.s) + "px) scale(" + st.s + ")"; }
    apply();
    return {
      to: function (target, dur, ease, at) { tl.to(st, Object.assign({ duration: dur, ease: ease || "sine.inOut", onUpdate: apply }, target), at); },
      set: function (target, at) { tl.set(st, Object.assign({ onUpdate: apply }, target), at); apply(); }
    };
  };

  function origin(o, sel) { return o && o.origin ? { svgOrigin: o.origin } : { transformOrigin: "50% 50%" }; }

  H.slap = function (tl, sel, t, o) {
    o = o || {};
    var rot = o.rot != null ? o.rot : 10, base = Object.assign({}, origin(o, sel));
    tl.fromTo(sel, Object.assign({ opacity: 0, y: o.y != null ? o.y : -60, rotation: rot, scale: 1.25 }, base),
      Object.assign({ opacity: 1, y: 0, rotation: -rot * 0.15, scale: 0.97, duration: 0.33, ease: H.twos("power3.in", 0.33) }, base), t);
    tl.to(sel, Object.assign({ rotation: 0, scale: 1, duration: 0.25, ease: H.twos("back.out(3)", 0.25) }, base), t + 0.33);
  };

  H.pop = function (tl, sel, t, o) {
    o = o || {};
    var b = o.origin ? { svgOrigin: o.origin } : { transformOrigin: "50% 100%" };
    tl.fromTo(sel, Object.assign({ y: o.from || 320, scaleY: 1.12, scaleX: 0.92 }, b), Object.assign({ y: -14, scaleY: 1.06, scaleX: 0.96, duration: 0.42, ease: H.twos("power3.out", 0.42) }, b), t);
    tl.to(sel, Object.assign({ y: 0, scaleY: 0.94, scaleX: 1.05, duration: 0.17, ease: H.twos("power2.in", 0.17) }, b), t + 0.42);
    tl.to(sel, Object.assign({ scaleY: 1, scaleX: 1, duration: 0.25, ease: H.twos("back.out(2.5)", 0.25) }, b), t + 0.59);
  };

  H.draw = function (tl, sel, t, dur, ease) {
    document.querySelectorAll(sel).forEach(function (p, i) {
      var L = p.getTotalLength ? p.getTotalLength() : 1000;
      p.style.strokeDasharray = L + " " + L; p.style.strokeDashoffset = L;
      tl.to(p, { strokeDashoffset: 0, duration: dur, ease: H.twos(ease || "power2.inOut", dur) }, t + i * dur * 0.9);
    });
  };

  H.wipe = function (tl, sel, t, dur, o) {
    o = o || {};
    tl.fromTo(sel, { clipPath: "inset(-20% 100% -20% 0%)" }, { clipPath: "inset(-20% 0% -20% 0%)", duration: dur, ease: H.twos(o.ease || "power2.out", dur), stagger: o.stagger || 0 }, t);
  };

  H.flip = function (tl, sel, t, o) {
    o = o || {};
    tl.fromTo(sel, { scaleX: 0, svgOrigin: o.origin }, { scaleX: 1.04, svgOrigin: o.origin, duration: 0.3, ease: H.twos("power3.out", 0.3) }, t);
    tl.to(sel, { scaleX: 1, svgOrigin: o.origin, duration: 0.17, ease: H.twos("power2.out", 0.17) }, t + 0.3);
  };

  // Line boil: every 2 frames pick one of 3 seeds. Uses onUpdate so it works when the renderer seeks.
  H.boil = function (tl, ids, D) {
    var tur = ids.map(function (id) { return document.querySelector("#" + id + " feTurbulence"); }).filter(Boolean);
    var base = tur.map(function (x) { return +x.getAttribute("seed") || 1; });
    var proxy = { t: 0 };
    tl.to(proxy, { t: D, duration: D, ease: "none", onUpdate: function () {
      var k = Math.floor(proxy.t * 12) % 3;
      tur.forEach(function (x, i) { x.setAttribute("seed", base[i] + k * 7); });
    } }, 0);
  };

  H.loop = function (tl, sel, D, o) {
    o = o || {};
    var per = o.period || 1.6, n = Math.max(1, Math.ceil(D / per))  /* ceil: must run to the last frame */;
    tl.fromTo(sel, Object.assign({}, o.from || { y: 0 }), Object.assign({ duration: per / 2, ease: "sine.inOut", yoyo: true, repeat: n * 2 - 1 }, o.to || { y: -10 }), o.at || 0);
  };

  H.blink = function (tl, eyes, t) {
    tl.to(eyes, { scaleY: 0.1, transformOrigin: "50% 50%", duration: 0.05, ease: "none" }, t);
    tl.to(eyes, { scaleY: 1, transformOrigin: "50% 50%", duration: 0.07, ease: "none" }, t + 0.1);
  };

  g.House = H;
})(window);
