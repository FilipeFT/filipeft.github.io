/* relations.js — the map's one set of relationships, step 3
   refined. The deck drew lines for exactly one kind of relation:
   a road that descends exactly one storey, or a built-from link.
   Its hover, separately, followed every land road transitively —
   including roads that skip storeys, which lit distant circles
   straight down to the machine groupings and said little. With
   the lines gone, that closure is all the highlight would have
   had, and it is not informative: the panorama's tap lights the
   drawn-road neighbours only — one step, up or down, the same
   set of relationships the lines carried — and the long-distance
   relations are left behind.

   This module is the pure definition of that set. It must stay
   pinned to fund.js's fundEdges (the deck's own drawn set):
   engine/tests/relations.js fails if the two ever drift.

   No DOM, no measurement, no Date, no randomness. */

var ETBRelations = (function () {
  'use strict';

  /* the storey rows, by the deck's own rule: the mid bands one
     per row, the fork's two columns stepping down in pairs */
  function bandRows(bands) {
    var rows = {}, r = -1, prev = null;
    bands.forEach(function (b) {
      var col = b.col || null;
      if (col === null || col === 'left' || prev !== 'left') r += 1;
      rows[b.id] = r;
      prev = col;
    });
    return rows;
  }

  function makeRelations(bands, edges) {
    var rows = bandRows(bands);
    var onMap = {}, bandOf = {}, ord = {}, oi = 0;
    bands.forEach(function (b) {
      b.views.forEach(function (v) {
        onMap[v] = 1; bandOf[v] = b.id; ord[v] = oi++;
      });
    });

    /* the drawn set, in the deck's own order: the one-storey
       descending roads first (authored order), then the
       built-from links (authored order) */
    var lines = [];
    edges.forEach(function (e) {
      if (e.kind === 'build') return;
      if (onMap[e.from] && onMap[e.to] &&
          rows[bandOf[e.from]] - rows[bandOf[e.to]] === 1)
        lines.push([e.from, e.to, false]);
    });
    edges.forEach(function (e) {
      if (e.kind !== 'build') return;
      if (onMap[e.from] && onMap[e.to])
        lines.push([e.from, e.to, true]);
    });

    /* the same relationship, read from either end: the tap lights
       neighbours, not routes */
    var adj = {};
    function link(a, b, build) {
      (adj[a] = adj[a] || []).push({ id: b, build: build });
      (adj[b] = adj[b] || []).push({ id: a, build: build });
    }
    lines.forEach(function (l) { link(l[0], l[1], l[2]); });
    Object.keys(adj).forEach(function (k) {
      adj[k].sort(function (x, y) { return ord[x.id] - ord[y.id]; });
    });

    function neighborsOf(id) {
      return (adj[id] || []).map(function (n) {
        return { id: n.id, build: n.build,
          below: rows[bandOf[n.id]] > rows[bandOf[id]] };
      });
    }

    function focusSet(id) {
      var s = new Set([id]);
      (adj[id] || []).forEach(function (n) { s.add(n.id); });
      return s;
    }

    return {
      lines: lines,
      rows: rows,
      bandOf: bandOf,
      neighborsOf: neighborsOf,
      focusSet: focusSet,
      degree: function (id) { return (adj[id] || []).length; }
    };
  }

  return { makeRelations: makeRelations, bandRows: bandRows };
})();

if (typeof module !== 'undefined' && module.exports)
  module.exports = ETBRelations;
