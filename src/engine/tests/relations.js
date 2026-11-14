/* relations.js — verifies the one relationship set: the engine's
   lines must be exactly the deck's drawn set (fund.js's
   fundEdges), and the tap highlight built on them lights one step
   and never a long distance. Run from the repo root:
   node engine/tests/relations.js */
'use strict';
const fs = require('fs');
const path = require('path');

let fails = 0, checks = 0;
function ok(c, msg) {
  checks++;
  if (!c) { fails++; console.error('FAIL: ' + msg); }
}

const page = fs.readFileSync(path.join('out', 'map.html'), 'utf8');
const DATA = JSON.parse(page.match(/const DATA = (\{[\s\S]*?\});\nconst SYSTEMS/)[1]);
const EDGES = DATA.edges || [];
const CHAIN = EDGES.filter((e) => e.kind === 'build');

const ETBRelations = require(path.join(__dirname, '..', 'relations.js'));
const R = ETBRelations.makeRelations(DATA.map, EDGES);

/* the deck's own drawn set, lifted out of fund.js the same way
   tests/hover.js lifts it */
const fundSrc = fs.readFileSync('fund.js', 'utf8');
const sandbox = new Function('DATA', 'SYSTEMS', 'EXPLAINERS', 'ICONS',
  'PRIMER_META', 'PLACEHOLDERS', 'MAP', 'EDGES', 'CHAIN',
  fundSrc + '\nreturn { fundEdges: fundEdges, fundFocus: fundFocus };');
const F = sandbox(DATA, DATA.cards, DATA.trails, DATA.icons,
  DATA.primers, DATA.placeholders, DATA.map, EDGES, CHAIN);
const deckLines = F.fundEdges();

/* ---- the pin: one set of relationships, the deck's own ------ */
const norm = (ls) => JSON.stringify(ls.map((l) => [l[0], l[1], l[2] === true]));
ok(norm(R.lines) === norm(deckLines),
  'the engine\'s line set is exactly the deck\'s drawn set, got ' +
  R.lines.length + ' vs ' + deckLines.length);
ok(R.lines.filter((l) => !l[2]).length === 39,
  '39 one-storey roads are drawn, got ' + R.lines.filter((l) => !l[2]).length);
ok(R.lines.filter((l) => l[2]).length === 8,
  '8 built-from links are drawn, got ' + R.lines.filter((l) => l[2]).length);

/* every line spans exactly one storey: no climbs, no level runs,
   no skips — the long-distance relations are left behind */
R.lines.forEach((l) => {
  ok(R.rows[R.bandOf[l[0]]] - R.rows[R.bandOf[l[1]]] === 1,
    'the line ' + l[0] + '>' + l[1] + ' spans exactly one storey');
});

/* ---- the tap: one step, symmetric, never a long distance ----- */
let lit = 0, maxDeg = 0, sum = 0, dropped = 0, gained = 0;
DATA.map.forEach((b) => b.views.forEach((id) => {
  const s = R.focusSet(id);
  ok(s.has(id), id + ' lights itself');
  ok(s.size === R.degree(id) + 1,
    id + ' lights exactly its neighbours, got ' + s.size +
    ' for degree ' + R.degree(id));
  sum += s.size;
  if (s.size > 1) lit++;
  if (R.degree(id) > maxDeg) maxDeg = R.degree(id);

  /* symmetry: a neighbour's set answers back */
  R.neighborsOf(id).forEach((n) => {
    ok(R.focusSet(n.id).has(id),
      id + ' and ' + n.id + ' light each other');
    /* the mandate itself: nothing more than one storey away */
    const diff = R.rows[R.bandOf[n.id]] - R.rows[R.bandOf[id]];
    ok(Math.abs(diff) === 1,
      id + ' lights ' + n.id + ' one storey away, got ' + diff);
    ok((diff > 0) === n.below,
      id + '\u2019s neighbour ' + n.id + ' reports its direction honestly');
  });

  /* the old closure walked land roads down, transitively — the
     long-distance relations. The one-step roads are a different,
     deliberate set: cross roads the old hover never followed,
     now lit because the lines drew them, and nothing beyond one
     storey, ever */
  const old = F.fundFocus(id);
  if (old.size > s.size) dropped++;
  if (s.size > old.size) gained++;
}));

ok(dropped > 0,
  'the transitive and long-distance relations are really gone ' +
  '(dropped for ' + dropped + ' doors)');
ok(maxDeg <= 8, 'no door has more than 8 drawn roads, got ' + maxDeg);

/* determinism: the same model gives the same set */
const R2 = ETBRelations.makeRelations(DATA.map, EDGES);
ok(JSON.stringify(R.lines) === JSON.stringify(R2.lines),
  'the relationship set is deterministic');
DATA.map.forEach((b) => b.views.forEach((id) => {
  const a = Array.from(R.focusSet(id)).join(',');
  const c = Array.from(R2.focusSet(id)).join(',');
  if (a !== c) ok(false, id + '\u2019s focus set is deterministic');
}));

console.log('relations: the one set is pinned to the deck\'s 47 drawn lines ' +
  '(' + R.lines.filter((l) => !l[2]).length + ' cross roads, ' +
  R.lines.filter((l) => l[2]).length + ' built-from)');
console.log('  ' + lit + ' doors have a road to light (max degree ' +
  maxDeg + ', average set ' + (sum / 51).toFixed(1) + ')');
console.log('  the old closure lighted more on ' + dropped +
  ' doors — left behind; the one-step set exceeds it on ' + gained +
  ' doors (cross roads the old hover never followed)');
console.log(fails === 0
  ? 'relations: all invariants pass (' + checks + ' checks)'
  : 'relations: ' + fails + ' FAILURES');
process.exit(fails === 0 ? 0 : 1);
