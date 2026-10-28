/* When a Name Is Not a Name: site interactions (no dependencies) */
(function () {
  "use strict";

  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;

  function whenVisible(el, fn, threshold = 0.3) {
    if (!el) return;
    if (!("IntersectionObserver" in window)) { fn(); return; }
    const io = new IntersectionObserver((es) => {
      if (es.some((e) => e.isIntersecting)) { io.disconnect(); fn(); }
    }, { threshold });
    io.observe(el);
  }

  /* ---------------- hero: one spelling, two lives ---------------- */
  const WORDS = [
    { w: "মায়া", ipa: "/māyā/", kind: "emotion", def: "deep, affectionate compassion; a tender attachment to someone." },
    { w: "আশা", ipa: "/āśā/", kind: "concept", def: "hope; the expectation that something good will come." },
    { w: "গগন", ipa: "/gɔgon/", kind: "concept", def: "the sky; the vast celestial firmament." },
    { w: "আরিফ", ipa: "/ārif/", kind: "spiritual", def: "one who knows the divine through inner, intuitive insight (Sufi)." },
    { w: "ঈমান", ipa: "/īmān/", kind: "spiritual", def: "faith; unwavering moral and religious integrity." },
  ];
  const art = $("#twoLives");
  let wi = 0, lastClick = 0;
  function showWord(i) {
    const d = WORDS[i];
    art.classList.add("is-flip");
    setTimeout(() => {
      $$("[data-w]", art).forEach((el) => { el.textContent = d.w; });
      $("#dIpa").textContent = d.ipa;
      $("#dKind").textContent = d.kind;
      $("#dDef").textContent = d.def;
      art.classList.remove("is-flip");
    }, reduced ? 0 : 300);
  }
  $("#nextWord").addEventListener("click", () => { wi = (wi + 1) % WORDS.length; showWord(wi); lastClick = performance.now(); });
  if (!reduced) setInterval(() => {
    if (document.hidden || performance.now() - lastClick < 8000) return;
    wi = (wi + 1) % WORDS.length; showWord(wi);
  }, 5000);

  /* ---------------- who is reading ---------------- */
  const read = $("#read");
  const VERDICT = {
    human: "✓ Name, then Emotion. The word নামের (“named”) tells a Bangla reader the first মায়া is a girl.",
    llm: "✗ Emotion, then Emotion. The model knows মায়া as a feeling and forgets the girl. This is dominant-meaning bias.",
  };
  function setRead(mode) {
    read.dataset.mode = mode;
    $$(".read__tabs button", read).forEach((b) => b.setAttribute("aria-selected", String(b.dataset.mode === mode)));
    $(".w1 small", read).textContent = mode === "human" ? "Name" : "Emotion";
    $(".w2 small", read).textContent = "Emotion";
    $("#readVerdict").textContent = VERDICT[mode];
  }
  $$(".read__tabs button", read).forEach((b) => b.addEventListener("click", () => setRead(b.dataset.mode)));
  setRead("human");

  /* ---------------- counters ---------------- */
  $$("[data-count]").forEach((el) => {
    const target = parseFloat(el.dataset.count);
    const dec = parseInt(el.dataset.decimals || "0", 10);
    const show = (v) => { el.textContent = dec ? v.toFixed(dec) : Math.round(v).toLocaleString("en-US"); };
    if (reduced) return;
    show(0);
    whenVisible(el, () => {
      const t0 = performance.now(), dur = 1300;
      (function step(t) {
        const p = Math.min(1, (t - t0) / dur);
        show(target * (1 - Math.pow(1 - p, 3)));
        if (p < 1) requestAnimationFrame(step);
      })(t0);
    });
  });

  /* ---------------- results chart ---------------- */
  const REGIMES = ["Zero-shot", "Few-shot", "Cultural CoT", "QLoRA-KD"];
  const MODELS = [
    { name: "Qwen2.5-1.5B", em: [0.65, 8.39, 30.97, 85.16], note: "From almost zero to 85.16%. Bias falls from 63.46% to 0.00%." },
    { name: "Llama-3.2-3B", em: [10.97, 22.58, 15.16, 82.42], note: "Cultural CoT doesn't help Llama, but distillation lifts it to 82.42% with 2.80% bias." },
    { name: "TituLLM-1B", em: [0.11, 0.31, 1.14, 87.91], note: "The Bangla-specific model fails every prompt, then becomes the strongest system of all." },
    { name: "GPT-4o-mini", em: [43.87, 49.68, null, null], note: "Closed model, prompting only. Its best (49.68%) is the red line every distilled small model clears." },
  ];
  const tabs = $("#modelTabs"), sewn = $("#sewn");
  tabs.innerHTML = MODELS.map((m, i) => `<button type="button" role="tab" aria-selected="${i === 0}" data-i="${i}">${m.name}</button>`).join("");
  sewn.innerHTML = `<div class="sewn__ceiling" aria-hidden="true"><span>GPT-4o-mini best · 49.68</span></div>` +
    REGIMES.map((r, j) => `
      <div class="row${j === 3 ? " row--kd" : ""}">
        <span class="row__label">${r}</span>
        <span class="row__track"><span class="row__fill"><span class="row__val"></span></span></span>
      </div>`).join("");

  function placeCeiling() {
    const track = $(".row__track", sewn);
    $(".sewn__ceiling", sewn).style.left = (track.offsetLeft + track.offsetWidth * 0.4968) + "px";
  }
  function drawModel(i) {
    const m = MODELS[i];
    $$("button", tabs).forEach((b, j) => b.setAttribute("aria-selected", String(j === i)));
    $$(".row", sewn).forEach((row, j) => {
      const v = m.em[j];
      const fill = $(".row__fill", row), val = $(".row__val", row);
      row.classList.toggle("row--na", v === null);
      fill.style.width = v === null ? "0%" : Math.max(v, 1.5) + "%";
      val.textContent = v === null ? "not tested" : v.toFixed(2) + "%";
      // keep long bars' labels inside the bar so they never overflow on phones
      const inside = v !== null && v > 70;
      val.style.left = inside ? "auto" : "";
      val.style.right = inside ? "10px" : "";
      val.style.color = inside ? "#fff" : "";
    });
    sewn.setAttribute("aria-label", `${m.name} exact match: ` + REGIMES.map((r, j) => `${r} ${m.em[j] === null ? "not tested" : m.em[j] + "%"}`).join(", "));
    $("#chartNote").textContent = m.note;
  }
  tabs.addEventListener("click", (e) => { const b = e.target.closest("button"); if (b) drawModel(+b.dataset.i); });
  placeCeiling();
  addEventListener("resize", placeCeiling);
  whenVisible(sewn, () => drawModel(0), 0.2);

  /* ---------------- figures ---------------- */
  $$(".seg button").forEach((b) => b.addEventListener("click", () => {
    $$(".seg button").forEach((x) => x.classList.toggle("is-on", x === b));
    $$("#figgrid img").forEach((img) => { img.src = `assets/figures/${img.dataset.base}${b.dataset.fig}.png`; });
  }));
  $$("#figgrid img").forEach((img) => img.addEventListener("click", () => {
    const lb = document.createElement("div");
    lb.className = "lightbox";
    lb.innerHTML = `<img src="${img.src}" alt="${img.alt}">`;
    const close = () => { lb.remove(); removeEventListener("keydown", onKey); };
    const onKey = (e) => { if (e.key === "Escape") close(); };
    lb.addEventListener("click", close);
    addEventListener("keydown", onKey);
    document.body.appendChild(lb);
  }));

  /* ---------------- game ---------------- */
  const LABELS = ["Name", "Concept", "Emotion", "Emotional State", "Collective State", "Spiritual"];
  const g = { data: [], pool: [], cur: null, picks: {}, done: false, right: 0, total: 0, streak: 0, bn: false };
  const esc = (s) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  // Bangla vowel signs, hasanta, nukta, chandrabindu etc. must stay with the letter before them
  const MARK = /[ঁ-ঃ়া-ৌ্ৗ‌‍]/;
  function clusterEnd(text, end) {
    while (end < text.length && MARK.test(text[end])) {
      end += text[end] === "্" && end + 1 < text.length ? 2 : 1; // hasanta joins the next consonant
    }
    return end;
  }

  function markSentence(text, w) {
    const out = []; let from = 0, n = 0, i;
    while (n < 2 && (i = text.indexOf(w, from)) !== -1) {
      out.push(esc(text.slice(from, i)));
      n += 1;
      const end = clusterEnd(text, i + w.length);
      out.push(`<span class="gt" data-slot="${n}">${esc(text.slice(i, end))}<sup>${n}</sup></span>`);
      from = end;
    }
    out.push(esc(text.slice(from)));
    return out.join("");
  }

  $$(".q").forEach((fs) => {
    const slot = fs.dataset.slot;
    $(".chips", fs).innerHTML = LABELS.map((l) => `<button type="button" class="chip" data-label="${l}" aria-pressed="false">${l}</button>`).join("");
    fs.addEventListener("click", (e) => {
      const c = e.target.closest(".chip");
      if (!c || g.done) return;
      g.picks[slot] = c.dataset.label;
      $$(".chip", fs).forEach((b) => b.setAttribute("aria-pressed", String(b === c)));
      $("#gCheck").disabled = !(g.picks[1] && g.picks[2]);
    });
  });

  function langLabel() { $("#gLang").textContent = g.bn ? "Explain in English" : "বাংলায় ব্যাখ্যা"; }
  function renderWhy() {
    const c = g.cur;
    $("#gWhy1").textContent = g.bn ? c.why1_bn : c.why1_en;
    $("#gWhy2").textContent = g.bn ? c.why2_bn : c.why2_en;
    $$("#gWhy1, #gWhy2").forEach((p) => p.classList.toggle("bn-text", g.bn));
  }

  function nextItem() {
    if (!g.pool.length) return;
    let c;
    do { c = g.pool[Math.floor(Math.random() * g.pool.length)]; } while (g.pool.length > 1 && c === g.cur);
    g.cur = c; g.picks = {}; g.done = false;
    $("#gId").textContent = "#" + c.id;
    $("#gType").textContent = c.cat.replace("↔", " ↔ ");
    $("#gSentence").innerHTML = markSentence(c.bn, c.w);
    $("#gEnglish").textContent = "“" + c.en + "”";
    $$(".chip").forEach((b) => { b.className = "chip"; b.setAttribute("aria-pressed", "false"); });
    $("#gCheck").disabled = true;
    $("#gOut").hidden = true;
  }

  function check() {
    if (g.done || !(g.picks[1] && g.picks[2])) return;
    g.done = true;
    $("#gCheck").disabled = true;
    const c = g.cur, gold = { 1: c.l1, 2: c.l2 };
    let ok = 0;
    $$(".q").forEach((fs) => {
      const s = fs.dataset.slot;
      $$(".chip", fs).forEach((b) => {
        if (b.dataset.label === gold[s]) b.classList.add("is-right");
        else if (b.dataset.label === g.picks[s]) b.classList.add("is-wrong");
      });
      if (g.picks[s] === gold[s]) ok += 1;
    });
    $$("#gSentence .gt").forEach((t) => t.classList.add(gold[t.dataset.slot] === "Name" ? "gt--name" : "gt--sense"));

    g.total += 1;
    if (ok === 2) { g.right += 1; g.streak += 1; } else g.streak = 0;
    $("#gScore").textContent = `${g.right}/${g.total}`;
    $("#gStreak").textContent = g.streak;

    const missedName = [1, 2].some((s) => gold[s] === "Name" && g.picks[s] !== "Name");
    $("#gVerdict").textContent = ok === 2
      ? (g.streak >= 3 ? `Both right, ${g.streak} in a row.` : "Both right. You read it like a native speaker.")
      : missedName ? "You missed the person. That's exactly the mistake the models make."
        : ok === 1 ? "One out of two. Here's the reasoning." : "Not this time. Here's the reasoning.";
    $("#gL1").textContent = c.l1;
    $("#gL2").textContent = c.l2;
    $("#gNote").textContent = c.note_en;
    renderWhy();
    $("#gOut").hidden = false;
  }

  function filter() {
    const v = $("#gCat").value;
    g.pool = v ? g.data.filter((d) => d.cat === v) : g.data.slice();
    nextItem();
  }

  $("#gCheck").addEventListener("click", check);
  $("#gNext").addEventListener("click", nextItem);
  $("#gLang").addEventListener("click", () => { g.bn = !g.bn; langLabel(); if (g.done) renderWhy(); });
  $("#gCat").addEventListener("change", filter);

  fetch("data/samples.json")
    .then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then((data) => {
      g.data = data;
      const cats = Array.from(new Set(data.map((d) => d.cat))).sort();
      $("#gCat").insertAdjacentHTML("beforeend", cats.map((c) => `<option value="${c}">${c.replace("↔", " ↔ ")}</option>`).join(""));
      filter();
    })
    .catch(() => { $("#gSentence").textContent = "Could not load the sentences. Open the site through a web server, e.g. GitHub Pages."; });

  /* ---------------- copy bibtex ---------------- */
  $("#copyBib").addEventListener("click", async () => {
    const b = $("#copyBib");
    try { await navigator.clipboard.writeText($("#bibtex").innerText); b.textContent = "Copied ✓"; }
    catch (e) {
      const r = document.createRange(); r.selectNodeContents($("#bibtex"));
      const s = getSelection(); s.removeAllRanges(); s.addRange(r);
      b.textContent = "Press Ctrl+C";
    }
    setTimeout(() => { b.textContent = "Copy"; }, 1800);
  });

  /* ---------------- nav highlight + reveal ---------------- */
  const links = $$(".top__nav a");
  const targets = links.map((a) => $(a.getAttribute("href")));
  function drawNav() {
    let active = -1;
    targets.forEach((t, i) => { if (t && t.getBoundingClientRect().top < innerHeight * 0.4) active = i; });
    links.forEach((a, i) => a.classList.toggle("is-active", i === active));
  }
  addEventListener("scroll", drawNav, { passive: true });
  drawNav();

  if (!reduced && "IntersectionObserver" in window) {
    const io = new IntersectionObserver((es) => es.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); }
    }), { threshold: 0.1 });
    $$(".sec-head, .problem__copy, .read, .patch, .tree, .thread li, .chartcard, .bigstat, .lesson, .game, .figgrid figure, .slip")
      .forEach((el, i) => { el.classList.add("rv"); el.style.transitionDelay = `${(i % 4) * 80}ms`; io.observe(el); });
  }
})();
