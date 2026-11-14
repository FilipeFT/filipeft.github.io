/* tests/hover.js — the hover contract, exercised at the level of
   logic before it is trusted on a screen.

   The map module (fund.js) is layered so this file can do its
   job: its decision layer is pure functions over the deck's own
   data, with no DOM, so the whole hover can be tested the way
   the build tests the data — by running it.

   What is checked, for every circle on the map:
     — the hovered circle is always part of what it lights;
     — nothing above the hovered circle's band ever lights
       (the rule is DOWN, and only down);
     — a bottom (nothing beneath it) does not dim the map and
       traces no tracks: it rings alone;
     — anything else dims the rest and lights ONE CONNECTED
       route: drawn lines between lit circles, plus the lit
       steps the map leaves undrawn, traced as walks, and the
       union of the two reaches every lit circle from the
       hovered one;
     — every drawn line it lights runs between two lit circles,
       and no walk duplicates a drawn line;
     — every trail, hovered, reaches at least one primer, the
       construction the whole map stands on.

   The closure is then recomputed here a second time, from the
   model alone (the strata and the roads, each with its kind), by
   an independent implementation, and the two answers must agree —
   a parity check, so the module cannot quietly drift from the
   contract it is believed to keep.

   Last, applyHighlight is run against a mock of the few DOM
   calls it makes: the classes it promises to toggle, the walk
   paths it promises to trace, and the clean slate it promises
   to leave when the mouse goes away.

   Run:  node tests/hover.js   (from the project root, after
   python3 build.py --only map). No dependencies. */
'use strict';

const fs = require('fs');
const path = require('path');

const mapPage = process.argv[2] || path.join('out', 'map.html');
const fundSrcPath = process.argv[3] || 'fund.js';

/* ---- lift the data and the module off the built page ---------- */

const page = fs.readFileSync(mapPage, 'utf8');
const m = page.match(/const DATA = (\{[\s\S]*?\});\nconst SYSTEMS/);
if (!m) { console.error('no DATA payload found in ' + mapPage); process.exit(1); }
const fundSrc = fs.readFileSync(fundSrcPath, 'utf8');
/* the module expects the same globals both builds provide; the
   DOM helpers stay undefined because the pure half never calls
   them, and this file only exercises that half plus
   applyHighlight against a mock */
const DATA = JSON.parse(m[1]);
const EDGES = DATA.edges || [];
const CHAIN = EDGES.filter((e) => e.kind === 'build');
const sandbox = new Function(
  'DATA', 'SYSTEMS', 'EXPLAINERS', 'ICONS', 'PRIMER_META', 'PLACEHOLDERS', 'MAP', 'EDGES', 'CHAIN',
  fundSrc + '\nreturn { fundDown: fundDown, fundFocus: fundFocus, ' +
    'fundHighlight: fundHighlight, fundPaths: fundPaths, ' +
    'applyHighlight: applyHighlight };');
const F = sandbox(DATA, DATA.cards, DATA.trails, DATA.icons,
  DATA.primers, DATA.placeholders, DATA.map, EDGES, CHAIN);
const fundHighlight = F.fundHighlight;
const applyHighlight = F.applyHighlight;
const SYSTEMS = DATA.cards;
const EXPLAINERS = DATA.trails;
const ICONS = DATA.icons;
const PRIMER_META = DATA.primers;
const PLACEHOLDERS = DATA.placeholders;
const MAP = DATA.map;

/* ---- the independent reimplementation -------------------------
   Same data, second opinion: written from the contract, not
   from the module, so agreement means something. */

/* the storeys, fork-aware — the same row rule the module and the
   build share: no column opens a storey, left opens the fork and
   a storey, right shares the left's storey directly after it */
function bandRows() {
  const rows = {};
  let r = -1;
  let prev = null;
  MAP.forEach((b) => {
    const col = b.col || null;
    if (col === null || col === 'left' || prev !== 'left') r += 1;
    rows[b.id] = r;
    prev = col;
  });
  return rows;
}

