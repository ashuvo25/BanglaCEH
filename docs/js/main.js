/* When a Name Is Not a Name: site interactions (no dependencies) */
(function () {
  "use strict";

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const fmt = (n, d = 2) => Number(n).toFixed(d);

  /* ---------------- theme ---------------- */
  const root = document.documentElement;
  try {
    const saved = localStorage.getItem("ceh-theme");
    if (saved) root.dataset.theme = saved;
  } catch (e) { /* storage unavailable */ }

  $("#themeToggle").addEventListener("click", () => {
    const dark = root.dataset.theme
      ? root.dataset.theme === "dark"
      : matchMedia("(prefers-color-scheme: dark)").matches;
    root.dataset.theme = dark ? "light" : "dark";
    try { localStorage.setItem("ceh-theme", root.dataset.theme); } catch (e) { /* ignore */ }
  });

  /* ---------------- hero specimen ---------------- */
  const SPECIMENS = [
    { w: "মায়া", r: "Maya", name: "a common girl's name", sense: "deep, affectionate compassion" },
    { w: "আশা", r: "Asha", name: "a girl's name", sense: "hope" },
    { w: "গগন", r: "Gagan", name: "a boy's name", sense: "the sky, the celestial firmament" },
    { w: "আরিফ", r: "Arif", name: "a boy's name", sense: "one who knows the divine intuitively (Sufi)" },
  ];
  let specIdx = 0;
  const specimen = $("#specimen");
  function turnSpecimen() {
    specIdx = (specIdx + 1) % SPECIMENS.length;
    const s = SPECIMENS[specIdx];
    specimen.classList.add("is-turning");
    setTimeout(() => {
      $("#specimenWord").textContent = s.w;
      $("#specimenRoman").textContent = s.r;
      $("#specimenName").textContent = s.name;
      $("#specimenSense").textContent = s.sense;
      $("#specimenIdx").textContent = specIdx + 1;
      specimen.classList.remove("is-turning");
    }, 220);
  }
  specimen.setAttribute("tabindex", "0");
  specimen.setAttribute("role", "button");
  specimen.addEventListener("click", turnSpecimen);
  specimen.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") { e.preventDefault(); turnSpecimen(); }
  });

  /* ---------------- word cards ---------------- */
  $$(".wcard").forEach((card) => {
    card.addEventListener("click", () => {
      card.setAttribute("aria-pressed", card.getAttribute("aria-pressed") === "true" ? "false" : "true");
    });
  });

  /* ---------------- margin index: active unit + progress ---------------- */
  const links = $$(".rail__list a");
  const units = links.map((a) => $(a.getAttribute("href")));
  const bar = $("#progressBar");
  function onScroll() {
    const y = window.scrollY + window.innerHeight * 0.3;
    let active = 0;
    units.forEach((u, i) => { if (u && u.offsetTop <= y) active = i; });
    links.forEach((a, i) => a.classList.toggle("is-active", i === active));
    const max = document.documentElement.scrollHeight - window.innerHeight;
    if (bar) bar.style.width = (max > 0 ? (window.scrollY / max) * 100 : 0) + "%";
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // keep the active tab visible in the horizontal mobile index
  let lastActive = null;
  window.addEventListener("scroll", () => {
    const a = $(".rail__list a.is-active");
    if (a && a !== lastActive && window.innerWidth < 960) {
      lastActive = a;
      a.parentElement.parentElement.scrollTo({ left: a.offsetLeft - 16, behavior: "smooth" });
    }
  }, { passive: true });

  /* ---------------- run-once when visible ---------------- */
  function whenVisible(el, fn) {
    if (!el) return;
    if (!("IntersectionObserver" in window)) { fn(); return; }
    const io = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) { io.disconnect(); fn(); }
    }, { threshold: 0.25 });
    io.observe(el);
  }

  /* ---------------- stat counters ---------------- */
  $$("[data-count]").forEach((el) => {
    const target = parseFloat(el.dataset.count);
    const dec = parseInt(el.dataset.decimals || "0", 10);
    whenVisible(el, () => {
      const t0 = performance.now(), dur = 1100;
      const step = (t) => {
        const p = Math.min(1, (t - t0) / dur);
        const v = target * (1 - Math.pow(1 - p, 3));
        el.textContent = dec ? v.toFixed(dec) : Math.round(v).toLocaleString("en-US");
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    });
  });

  /* ---------------- category bars ---------------- */
  const CATS = [
    ["Name ↔ Concept", 795, true],
    ["Concept ↔ Emotion", 193, false],
    ["Name ↔ Spiritual", 179, true],
    ["Name ↔ Emotion", 178, true],
    ["Emotion ↔ State", 171, false],
  ];
  const catBars = $("#catBars");
  const catMax = Math.max(...CATS.map((c) => c[1]));
  catBars.innerHTML = CATS.map(([l, n, isName]) => `
    <div class="hbar">
      <span class="hbar__label">${l}</span>
      <span class="hbar__track"><span class="hbar__fill${isName ? " hbar__fill--name" : ""}" data-w="${(n / catMax) * 100}"></span></span>
      <span class="hbar__val">${n}</span>
    </div>`).join("");
  catBars.setAttribute("aria-label", CATS.map(([l, n]) => `${l}: ${n}`).join("; "));
  whenVisible(catBars, () => $$(".hbar__fill", catBars).forEach((f) => { f.style.width = f.dataset.w + "%"; }));

  /* ---------------- results chart ---------------- */
  const REGIMES = ["Zero-shot", "Few-shot", "C-CoT", "QLoRA-KD"];
  const MODELS = [
    { id: "qwen", name: "Qwen2.5-1.5B", em: [0.65, 8.39, 30.97, 85.16],
      note: "From near-zero to 85.16% EM, and dominant-meaning bias falls from 63.46% to 0.00%." },
    { id: "llama", name: "Llama-3.2-3B", em: [10.97, 22.58, 15.16, 82.42],
      note: "C-CoT alone does not help Llama, but distillation lifts it to 82.42% EM with 2.80% bias." },
    { id: "titu", name: "TituLLM-1B", em: [0.11, 0.31, 1.14, 87.91],
      note: "The Bangla-specific model fails every prompting regime, then becomes the strongest system after distillation." },
    { id: "gpt", name: "GPT-4o-mini", em: [43.87, 49.68, null, null],
      note: "Closed model, prompting only. Its best score (49.68%) is the bar every fine-tuned small model clears." },
  ];

  const tabs = $("#modelTabs");
  const chart = $("#emChart");
  tabs.innerHTML = MODELS.map((m, i) =>
    `<button type="button" role="tab" class="tab" aria-selected="${i === 0}" data-i="${i}">${m.name}</button>`).join("");
  chart.innerHTML = REGIMES.map((r, i) => `
    <div class="col"><div class="col__bar${i === 3 ? " col__bar--kd" : ""}"><span class="col__val"></span></div></div>`).join("");
  chart.insertAdjacentHTML("afterend",
    `<div class="chart__x">${REGIMES.map((r) => `<span>${r}</span>`).join("")}</div>`);

  function drawModel(i) {
    const m = MODELS[i];
    $$(".tab", tabs).forEach((t, j) => t.setAttribute("aria-selected", String(j === i)));
    $$(".col__bar", chart).forEach((b, j) => {
      const v = m.em[j];
      b.classList.toggle("col__bar--na", v === null);
      b.style.height = v === null ? "" : v + "%";
      $(".col__val", b).textContent = v === null ? "n/a" : fmt(v) + "%";
    });
    chart.setAttribute("aria-label", `${m.name} exact match: ` +
      REGIMES.map((r, j) => `${r} ${m.em[j] === null ? "not applicable" : m.em[j] + "%"}`).join(", "));
    $("#emCaption").textContent = m.note;
  }
  tabs.addEventListener("click", (e) => {
    const t = e.target.closest(".tab");
    if (t) drawModel(+t.dataset.i);
  });
  whenVisible(chart, () => drawModel(0));

  /* ---------------- ablation ---------------- */
  const ABL = [
    { name: "Zero-shot", sub: "no training", em: 0.65, bias: 63.46, hall: 52.9 },
    { name: "KD, label only", sub: "learns which", em: 41.33, bias: 34.56, hall: 36.11 },
    { name: "QLoRA-KD", sub: "learns why + which", em: 85.16, bias: 0, hall: 1.65 },
  ];
  const abl = $("#ablation");
  abl.innerHTML = ABL.map((a) => `
    <div class="abl">
      <div class="abl__name">${a.name}<span>${a.sub}</span></div>
      <div class="abl__rows">
        ${[["EM ↑", a.em, "em"], ["Bias ↓", a.bias, "bias"], ["Halluc. ↓", a.hall, "hall"]].map(([l, v, k]) => `
          <div class="abl__row"><span class="mono">${l}</span>
            <span class="abl__track"><span class="abl__fill abl__fill--${k}" data-w="${v}"></span></span>
            <span class="mono">${fmt(v)}</span></div>`).join("")}
      </div>
    </div>`).join("");
  whenVisible(abl, () => $$(".abl__fill", abl).forEach((f) => { f.style.width = f.dataset.w + "%"; }));

  /* ---------------- figures ---------------- */
  $$(".seg__btn").forEach((btn) => btn.addEventListener("click", () => {
    $$(".seg__btn").forEach((b) => b.classList.toggle("is-on", b === btn));
    $$("#figs img").forEach((img) => { img.src = `assets/figures/${img.dataset.base}${btn.dataset.fig}.png`; });
  }));
  $$("#figs img").forEach((img) => img.addEventListener("click", () => {
    const lb = document.createElement("div");
    lb.className = "lightbox";
    lb.innerHTML = `<img src="${img.src}" alt="${img.alt}">`;
    const close = () => { lb.remove(); document.removeEventListener("keydown", esc); };
    const esc = (e) => { if (e.key === "Escape") close(); };
    lb.addEventListener("click", close);
    document.addEventListener("keydown", esc);
    document.body.appendChild(lb);
  }));

  /* ---------------- exercise ---------------- */
  const LABELS = ["Name", "Concept", "Emotion", "Emotional State", "Collective State", "Spiritual"];
  const ex = {
    data: [], pool: [], cur: null, picks: {}, checked: false,
    right: 0, total: 0, bangla: false,
  };

  const escapeHtml = (s) => s.replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  // Highlight the first two occurrences of the target word
  function markSentence(text, word) {
    const parts = [];
    let from = 0, n = 0, idx;
    while (n < 2 && (idx = text.indexOf(word, from)) !== -1) {
      parts.push(escapeHtml(text.slice(from, idx)));
      n += 1;
      parts.push(`<span class="tok tok--plain" data-slot="${n}">${escapeHtml(word)}<sup>${n}</sup></span>`);
      from = idx + word.length;
    }
    parts.push(escapeHtml(text.slice(from)));
    return parts.join("");
  }

  function renderChoices() {
    $$(".ex__q").forEach((fs) => {
      const slot = fs.dataset.slot;
      $(".choices", fs).innerHTML = LABELS.map((l) =>
        `<button type="button" class="choice" data-label="${l}" aria-pressed="false">${l}</button>`).join("");
      fs.addEventListener("click", (e) => {
        const c = e.target.closest(".choice");
        if (!c || ex.checked) return;
        ex.picks[slot] = c.dataset.label;
        $$(".choice", fs).forEach((b) => b.setAttribute("aria-pressed", String(b === c)));
        $("#exCheck").disabled = !(ex.picks[1] && ex.picks[2]);
      });
    });
  }

  function renderWhy() {
    const c = ex.cur;
    $("#exWhy1").textContent = ex.bangla ? c.why1_bn : c.why1_en;
    $("#exWhy2").textContent = ex.bangla ? c.why2_bn : c.why2_en;
    $$("#exWhy1, #exWhy2").forEach((p) => p.classList.toggle("bn", ex.bangla));
    $("#exLang").textContent = ex.bangla ? "English explanation" : "বাংলা ব্যাখ্যা";
    $("#exLang").setAttribute("aria-pressed", String(ex.bangla));
  }

  function nextItem() {
    if (!ex.pool.length) return;
    let c;
    do { c = ex.pool[Math.floor(Math.random() * ex.pool.length)]; }
    while (ex.pool.length > 1 && c === ex.cur);
    ex.cur = c; ex.picks = {}; ex.checked = false;

    $("#exId").textContent = "#" + c.id;
    $("#exType").textContent = c.cat;
    $("#exSentence").innerHTML = markSentence(c.bn, c.w);
    $("#exEnglish").textContent = "“" + c.en + "”";
    $$(".choice").forEach((b) => { b.className = "choice"; b.setAttribute("aria-pressed", "false"); });
    $("#exCheck").disabled = true;
    $("#exReveal").hidden = true;
  }

  function check() {
    if (ex.checked || !(ex.picks[1] && ex.picks[2])) return;
    ex.checked = true;
    $("#exCheck").disabled = true;
    const c = ex.cur;
    const gold = { 1: c.l1, 2: c.l2 };
    let ok = 0;
    $$(".ex__q").forEach((fs) => {
      const slot = fs.dataset.slot;
      $$(".choice", fs).forEach((b) => {
        if (b.dataset.label === gold[slot]) b.classList.add("is-correct");
        else if (b.dataset.label === ex.picks[slot]) b.classList.add("is-wrong");
      });
      if (ex.picks[slot] === gold[slot]) ok += 1;
    });
    $$("#exSentence .tok").forEach((t) => {
      const lab = gold[t.dataset.slot];
      t.className = "tok " + (lab === "Name" ? "tok--name" : "tok--sense");
    });

    ex.total += 1;
    if (ok === 2) ex.right += 1;
    $("#exScore").textContent = `Score ${ex.right} / ${ex.total}`;

    // was the reader caught by the dominant-meaning trap?
    const missedName = [1, 2].some((s) => gold[s] === "Name" && ex.picks[s] !== "Name");
    $("#exVerdict").textContent = ok === 2
      ? "Exact match. Both readings correct."
      : missedName
        ? "You missed the name. That is the dominant-meaning bias LLMs show too."
        : ok === 1 ? "One of two correct." : "Not this time. Read the explanation below.";
    $("#exL1").textContent = c.l1;
    $("#exL2").textContent = c.l2;
    $("#exNote").textContent = c.note_en;
    renderWhy();
    $("#exReveal").hidden = false;
  }

  function applyFilter() {
    const v = $("#exCat").value;
    ex.pool = v ? ex.data.filter((d) => d.cat === v) : ex.data.slice();
    nextItem();
  }

  renderChoices();
  $("#exCheck").addEventListener("click", check);
  $("#exNext").addEventListener("click", nextItem);
  $("#exLang").addEventListener("click", () => { ex.bangla = !ex.bangla; if (ex.cur) renderWhy(); });
  $("#exCat").addEventListener("change", applyFilter);

  fetch("data/samples.json")
    .then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then((data) => {
      ex.data = data;
      const cats = Array.from(new Set(data.map((d) => d.cat))).sort();
      $("#exCat").insertAdjacentHTML("beforeend",
        cats.map((c) => `<option value="${c}">${c.replace("↔", " ↔ ")}</option>`).join(""));
      applyFilter();
    })
    .catch(() => {
      $("#exSentence").textContent = "Could not load sample data. Open this page through a web server (e.g. GitHub Pages) rather than as a local file.";
      $("#exSentence").classList.remove("bn");
    });

  /* ---------------- copy bibtex ---------------- */
  $("#copyBib").addEventListener("click", async () => {
    const btn = $("#copyBib");
    const text = $("#bibtex").innerText;
    try {
      await navigator.clipboard.writeText(text);
      btn.textContent = "Copied ✓";
    } catch (e) {
      const r = document.createRange();
      r.selectNodeContents($("#bibtex"));
      const s = getSelection(); s.removeAllRanges(); s.addRange(r);
      btn.textContent = "Press Ctrl+C";
    }
    setTimeout(() => { btn.textContent = "Copy BibTeX"; }, 1800);
  });

  /* ---------------- reveal-on-scroll ---------------- */
  if ("IntersectionObserver" in window && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); } });
    }, { threshold: 0.08 });
    $$(".unit > *").forEach((el) => { el.classList.add("reveal"); io.observe(el); });
  }
})();
