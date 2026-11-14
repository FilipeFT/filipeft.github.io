/* engine tests — the layout engine's contract, checked at a
   sweep of widths from phone to desktop. Dependency-free, like
   tests/hover.js: the engine is pure, so Node can check every
   invariant without a browser.

   The drawing is symmetrical at every scale: every frame the
   same width as its column, every row and label centred in
   its frame, and no connecting lines anywhere — the panorama's
   invariants, not the old drawing's.

   usage: node engine/tests/engine.js [map page] [layout.js] */

'use strict';

const fs = require('fs');
const path = require('path');

const HERE = path.dirname(__filename);
const mapPage = process.argv[2] || path.join(HERE, '..', '..', 'out', 'map.html');
const enginePath = process.argv[3] || path.join(HERE, '..', 'layout.js');

/* ---- lift the model off the built page ------------------------- */

const page = fs.readFileSync(mapPage, 'utf8');
const m = page.match(/const DATA = (\{[\s\S]*?\});\nconst SYSTEMS/);
if (!m) { console.error('no DATA payload found in ' + mapPage); process.exit(1); }
const DATA = JSON.parse(m[1]);
const ETBLayout = require(path.resolve(enginePath));

const bandOf = {};
DATA.map.forEach((b) => b.views.forEach((v) => { bandOf[v] = b; }));

const model = { bands: DATA.map, floors: {
  left: 'the floor beneath is mathematics itself — the machine as thought, all the way down',
  right: 'the floor beneath is physics itself — a voltage high or low, all the way down'
}};

/* the label widths, synthesized deterministically (the renderer
   measures them for real; only their relative sizes matter
   here) */
const widths = { labels: {} };
DATA.map.forEach((b) => {
  widths.labels[b.id] = Math.ceil(b.label.length * 6.4) + 10;
});

/* ---- the checks ------------------------------------------------ */

let pass = 0, fails = 0;
function ok(cond, msg) {
  if (cond) { pass++; return; }
  fails++;
  console.error('FAIL: ' + msg);
}

const SWEEP = [1920, 1600, 1440, 1340, 1200, 1024, 900, 800, 768,
  700, 640, 540, 480, 414, 390, 360, 320];

function overlaps(d1, d2) {
  return d1.x < d2.x + d2.w - 0.5 && d2.x < d1.x + d1.w - 0.5 &&
    d1.y < d2.y + d2.h - 0.5 && d2.y < d1.y + d1.h - 0.5;
}

function rowWidth(n, C) {
  return n * C.doorW + (n - 1) * C.doorGap;
}

const census = [];
const C = ETBLayout.defaults;