function independentHighlight(id) {
  const rowsB = bandRows();
  const rowOf = {};
  MAP.forEach((b) => b.views.forEach((v) => { rowOf[v] = rowsB[b.id]; }));
  const onMap = new Set();
  MAP.forEach((b) => b.views.forEach((v) => onMap.add(v)));
  // downward adjacency: the land roads of the model, plus the
  // build roads read downward
  const down = new Map();
  const push = (a, b) => {
    if (!onMap.has(a) || !onMap.has(b)) return;
    if (!down.has(a)) down.set(a, new Set());
    down.get(a).add(b);
  };
  EDGES.forEach((e) => { if (e.kind === 'land') push(e.from, e.to); });
  CHAIN.forEach((l) => push(l.to, l.from));
  // closure: landings, then the chain beneath, then the web
  const lit = new Set([id]);
  const grow = (start) => {
    const stack = [...start];
    while (stack.length) {
      const cur = stack.pop();
      (down.get(cur) || []).forEach((n) => {
        if (!lit.has(n)) { lit.add(n); stack.push(n); }
      });
    }
  };
  grow([id]);
  // web completion, strictly below the hovered band
  for (;;) {
    const before = lit.size;
    CHAIN.forEach((l) => {
      if (lit.has(l.to) && !lit.has(l.from) && rowOf[l.from] > rowOf[id]) lit.add(l.from);
      if (lit.has(l.from) && !lit.has(l.to) && rowOf[l.to] > rowOf[id]) lit.add(l.to);
    });
    grow([...lit]);
    if (lit.size === before) break;
  }
  // classification: a drawn line is a road that descends exactly
  // one storey — a road that climbs, runs level, or skips storeys
  // is a walk — plus the built-from roads, both orientations
  const bandOf = {};
  const rowOfBand = bandRows();
  MAP.forEach((b) => {
    b.views.forEach((v) => { bandOf[v] = b.id; });
  });
  const drawn = new Set();
  EDGES.forEach((e) => {
    if (e.kind === 'build') {
      drawn.add(e.from + '>' + e.to);
      drawn.add(e.to + '>' + e.from);
      return;
    }
    if (bandOf[e.from] && bandOf[e.to] &&
        rowOfBand[bandOf[e.from]] - rowOfBand[bandOf[e.to]] === 1) {
      drawn.add(e.from + '>' + e.to);
    }
  });
  const lines = [];
  const walks = [];
  down.forEach((targets, a) => {
    targets.forEach((b) => {
      if (!lit.has(a) || !lit.has(b)) return;
      if (drawn.has(a + '>' + b)) lines.push([a, b]);
      else walks.push([a, b]);
    });
  });
  return { circles: lit, lines: lines, walks: walks };
}

/* ---- the assertions -------------------------------------------- */

let failures = 0;
const fail = (msg) => { failures++; console.error('  FAIL ' + msg); };
const sameSet = (a, b) => a.size === b.size && [...a].every((x) => b.has(x));
const keySet = (pairs) => new Set(pairs.map((p) => p[0] + '>' + p[1]));

const rowsB = bandRows();
const rowOf = {};
MAP.forEach((b) => b.views.forEach((v) => { rowOf[v] = rowsB[b.id]; }));
const primers = new Set(Object.keys(PRIMER_META));

const circles = [];
MAP.forEach((b) => b.views.forEach((id) => circles.push(id)));
const trailIds = new Set(Object.keys(EXPLAINERS));

let connectedCount = 0;
let walkCount = 0;
const trace = [];

