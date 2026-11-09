/* Compact section menu for phones. Without JS the section links show as a scrolling row. */
(function () {
  "use strict";
  var btn = document.querySelector(".menu-btn");
  var nav = document.getElementById("site-nav");
  if (!btn || !nav) return;
  function setOpen(open) {
    nav.classList.toggle("open", open);
    btn.setAttribute("aria-expanded", open ? "true" : "false");
  }
  btn.addEventListener("click", function () {
    setOpen(btn.getAttribute("aria-expanded") !== "true");
  });
  nav.addEventListener("click", function (e) {
    if (e.target.closest("a")) setOpen(false);
  });
  nav.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { setOpen(false); btn.focus(); }
  });
  btn.addEventListener("keydown", function (e) {
    if (e.key === "Escape") setOpen(false);
  });
  document.addEventListener("click", function (e) {
    if (nav.classList.contains("open") && !nav.contains(e.target) && !btn.contains(e.target)) setOpen(false);
  });
})();

/* "Am I likely eligible?" self-check.
   Runs entirely in the browser. Nothing is stored, logged, or sent anywhere. */
(function () {
  "use strict";

  // 2026 HHS poverty guidelines, 48 states + DC (ASPE, 2026).
  var FPL = [15960, 21640, 27320, 33000, 38680, 44360, 50040, 55720];
  var FPL_EXTRA = 5680;
  // DHCS published 138% FPL yearly limits, household sizes 1-12 (DHCS, n.d.-b).
  var ADULT_138 = [22025, 29863, 37702, 45540, 53378, 61217, 69055, 76894, 84732, 92570, 100409, 108247];

  function fpl(n) {
    return n <= 8 ? FPL[n - 1] : FPL[7] + FPL_EXTRA * (n - 8);
  }

  var lang = (document.documentElement.lang || "en").slice(0, 2);
  var money = function (v) {
    return "$" + Math.round(v).toLocaleString("en-US");
  };

  var T = {
    en: {
      need: "Please answer all three questions.",
      childGoodH: "Your child is likely eligible for free Medi-Cal.",
      childGood: function (lim) {
        return "Children under 19 can get full Medi-Cal with dental care when family income is at or below about " + lim + " a year for your household size. A child's immigration status does not matter.";
      },
      childMaybeH: "Your child may qualify for low-cost coverage.",
      childMaybe: function (lo, hi) {
        return "Your income is above " + lo + " but at or below about " + hi + ". Many children in this range can get coverage with medical, dental, and vision care for a small monthly premium. Apply to find out.";
      },
      childOverH: "Your income looks higher than the Medi-Cal limit for kids.",
      childOver: "You can still apply. Medi-Cal counts income in special ways, and Covered California may help pay for a health plan.",
      pregH: "Pregnant people can get full Medi-Cal, including dental.",
      pregLow: function (lim) {
        return "Your income is at or below " + lim + ", so you are likely eligible. ";
      },
      preg: "Pregnancy coverage does not depend on immigration status, and it lasts during pregnancy and for one year after. Pregnancy has its own income rules, so apply even if your income is higher.",
      adultGoodH: "You may be eligible for Medi-Cal based on income.",
      adultGood: function (lim) {
        return "Adults 19 to 64 can qualify with income at or below " + lim + " a year for your household size.";
      },
      adultOverH: "Your income looks higher than the Medi-Cal limit for adults.",
      adultOver: "Covered California can help you find a lower-cost health plan, and your children may still qualify for Medi-Cal at your income. Check again with \"My child\" selected.",
      adultFreeze: "Since January 1, 2026, most adults 19 and older without a qualifying immigration status cannot newly sign up for full Medi-Cal. They can still get emergency and pregnancy care.",
      seniorH: "Older adults use different Medi-Cal rules.",
      senior: "Since January 1, 2026, Medi-Cal counts assets for adults 65 and older (limit: $130,000 for one person, plus $65,000 for each extra person). Call your county office to talk through your situation.",
      foot: "This is only an estimate, not a decision. The county makes the final decision when you apply."
    },
    es: {
      need: "Por favor conteste las tres preguntas.",
      childGoodH: "Es probable que su hijo califique para Medi-Cal gratis.",
      childGood: function (lim) {
        return "Los niños menores de 19 años pueden recibir Medi-Cal completo con servicios dentales si el ingreso familiar es de aproximadamente " + lim + " al año o menos para el tamaño de su hogar. El estatus migratorio del niño no importa.";
      },
      childMaybeH: "Su hijo podría calificar para cobertura de bajo costo.",
      childMaybe: function (lo, hi) {
        return "Su ingreso es mayor de " + lo + " pero de aproximadamente " + hi + " o menos. Muchos niños en este rango pueden recibir cobertura médica, dental y de la vista por una pequeña cuota mensual. Presente una solicitud para saberlo.";
      },
      childOverH: "Su ingreso parece ser mayor que el límite de Medi-Cal para niños.",
      childOver: "Aun así puede presentar una solicitud. Medi-Cal cuenta el ingreso de maneras especiales, y Covered California puede ayudarle a pagar un plan de salud.",
      pregH: "Las personas embarazadas pueden recibir Medi-Cal completo, incluido el dental.",
      pregLow: function (lim) {
        return "Su ingreso es de " + lim + " o menos, así que es probable que califique. ";
      },
      preg: "La cobertura durante el embarazo no depende del estatus migratorio y dura todo el embarazo y un año después. El embarazo tiene sus propias reglas de ingreso, así que presente una solicitud aunque su ingreso sea más alto.",
      adultGoodH: "Podría calificar para Medi-Cal según su ingreso.",
      adultGood: function (lim) {
        return "Los adultos de 19 a 64 años pueden calificar con un ingreso de " + lim + " al año o menos para el tamaño de su hogar.";
      },
      adultOverH: "Su ingreso parece ser mayor que el límite de Medi-Cal para adultos.",
      adultOver: "Covered California puede ayudarle a encontrar un plan de salud de menor costo, y sus hijos aún podrían calificar para Medi-Cal con su ingreso. Vuelva a revisar eligiendo \"Mi hijo o hija\".",
      adultFreeze: "Desde el 1 de enero de 2026, la mayoría de los adultos de 19 años o más sin un estatus migratorio que califique no pueden inscribirse por primera vez en Medi-Cal completo. Todavía pueden recibir atención de emergencia y del embarazo.",
      seniorH: "Los adultos mayores tienen otras reglas de Medi-Cal.",
      senior: "Desde el 1 de enero de 2026, Medi-Cal cuenta los bienes de los adultos de 65 años o más (límite: $130,000 para una persona, más $65,000 por cada persona adicional). Llame a la oficina de su condado para hablar de su situación.",
      foot: "Esto es solo un cálculo aproximado, no una decisión. El condado toma la decisión final cuando usted presenta su solicitud."
    }
  };
  var t = T[lang] || T.en;

  var form = document.getElementById("checker");
  if (!form) return;
  var out = document.getElementById("result");

  function show(kind, heading, body) {
    out.className = "result show " + kind;
    out.innerHTML = "";
    var h = document.createElement("h3");
    h.textContent = heading;
    out.appendChild(h);
    body.forEach(function (txt) {
      var p = document.createElement("p");
      p.textContent = txt;
      out.appendChild(p);
    });
    var f = document.createElement("p");
    f.className = "hint";
    f.textContent = t.foot;
    out.appendChild(f);
    out.focus();
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var who = form.querySelector('input[name="who"]:checked');
    var size = parseInt(form.size.value, 10);
    var income = parseFloat(String(form.income.value).replace(/[^0-9.]/g, ""));
    if (!who || !size || isNaN(income)) {
      out.className = "result show other";
      out.textContent = t.need;
      out.focus();
      return;
    }
    var base = fpl(size);
    var adult = ADULT_138[size - 1];
    switch (who.value) {
      case "child":
        var c266 = base * 2.66, c322 = base * 3.22;
        if (income <= c266) show("good", t.childGoodH, [t.childGood(money(c266))]);
        else if (income <= c322) show("maybe", t.childMaybeH, [t.childMaybe(money(c266), money(c322))]);
        else show("other", t.childOverH, [t.childOver]);
        break;
      case "pregnant":
        show("good", t.pregH, [(income <= adult ? t.pregLow(money(adult)) : "") + t.preg]);
        break;
      case "adult":
        if (income <= adult) show("good", t.adultGoodH, [t.adultGood(money(adult)), t.adultFreeze]);
        else show("other", t.adultOverH, [t.adultOver]);
        break;
      case "senior":
        show("maybe", t.seniorH, [t.senior]);
        break;
    }
  });

  form.addEventListener("reset", function () {
    out.className = "result";
    out.textContent = "";
  });
})();
