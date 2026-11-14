/* layout.js — the map's layout engine, step 3.
   A pure function from the model and a width to the map's
   geometry: every storey's frame, every door's box, the two
   floors — and nothing else. The connecting lines are gone by
   design: they were dense, they connected at strange angles,
   and they carried little the strata themselves and a tap do
   not carry better. The map is a panorama — how a whole story
   runs under each trail is read by tapping a circle and
   watching its full route light while the rest fades, and the
   dive into the view opens from there.

   The whole drawing is symmetrical at every scale: every
   storey's frame is the same width, its label centred above
   its doors, its rows centred in the frame, so the map is a
   column of equal strata at any width. A storey too wide for
   the window wraps into balanced rows the engine itself
   chooses, the doors full size at every width.

   No DOM, no measurement, no Date, no randomness: the same
   inputs give the same output, so the whole engine is testable
   in Node, like tests/hover.js. */

var ETBLayout = (function () {
  'use strict';

  var DEF = {
    doorW: 86,      /* the door component's fixed width */
    doorH: 88,      /* the circle, the gap, a two-line name */
    doorGap: 12,
    rowGap: 16,     /* between rows inside a wrapped band */
    bandPadX: 28,
    bandPadTop: 16,
    bandPadBottom: 20,
    bandGap: 56,    /* the gap between consecutive bands */
    labelLineH: 18, /* the label's own line, centred above the doors */
    labelGap: 10,   /* between the label's line and the first row */
    colGap: 72,     /* the seam between the fork's two columns */
    minColW: 400,   /* the columns stand side by side above this */
    floorGap: 10,
    floorH: 44,
    labelCharW: 6.4  /* the default label width estimate */
  };

  function merge(cfg) {
    var c = {}, k;
    for (k in DEF) c[k] = DEF[k];
    if (cfg) for (k in cfg) c[k] = cfg[k];
    return c;
  }

  /* the label width: measured by the renderer, supplied by the
     tests, estimated from the text by default */
  function labelWidth(b, widths, C) {
    if (widths && widths.labels && widths.labels[b.id] != null)
      return widths.labels[b.id];
    return Math.ceil(b.label.length * C.labelCharW) + 10;
  }

  /* ---- rows: how a band's doors share the width ----------------
     One line when it fits; below that the engine wraps the
     storey into balanced rows, the authored order preserved
     and the break points chosen, not fallen into */

  function rowsFor(n, budget, C) {
    var per = Math.floor((budget + C.doorGap) / (C.doorW + C.doorGap));
    if (per < 1) per = 1;
    if (n <= per) return [n];
    var r = Math.ceil(n / per);
    var base = Math.floor(n / r), extra = n % r, rows = [], i;
    for (i = 0; i < r; i++) rows.push(base + (i < extra ? 1 : 0));
    return rows;
  }

  function rowWidth(n, C) {
    return n * C.doorW + (n - 1) * C.doorGap;
  }

  /* ---- one band's geometry ------------------------------------
     Every band's frame is the same width — the budget the map
     gave this column — and everything inside it is centred */

  function bandGeometry(b, budget, widths, C) {
    var n = b.views.length;
    var lw = labelWidth(b, widths, C);
    var content = budget - C.bandPadX * 2;
    var counts = n === 0 ? [0]
      : rowWidth(n, C) <= content ? [n] : rowsFor(n, content, C);
    var g = {
      id: b.id, col: b.col || null, views: b.views,
      rows: [], label: { w: lw },
      w: budget,
      h: C.bandPadTop + C.labelLineH + C.labelGap +
        counts.length * C.doorH +
        (counts.length - 1) * C.rowGap + C.bandPadBottom,
      x: 0, y: 0
    };
    var i, r, k = 0;
    for (r = 0; r < counts.length; r++) {
      var row = [];
      for (i = 0; i < counts[r]; i++) {
        row.push({ id: b.views[k++], band: b.id, row: r,
          w: C.doorW, h: C.doorH });
      }
      g.rows.push(row);
    }
    return g;
  }

  function placeBand(g, x, y, C) {
    g.x = x; g.y = y;
    /* the label centred above the doors */
    g.label.x = x + (g.w - g.label.w) / 2;
    g.label.y = y + C.bandPadTop;
    var top = y + C.bandPadTop + C.labelLineH + C.labelGap;
    var doors = {};
    g.rows.forEach(function (row, r) {
      var ry = top + r * (C.doorH + C.rowGap);
      var start = g.x + (g.w - rowWidth(row.length, C)) / 2;
      row.forEach(function (d, i) {
        d.x = start + i * (C.doorW + C.doorGap);
        d.y = ry;
        d.cx = d.x + C.doorW / 2;
        doors[d.id] = d;
      });
    });
    g.doors = doors;
    return g;
  }

  /* ---- the drawing's geometry ----------------------------------
     The storeys above the fork, then the fork: two columns
     stepping down in pairs, each pair's tops level, the
     columns' floors beneath their own last band. The engine
     stacks the columns when half the width cannot hold a
     readable column — a measured decision, not a stylesheet
     breakpoint */

  function layoutMap(model, widths, avail, cfg) {
    var C = merge(cfg);
    var mid = [], left = [], right = [];
    model.bands.forEach(function (b) {
      if (b.col === 'left') left.push(b);
      else if (b.col === 'right') right.push(b);
      else mid.push(b);
    });

    /* the natural width: the widest storey on one line — the
       width at which no band ever wraps (metadata for the
       renderer; the map itself always fills its avail) */
    var natW = 0;
    model.bands.forEach(function (b) {
      var lw = labelWidth(b, widths, C);
      natW = Math.max(natW, C.bandPadX * 2 +
        rowWidth(b.views.length, C));
    });

    var colW = Math.floor((avail - C.colGap) / 2);
    var stacked = avail < 2 * C.minColW + C.colGap;

    var geo = {
      avail: avail, natW: natW,
      fork: stacked ? 'stacked' : 'side',
      bands: [], doors: {}, floors: [],
      width: avail, height: 0,
      key: Math.floor(avail / 16) * 16 + ':' +
        (stacked ? 'stacked' : 'side')
    };

    var y = 0;

    mid.forEach(function (b) {
      var g = bandGeometry(b, avail, widths, C);
      placeBand(g, 0, y, C);
      geo.bands.push(g);
      y += g.h + C.bandGap;
    });

    if (!stacked) {
      var leftGs = left.map(function (b) {
        return bandGeometry(b, colW, widths, C);
      });
      var rightGs = right.map(function (b) {
        return bandGeometry(b, colW, widths, C);
      });
      var rightX = avail - colW;
      var nPairs = Math.max(leftGs.length, rightGs.length), p;
      for (p = 0; p < nPairs; p++) {
        var pairTop = y, pairH = 0;
        if (leftGs[p]) { placeBand(leftGs[p], 0, pairTop, C); geo.bands.push(leftGs[p]); }
        if (rightGs[p]) { placeBand(rightGs[p], rightX, pairTop, C); geo.bands.push(rightGs[p]); }
        pairH = Math.max(leftGs[p] ? leftGs[p].h : 0,
                         rightGs[p] ? rightGs[p].h : 0);
        y += pairH + C.bandGap;
      }
      if (model.floors) {
        ['left', 'right'].forEach(function (side) {
          if (!model.floors[side]) return;
          var list = side === 'left' ? leftGs : rightGs;
          if (!list.length) return;
          var last = list[list.length - 1];
          geo.floors.push({
            col: side, text: model.floors[side],
            x: side === 'left' ? 0 : rightX,
            y: last.y + last.h + C.floorGap,
            w: colW, h: C.floorH
          });
        });
      }
    } else {
      ['left', 'right'].forEach(function (side) {
        (side === 'left' ? left : right).forEach(function (b) {
          var g = bandGeometry(b, avail, widths, C);
          placeBand(g, 0, y, C);
          geo.bands.push(g);
          y += g.h + C.bandGap;
        });
        if (model.floors && model.floors[side]) {
          var gs = geo.bands.filter(function (g) { return g.col === side; });
          var last = gs[gs.length - 1];
          geo.floors.push({
            col: side, text: model.floors[side],
            x: 0, y: y - C.bandGap + C.floorGap,
            w: avail, h: C.floorH
          });
          y += C.floorH + C.bandGap;
        }
      });
    }

    geo.floors.forEach(function (f) {
      y = Math.max(y, f.y + f.h);
    });
    geo.height = y;
    geo.bands.forEach(function (g) {
      var k;
      for (k in g.doors) geo.doors[k] = g.doors[k];
    });
    return geo;
  }

  return { layoutMap: layoutMap, defaults: DEF };
})();

if (typeof module !== 'undefined' && module.exports)
  module.exports = ETBLayout;