circles.forEach((id) => {
  const hi = fundHighlight(id);
  const label = id;
  if (!hi.circles.has(id)) fail(label + ': the hovered circle does not light itself');
  hi.circles.forEach((c) => {
    if (rowOf[c] < rowOf[id]) {
      fail(label + ': lights ' + c + ' above itself — the rule is down, only down');
    }
  });
  if (hi.circles.size === 1) {
    if (hi.dim) fail(label + ': a bottom must not dim the map');
    if (hi.lines.length || hi.walks.length) fail(label + ': a bottom traces no tracks');
  } else {
    if (!hi.dim) fail(label + ': ' + hi.circles.size + ' circles lit but no dim');
    if (!hi.lines.length && !hi.walks.length) {
      fail(label + ': lit circles but no tracks connect them');
    }
    // connected route: lines ∪ walks reach every lit circle
    const adj = new Map();
    const link = (a, b) => {
      if (!adj.has(a)) adj.set(a, new Set());
      if (!adj.has(b)) adj.set(b, new Set());
      adj.get(a).add(b); adj.get(b).add(a);
    };
    hi.lines.forEach((p) => link(p[0], p[1]));
    hi.walks.forEach((p) => link(p[0], p[1]));
    const seen = new Set([id]);
    const stack = [id];
    while (stack.length) {
      const cur = stack.pop();
      (adj.get(cur) || []).forEach((n) => {
        if (!seen.has(n)) { seen.add(n); stack.push(n); }
      });
    }
    if (!sameSet(seen, hi.circles)) {
      fail(label + ': the lit route is broken — ' +
        [...hi.circles].filter((c) => !seen.has(c)).join(', ') +
        (hi.circles.size > seen.size ? ' unreachable' : '') +
        (seen.size > hi.circles.size ? ' (route reaches unlit circles?)' : ''));
    } else {
      connectedCount++;
    }
    hi.lines.forEach((p) => {
      if (!hi.circles.has(p[0]) || !hi.circles.has(p[1])) {
        fail(label + ': a drawn line lights between unlit circles (' + p[0] + '>' + p[1] + ')');
      }
    });
    const lineKeys = keySet(hi.lines);
    hi.walks.forEach((p) => {
      const k = p[0] + '>' + p[1];
      if (lineKeys.has(k)) fail(label + ': a walk duplicates a drawn line (' + k + ')');
    });
    walkCount += hi.walks.length;
    if (trailIds.has(id) && ![...hi.circles].some((c) => primers.has(c))) {
      fail(label + ': hovered, never reaches a primer, the construction');
    }
  }
  // parity with the independent reimplementation
  const indep = independentHighlight(id);
  if (!sameSet(hi.circles, indep.circles)) {
    fail(label + ': closure disagrees with the independent check (' +
      hi.circles.size + ' vs ' + indep.circles.size + ' circles)');
  }
  if (!sameSet(keySet(hi.lines), keySet(indep.lines)) ||
      !sameSet(keySet(hi.walks), keySet(indep.walks))) {
    fail(label + ': track classification disagrees with the independent check');
  }
  trace.push([id, hi.circles.size, hi.dim ? 1 : 0,
    hi.lines.length, hi.walks.length]);
});

/* ---- the mock DOM: applyHighlight keeps its promises --------- */

function mockNode(name, opts) {
  opts = opts || {};
  const n = {
    tagName: name,
    classes: new Set(opts.classes || []),
    attrs: opts.attrs || {},
    children: [],
    rect: opts.rect || { left: 0, top: 0, right: 0, bottom: 0, width: 0, height: 0 },
    parent: null,
  };
  n.classList = {
    add: (c) => n.classes.add(c),
    remove: (c) => n.classes.delete(c),
    contains: (c) => n.classes.has(c),
    toggle: (c, force) => {
      const on = force === undefined ? !n.classes.has(c) : !!force;
      if (on) n.classes.add(c); else n.classes.delete(c);
      return on;
    },
  };
  n.setAttribute = (k, v) => { n.attrs[k] = String(v); };
  n.getAttribute = (k) => (k in n.attrs ? n.attrs[k] : null);
  n.appendChild = (c) => { c.parent = n; n.children.push(c); return c; };
  n.removeChild = (c) => { n.children.splice(n.children.indexOf(c), 1); };
  Object.defineProperty(n, 'firstChild', { get: () => n.children[0] || null });
  n.getBoundingClientRect = () => n.rect;
  n.querySelector = (sel) => {
    for (const c of n.children) {
      if (mockMatches(c, sel)) return c;
      const deep = c.querySelector(sel);
      if (deep) return deep;
    }
    return null;
  };
  n.querySelectorAll = (sel) => {
    const out = [];
    const walk = (x) => {
      x.children.forEach((c) => {
        if (mockMatches(c, sel)) out.push(c);
        walk(c);
      });
    };
    walk(n);
    return out;
  };
  return n;
}
function mockMatches(node, sel) {
  const m1 = sel.match(/^\[data-go="(.+)"\]$/);
  if (m1) return node.attrs['data-go'] === m1[1];
  const m2 = sel.match(/^\.door\[data-go\]$/);
  if (m2) return node.classes.has('door') && 'data-go' in node.attrs;
  const m3 = sel.match(/^\.d-ic$/);
  if (m3) return node.classes.has('d-ic');
  const m4 = sel.match(/^path\[data-a\]$/);
  if (m4) return node.tagName === 'path' && 'data-a' in node.attrs;
  return false;
}

