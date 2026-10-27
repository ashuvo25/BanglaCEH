# Project website

Static site for *When a Name Is Not a Name* (WiNLP 2026). Plain HTML, CSS and JavaScript, with no build step.

```
docs/
├── index.html            # the page
├── css/style.css
├── js/main.js            # charts, exercise, theme toggle
├── data/samples.json     # 80 benchmark instances used by the exercise
├── assets/figures/       # paper figures (copied from Conf-loss-diagram/)
└── .nojekyll
```

## Deploy on GitHub Pages

1. Push this folder to the default branch (`main`).
2. On GitHub, go to **Settings → Pages**.
3. Under **Build and deployment**, set **Source** to *Deploy from a branch*, choose branch `main` and folder `/docs`, then save.
4. After a minute the site is live at `https://ashuvo25.github.io/BanglaCEH/`.

## Preview locally

```bash
cd docs && python3 -m http.server 8000
# open http://localhost:8000
```

Use a local server rather than opening `index.html` directly, because the exercise loads `data/samples.json` with `fetch`.

## Editing

- **Authors and affiliations:** the `.authors` block near the top of `index.html`.
- **BibTeX:** the `#bibtex` block in Unit 9. Replace it with the official entry from the ACL Anthology page if it differs.
- **Results numbers:** the `MODELS` and `ABL` arrays in `js/main.js`, plus the table in `index.html`.
- **Exercise sentences:** regenerate `data/samples.json` from `ceh_knowledge_distillation.json`.
