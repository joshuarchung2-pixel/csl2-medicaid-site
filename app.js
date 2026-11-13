/* Smiles Start with Medi-Cal. All page text lives in the HTML (English and Spanish);
   this file only shows and hides parts of it and fills in numbers.
   Nothing is stored (no cookies, no localStorage) and nothing is sent anywhere. */

/* ---------- Guided flow: county, household size, who needs coverage ---------- */
(function () {
  "use strict";
  var flow = document.getElementById("flow");
  if (!flow) return;

  // 2026 HHS poverty guidelines, 48 states + DC (ASPE, 2026).
  var FPL = [15960, 21640, 27320, 33000, 38680, 44360, 50040, 55720];
  var FPL_EXTRA = 5680;
  // DHCS published 138% FPL yearly limits, household sizes 1 to 12 (DHCS, n.d.-b).
  var ADULT_138 = [22025, 29863, 37702, 45540, 53378, 61217, 69055, 76894, 84732, 92570, 100409, 108247];
  function fpl(n) { return n <= 8 ? FPL[n - 1] : FPL[7] + FPL_EXTRA * (n - 8); }
  function money(v) { return "$" + Math.round(v).toLocaleString("en-US"); }

  var steps = flow.querySelectorAll(".step");
  var bar = flow.querySelectorAll(".flow-bar span");
  var progress = document.getElementById("flow-progress");
  var progressText = progress.textContent; // "Step 1 of 3" / "Paso 1 de 3"
  var plan = document.getElementById("plan");
  var err = document.getElementById("flow-error");
  var state = { county: null, countyName: null, size: null };

  function go(n) {
    steps.forEach(function (s) { s.hidden = Number(s.dataset.step) !== n; });
    plan.hidden = n !== 4;
    flow.classList.toggle("done", n === 4);
    bar.forEach(function (b, i) { b.classList.toggle("on", i < n); });
    progress.textContent = n === 4 ? progress.dataset.done : progressText.replace("1", String(n));
    var target = n === 4 ? document.getElementById("plan-h") : flow.querySelector('.step[data-step="' + n + '"] legend');
    if (target) target.focus({ preventScroll: n !== 4 });
    if (n === 4 && plan.scrollIntoView) {
      var top = plan.getBoundingClientRect().top;
      if (top < 0 || top > window.innerHeight * 0.6) plan.scrollIntoView({ block: "start", behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
    }
  }

  function mark(group, btn) {
    group.forEach(function (b) { b.classList.toggle("chosen", b === btn); });
  }

  // Step 1: California county map (58 paths) plus a list fallback. LA, Riverside and
  // San Bernardino have their own results; any other county is "other" and keeps its name.
  var cmap = flow.querySelector(".county-map");
  var countyEls = flow.querySelectorAll(".step [data-county]");
  var svg = cmap.querySelector(".ca-map");
  var mapLabel = cmap.querySelector(".map-label");
  var tip = cmap.querySelector(".map-tip");
  var box = cmap.querySelector(".map-box");
  var hlHover = svg.querySelector(".hl-hover");
  var hlSel = svg.querySelector(".hl-sel");
  var lastPointer = "mouse";
  var hot = null; // county path under the pointer
  var foc = null; // county path with keyboard focus
  var picked = null; // chosen county path

  function nameOf(el) { return cmap.dataset.label.replace("{name}", el.dataset.name); }
  function pathFor(name) { return svg.querySelector('.cty[data-name="' + name + '"]'); }
  function paint() {
    var kf = foc && foc.matches(":focus-visible") ? foc : null;
    var show = kf || hot || picked;
    mapLabel.textContent = show ? nameOf(show) : mapLabel.dataset.idle;
    mapLabel.classList.toggle("on", !!show);
    var ring = kf || hot;
    hlHover.setAttribute("d", ring && (ring !== picked || kf) ? ring.getAttribute("d") : "");
    hlHover.classList.toggle("kbd", !!kf);
    hlSel.setAttribute("d", picked ? picked.getAttribute("d") : "");
  }
  function pickCounty(el) {
    var p = pathFor(el.dataset.name);
    state.county = el.dataset.county;
    state.countyName = el.dataset.name;
    picked = p;
    countyEls.forEach(function (c) { c.classList.toggle("chosen", c.dataset.name === el.dataset.name); });
    paint();
    // A tap shows the name first; mouse, keyboard and the list move on right away, like the old tiles.
    if (lastPointer === "touch" && el.classList.contains("cty")) setTimeout(function () { go(2); }, 450);
    else go(2);
  }
  svg.addEventListener("pointerdown", function (e) { lastPointer = e.pointerType || "mouse"; });
  cmap.querySelector(".county-list").addEventListener("pointerdown", function () { lastPointer = "mouse"; });
  svg.addEventListener("pointerover", function (e) {
    var p = e.target.closest(".cty");
    if (!p || e.pointerType === "touch") return;
    hot = p; tip.textContent = nameOf(p); tip.hidden = false; paint();
  });
  svg.addEventListener("pointermove", function (e) {
    if (tip.hidden || e.pointerType === "touch") return;
    var r = box.getBoundingClientRect();
    var x = Math.min(e.clientX - r.left + 14, r.width - tip.offsetWidth);
    var y = e.clientY - r.top - tip.offsetHeight - 10;
    tip.style.transform = "translate(" + Math.max(0, x) + "px," + Math.max(0, y) + "px)";
  });
  svg.addEventListener("pointerout", function (e) {
    var p = e.target.closest(".cty");
    if (!p || (e.relatedTarget && e.relatedTarget.closest && e.relatedTarget.closest(".cty") === p)) return;
    if (hot === p) hot = null;
    tip.hidden = true; paint();
  });
  svg.addEventListener("focusin", function (e) { var p = e.target.closest(".cty"); if (p) { foc = p; paint(); } });
  svg.addEventListener("focusout", function () { foc = null; tip.hidden = true; paint(); });
  svg.addEventListener("click", function (e) { var p = e.target.closest(".cty"); if (p) pickCounty(p); });
  svg.addEventListener("keydown", function (e) {
    var p = e.target.closest(".cty");
    if (!p || (e.key !== "Enter" && e.key !== " " && e.key !== "Spacebar")) return;
    e.preventDefault(); lastPointer = "keyboard"; pickCounty(p);
  });
  cmap.querySelectorAll(".county-opt").forEach(function (b) {
    b.addEventListener("click", function () { pickCounty(b); });
  });
  function resetCounty() { picked = null; hot = null; foc = null; tip.hidden = true; paint(); }
  var sizeBtns = flow.querySelectorAll(".step [data-size]");
  sizeBtns.forEach(function (b) {
    b.addEventListener("click", function () { state.size = Number(b.dataset.size); mark(sizeBtns, b); go(3); });
  });
  var whoBtns = flow.querySelectorAll(".step [data-who]");
  whoBtns.forEach(function (b) {
    b.addEventListener("click", function () {
      b.setAttribute("aria-pressed", b.getAttribute("aria-pressed") === "true" ? "false" : "true");
      err.textContent = "";
    });
  });
  flow.querySelectorAll("[data-back]").forEach(function (b) {
    b.addEventListener("click", function () { go(Number(b.closest(".step").dataset.step) - 1); });
  });

  flow.querySelector("[data-finish]").addEventListener("click", function () {
    var who = {};
    whoBtns.forEach(function (b) { if (b.getAttribute("aria-pressed") === "true") who[b.dataset.who] = true; });
    if (!Object.keys(who).length) { err.textContent = err.dataset.msg; return; }
    who.kids = who.baby || who.kid || who.teen;

    var n = state.size;
    plan.querySelectorAll("[data-fill]").forEach(function (el) {
      var k = el.dataset.fill;
      el.textContent = k === "size" ? String(n)
        : k === "kid266" ? money(fpl(n) * 2.66)
        : k === "kid322" ? money(fpl(n) * 3.22)
        : money(ADULT_138[n - 1]);
    });
    plan.querySelectorAll("[data-show]").forEach(function (el) { el.hidden = !who[el.dataset.show]; });
    plan.querySelectorAll("[data-county], [data-county-name]").forEach(function (el) {
      el.hidden = (el.dataset.county || el.dataset.countyName) !== state.county;
    });
    var otherName = plan.querySelector('[data-county-name="other"]');
    if (otherName) {
      if (!otherName.dataset.base) otherName.dataset.base = otherName.textContent;
      otherName.textContent = state.county === "other" && state.countyName
        ? otherName.dataset.tpl.replace("{name}", state.countyName) : otherName.dataset.base;
    }
    plan.querySelectorAll(".plan-block").forEach(function (d, i) { d.open = i === 0; });
    go(4);
  });

  plan.querySelector("[data-restart]").addEventListener("click", function () {
    state = { county: null, countyName: null, size: null };
    flow.querySelectorAll(".chosen").forEach(function (b) { b.classList.remove("chosen"); });
    resetCounty();
    whoBtns.forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
    go(1);
  });
})();

/* ---------- Tap a tooth: age slider, stage of teeth, Medi-Cal age group ---------- */
(function () {
  "use strict";
  var root = document.getElementById("teeth");
  if (!root) return;
  var range = document.getElementById("age");
  var num = document.getElementById("age-num");
  var unit = document.getElementById("age-unit");
  var labels = range.dataset.labels.split("|");
  var units = unit.dataset.units.split("|");
  var segs = root.querySelectorAll("[data-stage]");
  var views = root.querySelectorAll("[data-mouth-view]");
  var panels = root.querySelectorAll(".panel");
  var aged = root.querySelectorAll("[data-ages]");
  var MAX = Number(range.max);

  // Slider steps: 0 = under 6 months, 1 = 6 to 11 months, then 1 year per step, last step = 90+.
  function years(i) { return i === 0 ? 0.25 : i === 1 ? 0.75 : i - 1; }
  function label(i) { return i === 0 ? labels[0] : i === 1 ? labels[1] : i === MAX ? labels[3] : labels[2].replace("{n}", String(i - 1)); }
  // Typical stage for an age. "No natural teeth" is never picked from age alone.
  function stageFor(y) { return y < 0.5 ? "none" : y < 6 ? "primary" : y < 12 ? "mixed" : "adult"; }
  // Medi-Cal Dental age groups (Smile, California, n.d.-a): babies 0-3, kids 4-12, teens 13-20, adults 21-54, seniors 55+.
  function groupFor(y) { return y < 4 ? "baby" : y < 13 ? "kid" : y < 21 ? "teen" : y < 55 ? "adult" : "senior"; }
  // If someone picks a stage that doesn't fit the age, move the slider to a typical age for it.
  var FIT = { none: [0, 2, 0], primary: [1, 8, 4], mixed: [6, 15, 9], adult: [12, MAX, 31], edentulous: [14, MAX, 61] };

  var stage = null;

  function showPanel(name) { panels.forEach(function (p) { p.hidden = p.dataset.panel !== name; }); }
  function teethOf(view) { return Array.prototype.slice.call(view.querySelectorAll(".tooth")); }
  function clear(view) {
    teethOf(view).forEach(function (t, i) {
      t.setAttribute("aria-checked", "false");
      t.setAttribute("tabindex", i === 0 ? "0" : "-1");
      t.classList.remove("same");
    });
  }
  function select(tooth, focus) {
    var all = teethOf(tooth.closest("[data-mouth-view]"));
    all.forEach(function (t) {
      var on = t === tooth;
      t.setAttribute("aria-checked", on ? "true" : "false");
      t.setAttribute("tabindex", on ? "0" : "-1");
      t.classList.toggle("same", !on && t.dataset.group === tooth.dataset.group);
    });
    showPanel(tooth.dataset.group);
    if (focus) tooth.focus();
  }

  // typing: leave the box alone while someone is typing in it
  function applyAge(typing) {
    var i = Number(range.value);
    var text = label(i);
    if (!typing) num.value = String(i <= 1 ? 0 : i === MAX ? 90 : i - 1);
    unit.textContent = i === 0 ? units[0] : i === 1 ? units[1] : i === MAX ? units[3] : units[2];
    range.setAttribute("aria-valuetext", text);
    var g = groupFor(years(i));
    aged.forEach(function (el) { el.classList.toggle("age-on", el.dataset.ages.split(" ").indexOf(g) !== -1); });
  }

  function setStage(name) {
    if (name === stage) return;
    stage = name;
    segs.forEach(function (s) { s.setAttribute("aria-pressed", s.dataset.stage === name ? "true" : "false"); });
    views.forEach(function (v) { v.hidden = v.dataset.mouthView !== name; clear(v); });
    showPanel(name + "-intro");
  }

  function onAge(typing) {
    var i = Number(range.value);
    applyAge(typing === true);
    if (!(stage === "edentulous" && i >= FIT.edentulous[0])) setStage(stageFor(years(i)));
  }

  range.addEventListener("input", onAge);
  // Typed age: digits only. 0 = under 1 year, 90 or more = 90+.
  num.addEventListener("beforeinput", function (e) { if (e.data && /\D/.test(e.data)) e.preventDefault(); });
  num.addEventListener("input", function () {
    var v = num.value.replace(/\D/g, "").slice(0, 3);
    if (v !== num.value) num.value = v;
    if (v === "") return;
    var n = Number(v), cur = Number(range.value);
    range.value = String(n === 0 ? (cur <= 1 ? cur : 0) : n >= 90 ? MAX : n + 1);
    onAge(true);
  });
  num.addEventListener("change", function () { applyAge(); });
  num.addEventListener("blur", function () { applyAge(); });
  num.addEventListener("keydown", function (e) {
    if (e.key === "Enter") { e.preventDefault(); applyAge(); num.select(); }
    else if (e.key === "ArrowUp" || e.key === "ArrowDown") {
      e.preventDefault();
      range.value = String(Math.min(MAX, Math.max(0, Number(range.value) + (e.key === "ArrowUp" ? 1 : -1))));
      onAge();
    }
  });
  root.querySelectorAll("[data-age-step]").forEach(function (b) {
    b.addEventListener("click", function () {
      range.value = String(Math.min(MAX, Math.max(0, Number(range.value) + Number(b.dataset.ageStep))));
      onAge();
    });
  });
  segs.forEach(function (s) {
    s.addEventListener("click", function () {
      var f = FIT[s.dataset.stage], i = Number(range.value);
      if (i < f[0] || i > f[1]) { range.value = String(f[2]); applyAge(); }
      setStage(s.dataset.stage);
    });
  });

  views.forEach(function (view) {
    var all = teethOf(view);
    all.forEach(function (t, i) {
      t.addEventListener("click", function () { select(t, false); });
      t.addEventListener("keydown", function (e) {
        var k = e.key, j = i;
        if (k === "ArrowRight" || k === "ArrowDown") j = (i + 1) % all.length;
        else if (k === "ArrowLeft" || k === "ArrowUp") j = (i - 1 + all.length) % all.length;
        else if (k === "Home") j = 0;
        else if (k === "End") j = all.length - 1;
        else if (k === " " || k === "Enter") { e.preventDefault(); select(t, false); return; }
        else return;
        e.preventDefault();
        select(all[j], true);
      });
    });
  });

  root.querySelectorAll("[data-panel-btn]").forEach(function (b) {
    b.addEventListener("click", function () {
      views.forEach(function (v) { if (!v.hidden) clear(v); });
      showPanel(b.dataset.panelBtn);
    });
  });

  applyAge();
  setStage(stageFor(years(Number(range.value))));
})();

/* ---------- Citations: the reference's back link returns to the citation that was clicked ---------- */
document.addEventListener("click", function (e) {
  var c = e.target.closest && e.target.closest("a.cite[id]");
  if (!c) return;
  var back = document.querySelector(c.getAttribute("href") + " .back");
  if (back) back.setAttribute("href", "#" + c.id);
});

/* ---------- Flip cards ---------- */
(function () {
  "use strict";
  document.querySelectorAll(".flip").forEach(function (card) {
    var front = card.querySelector(".front");
    var back = card.querySelector(".back");
    function set(flipped) {
      card.classList.toggle("flipped", flipped);
      front.inert = flipped;
      back.inert = !flipped;
      (flipped ? back.querySelector("p[tabindex]") : front.querySelector(".flip-btn")).focus({ preventScroll: true });
    }
    back.inert = true;
    card.addEventListener("click", function (e) {
      if (e.target.closest("a")) return;
      set(!card.classList.contains("flipped"));
    });
  });
})();

/* ---------- Motion (v4.3): background, scroll reveals, smooth expand/collapse ----------
   Decoration only. Nothing is hidden unless this script runs, and with
   prefers-reduced-motion: reduce nothing moves (the background stays still, reveals and
   expand/collapse are instant). */
(function () {
  "use strict";
  var reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Background: drifting palette blobs + faint dot grid, both trailing the scroll (styles.css .bg-fx).
  var bg = document.createElement("div");
  bg.className = "bg-fx";
  bg.setAttribute("aria-hidden", "true");
  bg.innerHTML = '<div class="bg-dotmask"><div class="bg-dots"></div></div><div class="bg-par"><div class="bg-blobs"></div></div>';
  document.body.appendChild(bg);
  if (!reduce) {
    var par = bg.querySelector(".bg-par"), dots = bg.querySelector(".bg-dots"), ticking = false;
    var drawBg = function () {
      ticking = false;
      var y = window.pageYOffset || 0;
      // Blobs move at a quarter of the scroll, dots at 40%. The patterns repeat every 1400px / 24px,
      // so wrapping the offset keeps them seamless and the layers small.
      par.style.transform = "translate3d(0," + (-(y * 0.25 % 1400)).toFixed(1) + "px,0)";
      dots.style.transform = "translate3d(0," + (-(y * 0.4 % 24)).toFixed(1) + "px,0)";
    };
    window.addEventListener("scroll", function () {
      if (!ticking) { ticking = true; requestAnimationFrame(drawBg); }
    }, { passive: true });
    drawBg();
  }

  if (reduce) return;

  // Scroll reveals: only blocks that start below the fold get hidden, so nothing on screen flashes.
  if ("IntersectionObserver" in window) {
    var SEL = [
      ".band .section-head", ".refs-head", ".note-card", ".sdoh-lead", ".sdoh-pairs > li", ".sdoh > .small",
      ".mouth-controls", ".teeth-grid", ".flips > li", ".steps > li", ".callout",
      ".help-grid > .card", "#help .note", ".share", ".ref-group"
    ].join(",");
    var fold = window.innerHeight * 0.95;
    var io = new IntersectionObserver(function (entries) {
      // Everything that enters together staggers top-to-bottom, left-to-right.
      var shown = entries.filter(function (e) { return e.isIntersecting; }).map(function (e) { return e.target; });
      shown.sort(function (a, b) {
        var ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
        return (ra.top - rb.top) || (ra.left - rb.left);
      });
      shown.forEach(function (el, i) {
        io.unobserve(el);
        var d = Math.min(i, 5) * 90;
        el.style.setProperty("--rv-d", d + "ms");
        el.classList.add("in");
        setTimeout(function () { el.classList.remove("rv", "in"); el.style.removeProperty("--rv-d"); }, d + 750);
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    Array.prototype.forEach.call(document.querySelectorAll(SEL), function (el) {
      var r = el.getBoundingClientRect();
      if (r.height > 0 && r.top > fold) { el.classList.add("rv"); io.observe(el); }
    });
  }

  // Expand/collapse: browsers that can transition to height:auto do it in CSS (styles.css,
  // interpolate-size). Others (Safari, Firefox) get the same motion here. <details> keeps its
  // native state and semantics; exclusive groups (name="...") are kept exclusive by hand.
  var cssDetails = window.CSS && CSS.supports && CSS.supports("interpolate-size", "allow-keywords");
  if (cssDetails || !Element.prototype.animate) return;
  var EASE = "cubic-bezier(.2, .7, .2, 1)";
  document.querySelectorAll("details").forEach(function (d) {
    var sum = d.firstElementChild;
    if (!sum || sum.tagName !== "SUMMARY") return;
    var group = d.getAttribute("name");
    if (group) { d.setAttribute("data-group", group); d.removeAttribute("name"); }
    var anim = null, closing = false;
    function run(opening) {
      var start = d.getBoundingClientRect().height;
      if (anim) { anim.cancel(); anim = null; }
      d.open = false;
      var closedH = d.getBoundingClientRect().height;
      d.open = true;
      var end = opening ? d.getBoundingClientRect().height : closedH;
      closing = !opening;
      d.style.overflow = "hidden";
      anim = d.animate([{ height: start + "px" }, { height: end + "px" }], { duration: 320, easing: EASE });
      if (opening) {
        Array.prototype.forEach.call(d.children, function (c) {
          if (c !== sum) c.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 260, easing: "ease" });
        });
      }
      anim.onfinish = function () {
        anim = null; closing = false; d.style.overflow = "";
        if (!opening) d.open = false;
      };
    }
    d._motion = { run: run, isOpen: function () { return d.open && !closing; } };
    sum.addEventListener("click", function (e) {
      e.preventDefault();
      var opening = !d.open || closing;
      if (opening && group) {
        document.querySelectorAll('details[data-group="' + group + '"]').forEach(function (o) {
          if (o !== d && o._motion && o._motion.isOpen()) o._motion.run(false);
        });
      }
      run(opening);
    });
  });
})();
