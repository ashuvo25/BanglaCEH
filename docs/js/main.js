/* When a Name Is Not a Name: site interactions (no dependencies) */
(function () {
  "use strict";

  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, t) => a + (b - a) * t;

  function whenVisible(el, fn, threshold = 0.3) {
    if (!el) return;
    if (!("IntersectionObserver" in window)) { fn(); return; }
    const io = new IntersectionObserver((es) => {
      if (es.some((e) => e.isIntersecting)) { io.disconnect(); fn(); }
    }, { threshold });
    io.observe(el);
  }

  /* ---------------- cursor ---------------- */
  const cursor = $(".cursor");
  if (matchMedia("(pointer: fine)").matches && !reduced) {
    let cx = 0, cy = 0, tx = 0, ty = 0;
    addEventListener("mousemove", (e) => { tx = e.clientX; ty = e.clientY; cursor.classList.add("is-on"); });
    document.addEventListener("mouseleave", () => cursor.classList.remove("is-on"));
    (function loop() {
      cx = lerp(cx, tx, 0.22); cy = lerp(cy, ty, 0.22);
      cursor.style.transform = `translate(${cx}px, ${cy}px) translate(-50%, -50%)`;
      requestAnimationFrame(loop);
    })();
    document.addEventListener("mouseover", (e) => {
      cursor.classList.toggle("is-big", !!e.target.closest("a, button, select, .tile, .find, img"));
    });
  }

  /* ---------------- hero: one word, two readings ---------------- */
  const WORDS = [
    { w: "মায়া", r: "Maya", name: "Maya, a girl", sense: "affectionate compassion" },
    { w: "আশা", r: "Asha", name: "Asha, a girl", sense: "hope" },
    { w: "গগন", r: "Gagan", name: "Gagan, a boy", sense: "the sky, the firmament" },
    { w: "আরিফ", r: "Arif", name: "Arif, a boy", sense: "one who knows the divine" },
    { w: "ঈমান", r: "Iman", name: "Iman, a man", sense: "faith, moral integrity" },
  ];
  const split = $("#split");
  const word = $(".split__word", split);
  let wi = 0;

  function setWord(i) {
    const d = WORDS[i];
    split.classList.add("is-swapping");
    setTimeout(() => {
      $$("[data-word]", split).forEach((l) => { l.textContent = d.w; });
      $("#tagName").textContent = d.name;
      $("#tagSense").textContent = d.sense;
      $("#splitSr").textContent = `${d.w}, ${d.r}: ${d.name}, and ${d.sense}`;
      split.classList.remove("is-swapping");
    }, reduced ? 0 : 450);
  }
  if (!reduced) setInterval(() => { if (!document.hidden) { wi = (wi + 1) % WORDS.length; setWord(wi); } }, 3800);

  // pointer pulls the two readings apart
  const hero = $("#hero");
  let idle = 0;
  hero.addEventListener("pointermove", (e) => {
    const r = hero.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width - 0.5;
    const y = (e.clientY - r.top) / r.height - 0.5;
    word.style.setProperty("--dx", `${(x * 70).toFixed(1)}px`);
    word.style.setProperty("--dy", `${(y * 30).toFixed(1)}px`);
    idle = performance.now();
  });
  if (!reduced) {
    (function breathe(t) {
      if (performance.now() - idle > 1500) {
        word.style.setProperty("--dx", `${(Math.sin(t / 900) * 14).toFixed(1)}px`);
        word.style.setProperty("--dy", `${(Math.cos(t / 1300) * 4).toFixed(1)}px`);
      }
      requestAnimationFrame(breathe);
    })(0);
  }

  /* ---------------- marquee ---------------- */
  const MQ = [["মায়া", "Maya"], ["আশা", "Asha"], ["গগন", "Gagan"], ["আরিফ", "Arif"], ["ঈমান", "Iman"],
    ["দীপ্তি", "Dipti"], ["সুনীল", "Sunil"], ["ভ্রমর", "Bhromor"], ["হৃদয়", "Hridoy"], ["সোহাগী", "Sohagi"]];
  const row = MQ.map(([b, r]) => `<span class="marquee__item"><span class="bn">${b}</span><span class="mono">${r}</span><i>✦</i></span>`).join("");
  $("#marquee").innerHTML = row + row;

  /* ---------------- manifesto: words light up on scroll ---------------- */
  const man = $("#manifesto");
  const KEYS = ["hope.", "Hope.", "Sky.", "Compassion.", "Faith.", "person,", "girl."];
  man.innerHTML = man.textContent.trim().split(/\s+/)
    .map((w) => `<span class="w${KEYS.includes(w) ? " is-key" : ""}">${w}</span>`).join(" ");
  const manWords = $$(".w", man);
  function litManifesto() {
    const r = man.getBoundingClientRect();
    const p = clamp((innerHeight * 0.85 - r.top) / (r.height + innerHeight * 0.35), 0, 1);
    const n = Math.round(p * manWords.length);
    manWords.forEach((w, i) => w.classList.toggle("is-lit", i < n));
  }

  /* ---------------- lens: human vs LLM reading ---------------- */
  const lens = $("#lensCard");
  const VERDICT = {
    human: "✓ Name + Emotion. The marker নামের (“named”) points to a person.",
    llm: "✗ Emotion + Emotion. The model sees মায়া and forgets the girl. This is dominant-meaning bias.",
  };
  function setLens(mode) {
    lens.dataset.mode = mode;
    $$(".switch__btn", lens).forEach((b) => b.classList.toggle("is-on", b.dataset.mode === mode));
    $(".tk--1 .tk__l", lens).textContent = mode === "human" ? "Name" : "Emotion";
    $(".tk--2 .tk__l", lens).textContent = "Emotion";
    $("#lensVerdict").textContent = VERDICT[mode];
  }
  $$(".switch__btn", lens).forEach((b) => b.addEventListener("click", () => setLens(b.dataset.mode)));
  setLens("human");
  lens.addEventListener("pointermove", (e) => {
    const r = lens.getBoundingClientRect();
    lens.style.setProperty("--mx", `${e.clientX - r.left}px`);
    lens.style.setProperty("--my", `${e.clientY - r.top}px`);
  });

  /* ---------------- counters ---------------- */
  $$("[data-count]").forEach((el) => {
    const target = parseFloat(el.dataset.count);
    const dec = parseInt(el.dataset.decimals || "0", 10);
    const show = (v) => { el.textContent = dec ? v.toFixed(dec) : Math.round(v).toLocaleString("en-US"); };
    if (reduced) { show(target); return; }
    whenVisible(el, () => {
      const t0 = performance.now(), dur = 1600;
      (function step(t) {
        const p = Math.min(1, (t - t0) / dur);
        show(target * (1 - Math.pow(1 - p, 4)));
        if (p < 1) requestAnimationFrame(step);
      })(t0);
    });
  });

  /* ---------------- donut ---------------- */
  const CATS = [
    ["Name ↔ Concept", 795, "#6d8dff"],
    ["Concept ↔ Emotion", 193, "#c27cff"],
    ["Name ↔ Spiritual", 179, "#ff6b3d"],
    ["Name ↔ Emotion", 178, "#ffb347"],
    ["Emotion ↔ State", 171, "#7be0a4"],
  ];
  const total = CATS.reduce((s, c) => s + c[1], 0);
  $("#legend").innerHTML = CATS.map(([l, n, c]) => `<li><i style="background:${c}"></i>${l}<b>${n}</b></li>`).join("");
  $("#donut").setAttribute("aria-label", "Entanglement types: " + CATS.map(([l, n]) => `${l} ${n}`).join(", "));
  whenVisible($("#donut"), () => {
    let acc = 0;
    const stops = CATS.map(([, n, c]) => { const a = acc; acc += (n / total) * 100; return `${c} ${a.toFixed(2)}% ${(acc - 0.4).toFixed(2)}%, transparent ${(acc - 0.4).toFixed(2)}% ${acc.toFixed(2)}%`; });
    $("#donut").style.background = `conic-gradient(${stops.join(", ")})`;
  });

  /* ---------------- meltdown (sticky scroll) ---------------- */
  const STAGES = [
    { name: "Zero-shot", em: 0.65, color: "#ff6b3d", note: "Out of the box, it almost never gets both readings right. 63.46% of the time it simply misses the name." },
    { name: "Few-shot", em: 8.39, color: "#ff8f4d", note: "Worked examples help the format, but not the culture." },
    { name: "Cultural CoT", em: 30.97, color: "#c27cff", note: "Make it argue for both readings first. Bias falls to 2.88%, with no training at all." },
    { name: "QLoRA-KD", em: 85.16, color: "#6d8dff", note: "Distil cultural explanations into the model. 85.16% exact match. Bias: 0.00%." },
  ];
  const melt = $("#results");
  const meltNum = $("#meltNum");
  const meltDots = $$("#meltDots li");
  let meltStage = -1;
  function drawMelt() {
    const r = melt.getBoundingClientRect();
    const p = clamp(-r.top / (r.height - innerHeight), 0, 1);
    const f = p * (STAGES.length - 1);
    const i = Math.min(STAGES.length - 2, Math.floor(f));
    const t = clamp((f - i - 0.35) / 0.3, 0, 1); // hold, then move
    meltNum.textContent = lerp(STAGES[i].em, STAGES[i + 1].em, t).toFixed(2);
    const s = Math.round(f);
    if (s !== meltStage) {
      meltStage = s;
      $("#meltStage").textContent = STAGES[s].name;
      $("#meltNote").textContent = STAGES[s].note;
      $("#meltGlow").style.background = STAGES[s].color;
      meltDots.forEach((d, j) => d.classList.toggle("is-on", j === s));
    }
  }
  meltDots.forEach((d, j) => {
    d.style.cursor = "pointer";
    d.addEventListener("click", () => {
      const top = melt.offsetTop + (melt.offsetHeight - innerHeight) * (j / (STAGES.length - 1));
      scrollTo({ top, behavior: reduced ? "auto" : "smooth" });
    });
  });

  /* ---------------- race ---------------- */
  const LANES = [
    { name: "Qwen2.5-1.5B", tag: "open", prompt: 30.97, kd: 85.16 },
    { name: "Llama-3.2-3B", tag: "open", prompt: 22.58, kd: 82.42 },
    { name: "TituLLM-1B", tag: "Bangla", prompt: 1.14, kd: 87.91, crown: true },
    { name: "GPT-4o-mini", tag: "closed", prompt: 49.68, kd: null },
  ];
  const board = $("#raceBoard");
  board.insertAdjacentHTML("beforeend", LANES.map((l) => `
    <div class="lane${l.crown ? " lane--crown" : ""}">
      <div class="lane__name">${l.name}<em>${l.tag}</em></div>
      <div class="lane__track" role="img" aria-label="${l.name}: best prompting ${l.prompt}%${l.kd ? `, after QLoRA-KD ${l.kd}%` : ""}">
        ${l.kd ? `<div class="lane__bar lane__bar--kd" data-w="${l.kd}">${l.kd.toFixed(2)}</div>` : ""}
        <div class="lane__bar lane__bar--prompt" data-w="${l.prompt}">${l.prompt.toFixed(2)}</div>
      </div>
    </div>`).join(""));
  whenVisible(board, () => $$(".lane__bar", board).forEach((b) => { b.style.width = `max(${b.dataset.w}%, 64px)`; }), 0.2);

  /* ---------------- figures ---------------- */
  $$(".seg__b").forEach((b) => b.addEventListener("click", () => {
    $$(".seg__b").forEach((x) => x.classList.toggle("is-on", x === b));
    $$("#figRail img").forEach((img) => { img.src = `assets/figures/${img.dataset.base}${b.dataset.fig}.png`; });
  }));
  $$("#figRail img").forEach((img) => img.addEventListener("click", () => {
    const lb = document.createElement("div");
    lb.className = "lightbox";
    lb.innerHTML = `<img src="${img.src}" alt="${img.alt}">`;
    const close = () => { lb.remove(); removeEventListener("keydown", esc); };
    const esc = (e) => { if (e.key === "Escape") close(); };
    lb.addEventListener("click", close);
    addEventListener("keydown", esc);
    document.body.appendChild(lb);
  }));

  /* ---------------- game ---------------- */
  const LABELS = ["Name", "Concept", "Emotion", "Emotional State", "Collective State", "Spiritual"];
  const g = { data: [], pool: [], cur: null, picks: {}, done: false, right: 0, total: 0, streak: 0, bn: false };
  const esc = (s) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  function markSentence(text, w) {
    const out = []; let from = 0, n = 0, i;
    while (n < 2 && (i = text.indexOf(w, from)) !== -1) {
      out.push(esc(text.slice(from, i)));
      n += 1;
      out.push(`<span class="gt" data-slot="${n}">${esc(w)}<sup>${n}</sup></span>`);
      from = i + w.length;
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

  function renderWhy() {
    const c = g.cur;
    $("#gWhy1").textContent = g.bn ? c.why1_bn : c.why1_en;
    $("#gWhy2").textContent = g.bn ? c.why2_bn : c.why2_en;
    $$("#gWhy1, #gWhy2").forEach((p) => p.classList.toggle("bn-text", g.bn));
    $("#gLang").textContent = g.bn ? "English" : "বাংলা";
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
    $("#gNext").textContent = "Skip →";
    $("#gReveal").hidden = true;
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
      ? (g.streak > 2 ? `Perfect. ${g.streak} in a row: better than GPT-4o-mini.` : "Perfect. Both readings right.")
      : missedName ? "You missed the name. That's the same bias the models have."
        : ok === 1 ? "Half right. Here's the reasoning." : "Not quite. Here's the reasoning.";
    $("#gL1").textContent = c.l1;
    $("#gL2").textContent = c.l2;
    $("#gNote").textContent = c.note_en;
    renderWhy();
    $("#gReveal").hidden = false;
    $("#gNext").textContent = "Next sentence →";
  }

  function filter() {
    const v = $("#gCat").value;
    g.pool = v ? g.data.filter((d) => d.cat === v) : g.data.slice();
    nextItem();
  }

  $("#gCheck").addEventListener("click", check);
  $("#gNext").addEventListener("click", nextItem);
  $("#gLang").addEventListener("click", () => { g.bn = !g.bn; if (g.done) renderWhy(); else $("#gLang").textContent = g.bn ? "English" : "বাংলা"; });
  $("#gCat").addEventListener("change", filter);

  fetch("data/samples.json")
    .then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then((data) => {
      g.data = data;
      const cats = Array.from(new Set(data.map((d) => d.cat))).sort();
      $("#gCat").insertAdjacentHTML("beforeend", cats.map((c) => `<option value="${c}">${c.replace("↔", " ↔ ")}</option>`).join(""));
      filter();
    })
    .catch(() => { $("#gSentence").textContent = "Could not load the sample sentences. Open the site through a web server, e.g. GitHub Pages."; });

  /* ---------------- copy bibtex ---------------- */
  $("#copyBib").addEventListener("click", async () => {
    const b = $("#copyBib");
    try { await navigator.clipboard.writeText($("#bibtex").innerText); b.textContent = "copied ✓"; }
    catch (e) {
      const r = document.createRange(); r.selectNodeContents($("#bibtex"));
      const s = getSelection(); s.removeAllRanges(); s.addRange(r);
      b.textContent = "press ctrl+c";
    }
    setTimeout(() => { b.textContent = "copy"; }, 1800);
  });

  /* ---------------- nav active + reveal ---------------- */
  const navLinks = $$(".nav__links a");
  const navTargets = navLinks.map((a) => $(a.getAttribute("href")));
  function drawNav() {
    const y = innerHeight * 0.4;
    let active = -1;
    navTargets.forEach((t, i) => { if (t && t.getBoundingClientRect().top < y) active = i; });
    navLinks.forEach((a, i) => a.classList.toggle("is-active", i === active));
  }

  if (!reduced && "IntersectionObserver" in window) {
    const io = new IntersectionObserver((es) => es.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); }
    }), { threshold: 0.12 });
    $$(".lens__head, .lens__card, .cats, .data h2, .tile, .race h2, .lane, .vs__side, .vs__cap, .find, .play__head, .game, .figs__rail, .term")
      .forEach((el, i) => { el.classList.add("rv"); el.style.transitionDelay = `${(i % 4) * 70}ms`; io.observe(el); });
  }

  let ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => { litManifesto(); drawMelt(); drawNav(); ticking = false; });
  }
  addEventListener("scroll", onScroll, { passive: true });
  addEventListener("resize", onScroll);
  litManifesto(); drawMelt(); drawNav();
})();
