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
  var state = { county: null, size: null };

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

  var countyBtns = flow.querySelectorAll(".step [data-county]");
  countyBtns.forEach(function (b) {
    b.addEventListener("click", function () { state.county = b.dataset.county; mark(countyBtns, b); go(2); });
  });
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
    go(4);
  });

  plan.querySelector("[data-restart]").addEventListener("click", function () {
    state = { county: null, size: null };
    flow.querySelectorAll(".chosen").forEach(function (b) { b.classList.remove("chosen"); });
    whoBtns.forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
    go(1);
  });
})();

/* ---------- Tap a tooth ---------- */
(function () {
  "use strict";
  var root = document.getElementById("teeth");
  if (!root) return;
  var panels = root.querySelectorAll(".panel");
  var segs = root.querySelectorAll("[data-mouth]");
  var views = root.querySelectorAll("[data-mouth-view]");

  function showPanel(name) {
    panels.forEach(function (p) { p.hidden = p.dataset.panel !== name; });
  }
  function teethOf(view) { return Array.prototype.slice.call(view.querySelectorAll(".tooth")); }

  function select(tooth, focus) {
    var view = tooth.closest("[data-mouth-view]");
    var all = teethOf(view);
    all.forEach(function (t) {
      var on = t === tooth;
      t.setAttribute("aria-checked", on ? "true" : "false");
      t.setAttribute("tabindex", on ? "0" : "-1");
      t.classList.toggle("same", !on && t.dataset.group === tooth.dataset.group);
    });
    showPanel(tooth.dataset.group);
    if (focus) tooth.focus();
  }

  function clear(view) {
    var all = teethOf(view);
    all.forEach(function (t, i) {
      t.setAttribute("aria-checked", "false");
      t.setAttribute("tabindex", i === 0 ? "0" : "-1");
      t.classList.remove("same");
    });
  }

  function setMouth(name) {
    segs.forEach(function (s) { s.setAttribute("aria-pressed", s.dataset.mouth === name ? "true" : "false"); });
    views.forEach(function (v) { v.hidden = v.dataset.mouthView !== name; clear(v); });
    showPanel(name + "-intro");
  }

  segs.forEach(function (s) { s.addEventListener("click", function () { setMouth(s.dataset.mouth); }); });

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

  setMouth("kid");
})();

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
