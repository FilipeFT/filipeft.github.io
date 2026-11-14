/* make-demo.js — builds engine/demo.html: the layout engine
   rendered as the panorama, for review with the eyes before the
   engine touches the deck. Self-contained: the model, the
   engine, and the relations module are all inlined.

   No connecting lines anywhere: tap a circle and the roads that
   were drawn as lines light — one step, up or down — while the
   rest fades; the panel names the roads and the dive opens the
   view's own opening. The one relationship set is the deck's own
   drawn set, pinned to fund.js's fundEdges by the engine's test.

   usage: node engine/make-demo.js [map page] (writes engine/demo.html) */

'use strict';

const fs = require('fs');
const path = require('path');

const mapPage = process.argv[2] || path.join('out', 'map.html');
const page = fs.readFileSync(mapPage, 'utf8');
const m = page.match(/const DATA = (\{[\s\S]*?\});\nconst SYSTEMS/);
if (!m) { console.error('no DATA payload found in ' + mapPage); process.exit(1); }
const DATA = m[1];

const layoutSrc = fs.readFileSync(path.join('engine', 'layout.js'), 'utf8');
const relSrc = fs.readFileSync(path.join('engine', 'relations.js'), 'utf8');

const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>the map's layout engine — a panorama demo, not the deck</title>
<style>
  :root { --ink:#111; --hair:#c9c2b4; --faint:#8a8474; --accent:#b3002d; }
  * { box-sizing: border-box; }
  body { margin:0; font:14px/1.45 -apple-system,"Segoe UI",sans-serif; color:var(--ink); background:#faf9f6; }
  .bar { position:sticky; top:0; z-index:10; display:flex; flex-wrap:wrap; gap:12px; align-items:center;
         padding:10px 16px; background:#fff; border-bottom:1px solid var(--hair); }
  .bar h1 { font-size:13px; font-weight:600; margin:0 8px 0 0; }
  .bar input[type=range] { width:220px; }
  .bar button { font:600 11px/1 inherit; padding:6px 10px; border:1px solid var(--hair);
                border-radius:999px; background:none; cursor:pointer; }
  .bar button.on { border-color:var(--ink); }
  .readout { font:11px/1.4 monospace; color:var(--faint); white-space:pre; }
  .note { padding:8px 16px; font:italic 12px/1.5 serif; color:var(--faint);
          border-bottom:1px solid var(--hair); }
  .panel { position:sticky; z-index:9; display:flex; flex-wrap:wrap; gap:8px 18px; align-items:baseline;
           padding:10px 16px; background:#fff; border-bottom:1px solid var(--hair); min-height:44px; }
  .panel .who { font-weight:600; }
  .panel .stratum { font-size:11.5px; font-weight:600; letter-spacing:.07em;
                    text-transform:uppercase; color:var(--faint); }
  .panel .route { font:italic 12.5px/1.5 serif; color:#444; }
  .panel .dive-btn { font:600 11px/1 inherit; padding:6px 10px; border:1px solid var(--ink);
                     border-radius:999px; background:none; cursor:pointer; }
  .panel .dive-btn[hidden] { display:none; }
  .dive { padding:10px 16px; font:italic 13px/1.6 serif; color:var(--ink);
          background:#fff; border-bottom:1px solid var(--hair); }
  .dive[hidden] { display:none; }
  .stage { overflow:auto; padding:24px; }
  .holder { position:relative; margin:0 auto; transform-origin:0 0; }
  .canvas { position:relative; }
  .band { position:absolute; border:1px solid var(--hair); border-radius:12px; background:rgba(255,255,255,.6); }
  .band-label { position:absolute; font-size:11.5px; font-weight:600; letter-spacing:.07em;
                color:var(--faint); text-transform:uppercase; text-align:center; }
  .door { position:absolute; width:86px; display:flex; flex-direction:column; align-items:center;
          gap:7px; cursor:pointer; opacity:1; transition:opacity .15s; }
  .door .d-ic { width:46px; height:46px; border-radius:50%; background:#fff; border:1px solid #9a927e;
                display:flex; align-items:center; justify-content:center; font:600 15px/1 serif; }
  .door.soon .d-ic { border-style:dashed; background:transparent; color:var(--faint); }
  .door .d-name { font-size:10.5px; font-weight:600; line-height:1.3; letter-spacing:.03em; text-align:center; }
  .focusing .door { opacity:.2; }
  .focusing .door.hi { opacity:1; }
  .focusing .door.hi .d-ic { border-color:var(--ink); box-shadow:0 0 0 4px rgba(17,17,17,.14); }
  .focusing .door.tapped .d-ic { border-color:var(--accent); box-shadow:0 0 0 4px rgba(179,0,45,.18); }
  .focusing .band-label { opacity:.25; }
  .focusing .band { opacity:.35; }
  .focusing .band.hi { opacity:1; }
  .floor { position:absolute; border-top:1px dashed var(--hair); color:var(--faint);
           font-size:12px; font-style:italic; text-align:center; padding-top:12px; }
</style>
</head>
<body>
<div class="bar">
  <h1>the layout engine, a panorama demo</h1>
  <input id="w" type="range" min="320" max="1920" step="10" value="1340">
  <span id="wv" class="readout"></span>
  <button data-w="1340">desktop</button>
  <button data-w="1024">laptop</button>
  <button data-w="768">tablet</button>
  <button data-w="390">phone</button>
  <button id="fit">fit to window</button>
  <span id="ro" class="readout"></span>
</div>
<div class="note">A prototype of step 3, after the pivot: no connecting lines anywhere — tap
any circle and the roads the lines once drew light — one step, up or down, never a
long distance — while the rest fades; the panel names the roads and the dive opens
the view's own opening. Every storey's frame the same width, every label and row
centred: symmetrical at every scale, doors full size at every width. Not the
deck — the deck still ships its own map until the engine is integrated.</div>
<div class="panel" id="panel"><span class="route" id="hint">tap any circle to light its drawn roads — one step; the rest fades</span></div>
<div class="dive" id="dive" hidden></div>
<div class="stage"><div class="holder" id="holder"><div class="canvas" id="canvas"></div></div></div>
<script>
const DATA = ${DATA};
</script>
<script>
${layoutSrc}
</script>
<script>
${relSrc}
</script>
<script>
/* the one set of relationships: the roads the deck drew as
   lines — a road spanning exactly one storey, or a built-from
   link — and nothing else */
const EDGES = DATA.edges || [];
const REL = ETBRelations.makeRelations(DATA.map, EDGES);

/* ---- the model and its lookup tables -------------------------- */
const bandOf = {}; DATA.map.forEach((b) => b.views.forEach((v) => { bandOf[v] = b; }));
const labelOf = {}; DATA.map.forEach((b) => { labelOf[b.id] = b.label; });
const model = { bands: DATA.map, floors: {
  left: 'the floor beneath is mathematics itself — the machine as thought, all the way down',
  right: 'the floor beneath is physics itself — a voltage high or low, all the way down'
}};

/* the roads the panel names, in reading order */

/* a door's name, wherever the view lives */
function doorName(id) {
  if (DATA.placeholders[id]) return DATA.placeholders[id].title;
  if (DATA.cards[id]) return DATA.cards[id].title;
  if (DATA.trails[id]) return DATA.trails[id].title;
  if (DATA.primers[id]) return DATA.primers[id][1];
  return id;
}

/* the view's own opening: what a dive reveals (in the deck, the
   dive opens the view itself) */
function diveText(id) {
  if (DATA.trails[id] && DATA.trails[id].intro) return DATA.trails[id].intro;
  if (DATA.cards[id] && DATA.cards[id].q) return DATA.cards[id].q;
  if (DATA.placeholders[id] && DATA.placeholders[id].line) return DATA.placeholders[id].line;
  if (DATA.primers[id]) return 'the primer: ' + DATA.primers[id][1] + '.';
  return '';
}

/* ---- the label widths, measured for real --------------------- */
const measure = document.createElement('canvas').getContext('2d');
measure.font = '600 11.5px -apple-system, "Segoe UI", sans-serif';
const widths = { labels: {} };
DATA.map.forEach((b) => {
  widths.labels[b.id] = Math.ceil(
    measure.measureText(b.label).width * 1.07 /* letter-spacing */) + 10;
});

/* ---- render a geometry ---------------------------------------- */
const holder = document.getElementById('holder');
const canvas = document.getElementById('canvas');
const ro = document.getElementById('ro');
const wv = document.getElementById('wv');
let geo = null, fit = false;

function render(avail) {
  geo = ETBLayout.layoutMap(model, widths, avail);
  canvas.className = 'canvas';
  canvas.style.width = geo.width + 'px';
  canvas.style.height = geo.height + 'px';
  canvas.innerHTML = '';
  geo.bands.forEach((g) => {
    const f = document.createElement('div');
    f.className = 'band';
    f.dataset.band = g.id;
    f.style.left = g.x + 'px'; f.style.top = g.y + 'px';
    f.style.width = g.w + 'px'; f.style.height = g.h + 'px';
    canvas.appendChild(f);
    const lb = document.createElement('div');
    lb.className = 'band-label';
    lb.textContent = labelOf[g.id];
    lb.style.left = g.label.x + 'px'; lb.style.top = g.label.y + 'px';
    lb.style.width = g.label.w + 'px';
    canvas.appendChild(lb);
    g.rows.forEach((row) => row.forEach((d) => {
      const el = document.createElement('div');
      el.className = 'door' + (DATA.placeholders[d.id] ? ' soon' : '');
      el.style.left = d.x + 'px'; el.style.top = d.y + 'px';
      el.dataset.go = d.id;
      const ic = document.createElement('span');
      ic.className = 'd-ic';
      ic.textContent = doorName(d.id).charAt(0);
      const nm = document.createElement('span');
      nm.className = 'd-name';
      nm.textContent = doorName(d.id);
      el.appendChild(ic); el.appendChild(nm);
      canvas.appendChild(el);
    }));
  });
  geo.floors.forEach((fl) => {
    const el = document.createElement('div');
    el.className = 'floor';
    el.textContent = fl.text;
    el.style.left = fl.x + 'px'; el.style.top = fl.y + 'px';
    el.style.width = fl.w + 'px';
    canvas.appendChild(el);
  });
  ro.textContent = ' fork ' + geo.fork + '  ' + Math.round(geo.width) +
    'x' + Math.round(geo.height) + '  natW ' + geo.natW;
  place();
  if (focusId) apply();
}

/* ---- the tap: light the roads, fade the rest, tell the story - */
let focusId = null;
const panel = document.getElementById('panel');
const diveEl = document.getElementById('dive');

/* the one-step story: only the roads that were drawn as lines,
   named by direction; the long-distance relations are gone */
function relationSummary(id) {
  const nb = REL.neighborsOf(id);
  const parts = [];
  const down = nb.filter((n) => n.below && !n.build).map((n) => doorName(n.id));
  const built = nb.filter((n) => n.below && n.build).map((n) => doorName(n.id));
  const from = nb.filter((n) => !n.below && !n.build).map((n) => doorName(n.id));
  const into = nb.filter((n) => !n.below && n.build).map((n) => doorName(n.id));
  if (down.length) parts.push('leads down to ' + down.join(', '));
  if (built.length) parts.push('built from ' + built.join(', '));
  if (from.length) parts.push('comes from ' + from.join(', '));
  if (into.length) parts.push('builds into ' + into.join(', '));
  if (!parts.length) return 'no drawn roads: it rings alone';
  return 'one step: ' + parts.join('; ');
}

function apply() {
  canvas.classList.toggle('focusing', !!focusId);
  const hi = focusId ? REL.focusSet(focusId) : null;
  canvas.querySelectorAll('.door').forEach((d) => {
    d.classList.toggle('hi', !!(hi && hi.has(d.dataset.go)));
    d.classList.toggle('tapped', !!(hi && d.dataset.go === focusId));
  });
  canvas.querySelectorAll('.band').forEach((b) => {
    let has = false;
    if (hi && bandOf[focusId] && b.dataset.band === bandOf[focusId].id) has = true;
    b.classList.toggle('hi', has);
  });
  panel.textContent = '';
  diveEl.hidden = true;
  if (!focusId) {
    const hint = document.createElement('span');
    hint.className = 'route';
    hint.id = 'hint';
    hint.textContent = 'tap any circle to light its drawn roads — one step; the rest fades';
    panel.appendChild(hint);
    return;
  }
  const who = document.createElement('span');
  who.className = 'who';
  who.textContent = doorName(focusId);
  const stratum = document.createElement('span');
  stratum.className = 'stratum';
  stratum.textContent = bandOf[focusId] ? bandOf[focusId].label : '';
  const route = document.createElement('span');
  route.className = 'route';
  route.textContent = relationSummary(focusId);
  const diveBtn = document.createElement('button');
  diveBtn.className = 'dive-btn';
  diveBtn.id = 'dive-btn';
  diveBtn.textContent = 'dive into this view';
  diveBtn.addEventListener('click', () => {
    if (diveEl.hidden) diveEl.textContent = diveText(focusId);
    diveEl.hidden = !diveEl.hidden;
    if (!diveEl.hidden) diveBtn.textContent = 'close the dive';
    else diveBtn.textContent = 'dive into this view';
  });
  panel.appendChild(who); panel.appendChild(stratum);
  panel.appendChild(route); panel.appendChild(diveBtn);
}

canvas.addEventListener('click', (ev) => {
  const d = ev.target.closest ? ev.target.closest('.door') : null;
  const id = d ? d.dataset.go : null;
  if (id) {
    focusId = (id === focusId) ? null : id;
  } else {
    focusId = null;
  }
  apply();
});

/* ---- the width slider and the fit toggle ---------------------- */
function place() {
  const stage = document.querySelector('.stage');
  if (fit) {
    const k = Math.min(1, (stage.clientWidth - 48) / geo.width);
    holder.style.transform = 'scale(' + k + ')';
    stage.style.height = (geo.height * k + 48) + 'px';
  } else {
    holder.style.transform = 'none';
    stage.style.height = '';
  }
}
const slider = document.getElementById('w');
slider.addEventListener('input', () => {
  render(+slider.value);
  wv.textContent = slider.value + 'px';
});
document.querySelectorAll('.bar button[data-w]').forEach((b) => {
  b.addEventListener('click', () => {
    slider.value = b.dataset.w;
    render(+b.dataset.w);
    wv.textContent = slider.value + 'px';
  });
});
const fitBtn = document.getElementById('fit');
fitBtn.addEventListener('click', () => {
  fit = !fit;
  fitBtn.classList.toggle('on', fit);
  place();
});
window.addEventListener('resize', place);
render(1340);
wv.textContent = slider.value + 'px';
</script>
</body>
</html>
`;

fs.writeFileSync(path.join('engine', 'demo.html'), html);
console.log('built engine/demo.html (' + Math.round(html.length / 1024) + ' KB) — open it in a browser');
