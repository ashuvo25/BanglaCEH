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

/* ================= method: animated walkthrough ================= */
(function () {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!$("#method")) return;

  const seg = "Segmenter" in Intl ? new Intl.Segmenter("bn", { granularity: "grapheme" }) : null;
  const graphemes = (t) => (seg ? Array.from(seg.segment(t), (x) => x.segment) : Array.from(t));
  const esc = (t) => t.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));

  // each scene runs an async timeline; a new run cancels the previous one
  function timeline(scene, fn) {
    const id = (scene._run = (scene._run || 0) + 1);
    const alive = () => scene._run === id;
    const wait = (ms) => new Promise((r) => setTimeout(r, reduced ? 0 : ms));
    fn(alive, wait);
  }

  // types [[text, cls], ...] into el, keeping Bangla letters whole
  async function type(el, parts, alive, wait, speed = 14) {
    const units = [];
    parts.forEach(([t, c]) => graphemes(t).forEach((g) => units.push([g, c])));
    let html = "", cur = null;
    const flush = () => { el.innerHTML = html + (cur !== null ? "</span>" : ""); };
    for (let i = 0; i < units.length; i++) {
      if (!alive()) return false;
      const [g, c] = units[i];
      if (c !== cur) { if (cur !== null) html += "</span>"; html += `<span class="${c || ""}">`; cur = c; }
      html += esc(g);
      if (reduced) continue;
      if (i % 2 === 0) { flush(); await wait(speed); }
    }
    flush();
    return true;
  }

  /* ---- 1. dataset ---- */
  const JSON_PARTS = [
    ["{\n  ", ""], ['"id"', "k"], [": 1,\n  ", ""],
    ['"word_bangla"', "k"], [": ", ""], ['"মায়া"', "s"], [",\n  ", ""],
    ['"category"', "k"], [": ", ""], ['"Name↔Emotion"', "s"], [",\n  ", ""],
    ['"narrative_bangla"', "k"], [": ", ""], ['"মায়া নামের মেয়েটিকে … গভীর মায়া জেগে উঠল।"', "s"], [",\n  ", ""],
    ['"token_labels"', "k"], [': { "token_1": ', ""], ['"Name"', "s"], [', "token_2": ', ""], ['"Emotion"', "s"], [" },\n  ", ""],
    ['"why_first"', "k"], [": ", ""], ['"নামের (named) marks a person…"', "s"], [",\n  ", ""],
    ['"cultural_note"', "k"], [": ", ""], ['"parents name daughters after aspirational emotions"', "s"], ["\n}", ""],
  ];
  function playData(scene) {
    $$(".flow > *", scene).forEach((el, i) => { el.dataset.step = ""; el.style.setProperty("--d", i * 260); });
    const json = $("[data-json]", scene), count = $("[data-countup]", scene);
    json.innerHTML = ""; count.textContent = "0";
    timeline(scene, async (alive, wait) => {
      await wait(1500);
      if (!(await type(json, JSON_PARTS, alive, wait, 10))) return;
      const target = +count.dataset.countup, t0 = performance.now();
      (function step(t) {
        if (!alive()) return;
        const p = Math.min(1, (t - t0) / 1200);
        count.textContent = Math.round(target * (1 - Math.pow(1 - p, 3))).toLocaleString("en-US");
        if (p < 1) requestAnimationFrame(step);
      })(t0);
    });
  }

  /* ---- 2. split ---- */
  function playSplit(scene) {
    const box = $("[data-dots]", scene);
    if (!box.children.length) box.innerHTML = "<i></i>".repeat(100);
    const cells = Array.from(box.children);
    cells.forEach((c) => { c.className = ""; });
    const order = cells.map((_, i) => i).sort(() => Math.random() - 0.5);
    timeline(scene, async (alive, wait) => {
      await wait(400);
      for (const i of order) {
        if (!alive()) return;
        const cls = i < 78 ? "d-train" : i < 88 ? "d-val" : "d-test";
        cells[i].className = cls + " pop";
        setTimeout(() => cells[i].classList.remove("pop"), 250);
        await wait(22);
      }
    });
  }

  /* ---- 3. prompting ---- */
  const REPLIES = {
    zero: [
      ["FINAL:\nOccurrence 1: Emotion   ", ""], ["✗ gold is Name", "bad"],
      ["\nOccurrence 2: Emotion   ", ""], ["✓", "ok"],
      ["\n\n→ the girl is missed: dominant-meaning bias", "bad"],
    ],
    few: [
      ["The word মায়া expresses deep compassion in both places…\n", ""],
      ["FINAL:\nOccurrence 1: Emotion   ", ""], ["✗", "bad"],
      ["\nOccurrence 2: Emotion   ", ""], ["✓", "ok"],
      ["\n\n→ the format is learned, the culture is not", "bad"],
    ],
    ccot: [
      ["Occurrence 1\n", ""], ["  A · Name: ", "arg"], ["followed by নামের “named” → a girl\n", ""],
      ["  B · Emotion: ", "arg"], ["no feeling is described here\n", ""], ["  Decision: Name\n", "ok"],
      ["Occurrence 2\n", ""], ["  A · Name: ", "arg"], ["no person is meant\n", ""],
      ["  B · Emotion: ", "arg"], ["“গভীর মায়া জেগে উঠল” → a feeling awoke\n", ""], ["  Decision: Emotion\n", "ok"],
      ["FINAL:\nOccurrence 1: Name      ", ""], ["✓", "ok"], ["\nOccurrence 2: Emotion   ", ""], ["✓", "ok"],
    ],
  };
  function showPrompt(scene, mode, alive, wait) {
    $$(".ptabs button", scene).forEach((b) => b.classList.toggle("is-on", b.dataset.p === mode));
    $("[data-shots]", scene).classList.toggle("is-on", mode === "few");
    return type($("[data-typed]", scene), REPLIES[mode], alive, wait, mode === "ccot" ? 12 : 18);
  }
  function playPrompt(scene, only) {
    timeline(scene, async (alive, wait) => {
      for (const mode of only ? [only] : ["zero", "few", "ccot"]) {
        if (!alive()) return;
        if (!(await showPrompt(scene, mode, alive, wait))) return;
        if (!only && mode !== "ccot") await wait(1600);
      }
    });
  }

  /* ---- 4. parse ---- */
  function playParse(scene) {
    $$(".raw__l", scene).forEach((l) => l.classList.remove("hl"));
    $$(".slot", scene).forEach((l) => l.classList.remove("in"));
    timeline(scene, async (alive, wait) => {
      const hl = (sel) => $$(sel, scene).forEach((l) => l.classList.add("hl"));
      const un = () => $$(".raw__l", scene).forEach((l) => l.classList.remove("hl"));
      const steps = [
        () => hl(".r3"), () => { hl(".r4"); }, () => $(".s1", scene).classList.add("in"),
        () => { un(); hl(".r5"); }, () => $(".s2", scene).classList.add("in"),
        () => { un(); hl(".r1, .r2"); }, () => $(".s3", scene).classList.add("in"),
        () => un(), () => $(".s4", scene).classList.add("in"),
      ];
      await wait(500);
      for (const s of steps) { if (!alive()) return; s(); await wait(650); }
    });
  }

  /* ---- 5. distillation ---- */
  function playKD(scene) {
    const box = $("[data-tokens]", scene);
    if (!box.children.length) {
      box.innerHTML = Array.from({ length: 44 }, (_, i) =>
        `<i class="${i < 16 ? "tk--p" : i < 39 ? "tk--r" : "tk--l"}"></i>`).join("");
    }
    const toks = Array.from(box.children);
    toks.forEach((t) => t.classList.remove("on"));
    timeline(scene, async (alive, wait) => {
      await wait(600);
      for (const t of toks) { if (!alive()) return; t.classList.add("on"); await wait(45); }
    });
  }

  /* ---- 6. evaluation ---- */
  const ROWS = [
    ["Name · Emotion", "Name · Emotion", "ok", "✓ exact"],
    ["Name · Concept", "Concept · Concept", "bias", "✗ missed Name"],
    ["Concept · Emotional State", "Concept · Emotional State", "ok", "✓ exact"],
    ["Name · Spiritual", "Name · Spiritual", "ok", "✓ exact"],
    ["Emotional State · Collective State", "Emotional State · Unknown", "hall", "? hallucination"],
    ["Name · Concept", "Name · Emotion", "part", "½ partial"],
  ];
  function playEval(scene) {
    const body = $("[data-evrows]", scene);
    body.innerHTML = ROWS.map((r, i) => `<tr><td>${i + 1}</td><td>${r[0]}</td><td>${r[1]}</td><td class="res res--${r[2]}">${r[3]}</td></tr>`).join("");
    const t = { em: 0, bias: 0, hall: 0 };
    const draw = () => {
      $('[data-t="em"]', scene).textContent = `${t.em}/6`;
      $('[data-t="bias"]', scene).textContent = `${t.bias}/4`;
      $('[data-t="hall"]', scene).textContent = `${t.hall}/6`;
    };
    draw();
    timeline(scene, async (alive, wait) => {
      await wait(400);
      const rows = Array.from(body.children);
      for (let i = 0; i < rows.length; i++) {
        if (!alive()) return;
        rows[i].classList.add("in");
        const k = ROWS[i][2];
        if (k === "ok") t.em += 1; else if (k === "bias") t.bias += 1; else if (k === "hall") t.hall += 1;
        draw();
        await wait(700);
      }
    });
  }

  const PLAY = { data: playData, split: playSplit, prompt: playPrompt, parse: playParse, kd: playKD, eval: playEval };

  function play(scene) {
    scene.classList.remove("is-play");
    void scene.offsetWidth; // restart CSS transitions
    scene.classList.add("is-play");
    PLAY[scene.dataset.scene](scene);
  }

  const scenes = $$(".ch__scene");
  // draw the static parts up front so nothing looks empty before a scene plays
  const dotsBox = $(".scene-split [data-dots]");
  if (dotsBox && !dotsBox.children.length) dotsBox.innerHTML = "<i></i>".repeat(100);
  const tokBox = $(".scene-kd [data-tokens]");
  if (tokBox && !tokBox.children.length) {
    tokBox.innerHTML = Array.from({ length: 44 }, (_, i) => `<i class="${i < 16 ? "tk--p" : i < 39 ? "tk--r" : "tk--l"}"></i>`).join("");
  }
  scenes.forEach((sc) => {
    $(".replay", sc).addEventListener("click", () => play(sc));
  });
  $$(".scene-prompt .ptabs button").forEach((b) => b.addEventListener("click", () => {
    const sc = b.closest(".ch__scene");
    sc.classList.add("is-play");
    playPrompt(sc, b.dataset.p);
  }));

  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((es) => es.forEach((e) => {
      if (e.isIntersecting && !e.target._played) { e.target._played = true; play(e.target); }
    }), { threshold: 0.2 });
    scenes.forEach((s) => io.observe(s));
  } else scenes.forEach(play);

  // stage map follows the scroll
  const mapLinks = $$("#methodMap a");
  const chs = mapLinks.map((a) => $(a.getAttribute("href")));
  function drawMap() {
    let active = -1;
    chs.forEach((c, i) => { if (c.getBoundingClientRect().top < innerHeight * 0.5) active = i; });
    mapLinks.forEach((a, i) => a.classList.toggle("is-active", i === active));
    const a = mapLinks[active];
    if (a && a !== drawMap.last) {
      drawMap.last = a;
      const map = $("#methodMap");
      map.scrollTo({ left: a.offsetLeft - 8, behavior: reduced ? "auto" : "smooth" });
    }
  }
  addEventListener("scroll", drawMap, { passive: true });
  drawMap();
})();