globalThis.document = {
  createElementNS: (ns, tag) => mockNode(tag),
};

function buildMockDag(hi) {
  const holder = mockNode('div', {
    classes: ['dag'],
    attrs: { id: 'fund-dag' },
    rect: { left: 0, top: 0, right: 900, bottom: 700, width: 900, height: 700 },
  });
  let x = 10;
  circles.forEach((id) => {
    const door = mockNode('button', {
      classes: ['door'],
      attrs: { 'data-go': id },
      rect: { left: x, top: 100, right: x + 86, bottom: 160, width: 86, height: 60 },
    });
    const icn = mockNode('span', {
      classes: ['d-ic'],
      rect: { left: x + 20, top: 100, right: x + 66, bottom: 146, width: 46, height: 46 },
    });
    door.appendChild(icn);
    holder.appendChild(door);
    x += 96;
  });
  const svg = mockNode('svg');
  const svgTop = mockNode('svg');
  // two drawn lines: one the hover below will light, one it will
  // not; a walk path is checked for its own geometry
  const litPair = hi.lines[0] || hi.walks[0] || ['cpu', 'adders'];
  const unlit = circles.filter((c) => !hi.circles.has(c)).slice(0, 2);
  const litLine = mockNode('path', { attrs: { 'data-a': litPair[0], 'data-b': litPair[1] } });
  const darkLine = mockNode('path', {
    attrs: { 'data-a': unlit[0] || 'cpu', 'data-b': unlit[1] || 'games' },
  });
  svg.appendChild(litLine); svg.appendChild(darkLine);
  return { holder: holder, svg: svg, svgTop: svgTop };
}

{
  const hi = fundHighlight('x-measure');
  const { holder, svg, svgTop } = buildMockDag(hi);
  if (hi.walks.length === 0) fail('mock: expected x-measure to trace walks');
  applyHighlight(holder, svg, svgTop, hi);
  if (!holder.classes.has('dag-focusing')) fail('mock: dag-focusing not set');
  const litDoors = holder.querySelectorAll('.door[data-go]')
    .filter((d) => d.classes.has('dag-hi'))
    .map((d) => d.attrs['data-go']);
  const hiDoors = [...hi.circles];
  if (litDoors.length !== hiDoors.length ||
      !hiDoors.every((c) => litDoors.includes(c))) {
    fail('mock: dag-hi does not match the lit circles');
  }
  if (svgTop.children.length !== hi.walks.length) {
    fail('mock: expected ' + hi.walks.length + ' traced walks, got ' + svgTop.children.length);
  }
  svgTop.children.forEach((p) => {
    if (p.tagName !== 'path' || p.attrs['class'] !== 'dag-walk') {
      fail('mock: a traced track is not a dag-walk path');
    }
    if (!/^M/.test(p.attrs['d'] || '')) fail('mock: a walk path carries no geometry');
  });
  const litLine = svg.children[0];
  const darkLine = svg.children[1];
  if (!litLine.classes.has('dag-hi')) fail('mock: a drawn line between lit circles stays dark');
  if (darkLine.classes.has('dag-hi')) fail('mock: a line to an unlit circle lights');
  // clean slate
  applyHighlight(holder, svg, svgTop, null);
  if (holder.classes.has('dag-focusing')) fail('mock: dag-focusing not cleared');
  if (holder.querySelectorAll('.door[data-go]').some((d) => d.classes.has('dag-hi'))) {
    fail('mock: dag-hi not cleared');
  }
  if (svgTop.children.length !== 0) fail('mock: traced walks not cleared');
  if (litLine.classes.has('dag-hi')) fail('mock: lit line not released');
}

/* ---- the trace ------------------------------------------------- */

console.log('hover contract, exercised on the built deck (' + circles.length + ' circles)');
console.log('  id            size dim lines walks');
trace.forEach((t) => {
  console.log('  ' + t[0].padEnd(13) + String(t[1]).padStart(4) +
    '   ' + t[2] + '    ' + String(t[3]).padStart(5) + String(t[4]).padStart(6));
});
console.log('  ' + connectedCount + ' connected routes · ' + walkCount +
  ' walks traced in total (summed over all hovers)');
if (failures) {
  console.error(failures + ' failure(s)');
  process.exit(1);
}
console.log('hover: all ' + circles.length + ' circles honour the contract');