SWEEP.forEach((avail) => {
  const geo = ETBLayout.layoutMap(model, widths, avail);
  census.push({
    avail, fork: geo.fork,
    h: Math.round(geo.height),
    rows: Math.max.apply(null, geo.bands.map((g) => g.rows.length))
  });

  /* every view is one door, placed once, at full size — the
     doors never shrink at any width */
  const ids = Object.keys(geo.doors);
  ok(ids.length === 51, avail + ': 51 doors placed, got ' + ids.length);
  ids.forEach((id) => {
    const d = geo.doors[id];
    ok(d.w === C.doorW && d.h === C.doorH,
      avail + ': door ' + id + ' is full size (' + d.w + 'x' + d.h + ')');
  });

  /* the symmetry: every frame is as wide as its column — all
     the storeys equal boxes — and nothing exceeds the canvas */
  const side = geo.fork === 'side';
  const colW = Math.floor((avail - C.colGap) / 2);
  geo.bands.forEach((g) => {
    const expect = g.col ? (side ? colW : avail) : avail;
    ok(Math.abs(g.w - expect) < 1.01,
      avail + ': band ' + g.id + ' frame is ' + g.w +
      ', expected ' + expect);
    ok(g.x + g.w <= avail + 0.5,
      avail + ': band ' + g.id + ' frame fits the canvas');
  });

  /* every row and label centred in its frame */
  geo.bands.forEach((g) => {
    const off = Math.abs(g.label.x + g.label.w / 2 - (g.x + g.w / 2));
    ok(off < 0.6, avail + ': band ' + g.id + ' label is centred');
    g.rows.forEach((row) => {
      const w = rowWidth(row.length, C);
      const left = row[0] ? row[0].x : g.x;
      const offRow = Math.abs(
        left + w / 2 - (g.x + g.w / 2));
      ok(row.length === 0 || offRow < 0.6,
        avail + ': band ' + g.id + ' row ' + row.length + ' is centred');
    });
  });

  /* every door sits inside its own band's frame */
  geo.bands.forEach((g) => {
    g.rows.forEach((row) => {
      row.forEach((d) => {
        ok(d.x >= g.x - 0.5 && d.x + d.w <= g.x + g.w + 0.5,
          avail + ': door ' + d.id + ' horizontally inside band ' + g.id);
        ok(d.y >= g.y - 0.5 && d.y + d.h <= g.y + g.h + 0.5,
          avail + ': door ' + d.id + ' vertically inside band ' + g.id);
      });
    });
  });

  /* no two doors overlap, anywhere in the drawing */
  for (let i = 0; i < ids.length; i++) {
    for (let j = i + 1; j < ids.length; j++) {
      ok(!overlaps(geo.doors[ids[i]], geo.doors[ids[j]]),
        avail + ': doors ' + ids[i] + ' and ' + ids[j] + ' overlap');
    }
  }

  /* the authored order survives every tier: reading a band's
     rows top to bottom, left to right, is reading its authored
     line */
  geo.bands.forEach((g) => {
    const flat = [];
    g.rows.forEach((row) => row.forEach((d) => flat.push(d.id)));
    const authored = model.bands
      .filter((b) => b.id === g.id)[0].views;
    ok(flat.length === authored.length &&
      flat.every((v, k) => v === authored[k]),
      avail + ': band ' + g.id + ' keeps its authored order');
  });

  /* the fork: side by side while half the width holds a
     readable column, stacked below — the engine decides, not a
     stylesheet */
  ok(geo.fork === (avail >= 2 * C.minColW + C.colGap ? 'side' : 'stacked'),
    avail + ': fork mode is ' + geo.fork);

  /* the floors follow their own column, beneath its last band */
  ok(geo.floors.length === 2, avail + ': two floors, got ' + geo.floors.length);
  geo.floors.forEach((f) => {
    const colBands = geo.bands.filter((g) => g.col === f.col);
    const last = colBands[colBands.length - 1];
    ok(f.y >= last.y + last.h - 0.5,
      avail + ': floor of ' + f.col + ' sits beneath its column');
  });

  /* there are no connecting lines: the geometry carries bands,
     doors, and floors, nothing else */
  ok(!geo.edges && !geo.crossings,
    avail + ': the geometry draws no lines');

  /* determinism: the same inputs, the same drawing */
  const again = ETBLayout.layoutMap(model, widths, avail);
  ok(JSON.stringify(again) === JSON.stringify(geo),
    avail + ': the engine is deterministic');
});

/* the panorama itself: nothing wraps until the widest storey's
   line no longer fits, and the doors stay full size everywhere */
const wide = ETBLayout.layoutMap(model, widths, 1920);
ok(wide.bands.every((g) => g.rows.length === 1),
  '1920 keeps every storey on one line');
const atNat = ETBLayout.layoutMap(model, widths, wide.natW);
ok(atNat.bands.every((g) => g.rows.length === 1),
  'at the natural width every storey still fits one line');
/* the natural width is derived, not decorated: the widest
   storey's line plus its frame, nothing more */
const widest = Math.max.apply(null, model.bands.map((b) =>
  b.views.length * C.doorW + (b.views.length - 1) * C.doorGap +
  2 * C.bandPadX));
ok(wide.natW === widest,
  'the natural width is the widest storey (' + widest + '), got ' +
  wide.natW);
ok(atNat.bands.every((g) => g.rows.length === 1),
  'at the natural width every storey still fits one line');
const phone = ETBLayout.layoutMap(model, widths, 390);
ok(phone.fork === 'stacked', 'the phone stacks the fork');
ok(Object.keys(phone.doors).length === 51,
  'the phone drawing keeps all 51 doors');

/* ---- the census ------------------------------------------------ */

console.log('engine: layout invariants hold at ' + SWEEP.length + ' widths');
console.log('  natural width (no storey wraps): ' + wide.natW);
console.log('  avail   fork      height  max rows');
census.forEach((c) => {
  console.log('  ' + String(c.avail).padStart(5) + '  ' +
    c.fork.padEnd(7) + '  ' + String(c.h).padStart(6) + '  ' + c.rows);
});
if (fails === 0) {
  console.log('engine: all invariants pass (' + pass + ' checks)');
} else {
  console.error('engine: ' + fails + ' failures');
  process.exit(1);
}
