/* ================================================================
   fund.js — the fundamentals map module: the territory beneath
   the stories, drawn as labelled bands of circles with one line
   per door that crosses a band, and the built-from chain drawn
   upward through the gaps between the construction storeys.

   One source, two builds: the deck build inlines this file into
   template.html at its marker, so the reader still receives one
   self-contained page; the isolated map build (build.py --only
   map) loads the same file whole, with the same shared helpers
   and the same data, so the map and its hover are tested alone.

   The module is layered, so the hover can be exercised at the
   level of logic before it is trusted on a screen:

     the decision — pure functions, no DOM: what a hover of a
       circle lights (which circles, which drawn lines), and
       which of its steps the static map does not draw, so they
       must be traced live instead: the long walks. fundHighlight
       returns the whole decision as data, and tests/hover.js
       exercises every circle's decision against the built deck
       before the wiring below is believed.

     the application — applyHighlight: one decision in, class
       toggles and traced walks out. No policy of its own.

     the wiring — renderFundDAG: builds the bands, draws the
       static lines, and lets the mouse ask the decision layer
       what to show.

   The hover contract, one rule for every circle: hovering lights
   the full path DOWN from it — the trail's landings (the doors
   at its bottom, not the crossings inside its steps), and,
   beneath them, the built-from chain read downward, from the
   built thing to the ingredient it is made of. Once any part of
   that construction is reached, the whole web it belongs to
   lights with it, and no circle above the hovered one is ever
   added. The lit route is one connected path: the drawn lines
   between lit circles light up, and every lit step the map
   leaves undrawn — a walk inside a band, or a landing that skips
   storeys — is traced live, dashed, only while hovered, so the
   static map keeps its rule (walked, not drawn) and the hover
   still shows the whole way down as tracks. A circle with
   nothing beneath it — a promise, or the bedrock itself — rings
   alone, without dimming the map. The build checks the contract
   from the data side: every trail, hovered, must reach at least
   one primer, and every circle's route must be connected.

   The model (data/model.xml) is the source of truth: its strata
   are the layers drawn here, and its edges are the roads the
   territory has — land (a landing, lit on hover), cross (a
   crossing, drawn only when it descends exactly one storey),
   build (built-from, drawn upward on purpose). The trails walk
   the roads; this module draws the strata and the roads that
   descend, and walks the rest live.

   Globals used, provided by both builds: $, el, ic, doorMeta
   (the shared helpers), MAP, EDGES, CHAIN (the build derives it
   from EDGES), EXPLAINERS, PLACEHOLDERS. */
/* ================================================================*/

/* ---- the decision ------------------------------------------------
   Everything below computes; nothing touches the page. */

/* the roads of the model, deduplicated by construction: the
   territory has each road once. Landings and crossings both —
   the caller filters; the module draws. */
function dagEdges() {
  return EDGES.filter((e) => e.kind !== 'build')
    .map((e) => [e.from, e.to]);
}

/* the storeys, fork-aware: a band with no column runs the full
   width of the map and opens a new storey; the left band opens
   the fork and its own storey; a right band shares the left
   band's storey when it follows it directly, and opens its own
   below. Across the fork seam two bands share one row: nothing
   lights upward across the seam, and nothing on the left is
   ever below anything on the right */
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

/* the lines the map actually draws: the roads that descend
   exactly one storey, and only down — a road that climbs, runs
   level, or skips storeys is walked in the views, never drawn,
   so no line on the map ever rises — plus the built-from roads,
   whose arrows point upward from ingredient to built thing on
   purpose: they are the construction, not a walk */
function fundEdges() {
  const bandOf = {};
  const rowOf = bandRows();
  MAP.forEach((b) => {
    b.views.forEach((v) => { bandOf[v] = b.id; });
  });
  const edges = dagEdges().filter((e) =>
    bandOf[e[0]] && bandOf[e[1]] &&
    rowOf[bandOf[e[0]]] - rowOf[bandOf[e[1]]] === 1);
  CHAIN.forEach((l) => edges.push([l.from, l.to, true]));
  return edges;
}

/* the hover's downward adjacency, over circles the map actually
   draws: the land roads of the model (where a trail bottoms
   out), and the build roads read downward (their arrows point
   up, from ingredient to built thing; the hover walks them the
   other way). Cross roads are walked in the views, never lit */
function fundDown() {
  const onMap = {};
  MAP.forEach((b) => b.views.forEach((v) => { onMap[v] = 1; }));
  const down = {};
  const add = (a, b) => {
    if (onMap[a] && onMap[b]) (down[a] = down[a] || []).push(b);
  };
  EDGES.forEach((e) => { if (e.kind === 'land') add(e.from, e.to); });
  CHAIN.forEach((l) => add(l.to, l.from));
  return down;
}

/* the full path down from one circle: itself, its landings, and
   the construction beneath them — followed transitively, and
   then completed: once any part of the built-from web is lit,
   the rest of it lights too. The completion may only add
   circles strictly below the hovered circle's band, so nothing
   ever lights upward, and a bottom (nothing beneath it) still
   rings alone */
function fundFocus(id) {
  const rows = bandRows();
  const rowOf = {};
  MAP.forEach((b) => b.views.forEach((v) => { rowOf[v] = rows[b.id]; }));
  const down = fundDown();
  const act = new Set([id]);
  const stack = [id];
  const walk = () => {
    while (stack.length) {
      (down[stack.pop()] || []).forEach((n) => {
        if (!act.has(n)) { act.add(n); stack.push(n); }
      });
    }
  };
  walk();
  let grew = true;
  while (grew) {
    grew = false;
    CHAIN.forEach((l) => {
      [[l.to, l.from], [l.from, l.to]].forEach((p) => {
        if (act.has(p[0]) && !act.has(p[1]) &&
            rowOf[p[1]] > rowOf[id]) {
          act.add(p[1]);
          stack.push(p[1]);
          grew = true;
        }
      });
    });
    walk();
  }
  return act;
}

/* the whole hover decision for one circle, as data: which
   circles light, whether the map dims, which drawn lines light
   (both ends lit), and which lit steps are walks the map does
   not draw — they will be traced live instead. Together the
   lines and the walks are one connected route from the hovered
   circle down */
function fundHighlight(id) {
  if (!id) {
    return { dim: false, circles: new Set(), lines: [], walks: [] };
  }
  const circles = fundFocus(id);
  const drawn = {};
  fundEdges().forEach((e) => { drawn[e[0] + '>' + e[1]] = 1; });
  const seen = {};
  const lines = [];
  const walks = [];
  Object.keys(fundDown()).forEach((a) => {
    fundDown()[a].forEach((b) => {
      const key = a + '>' + b;
      if (circles.has(a) && circles.has(b) && !seen[key]) {
        seen[key] = 1;
        if (drawn[key] || drawn[b + '>' + a]) {
          lines.push([a, b]);
        } else {
          walks.push([a, b]);
        }
      }
    });
  });
  return {
    dim: circles.size > 1,
    circles: circles,
    lines: lines,
    walks: walks,
  };
}

/* the report: one row per circle on the map, in reading order —
   what a hover of that circle lights, top to bottom, or an
   honest bottom */
function fundPaths() {
  const ord = {};
  MAP.forEach((b, i) => b.views.forEach((v, vi) => { ord[v] = i * 1000 + vi; }));
  const rows = [];
  MAP.forEach((b) => b.views.forEach((id) => {
    const hi = fundHighlight(id);
    rows.push({
      id: id,
      band: b.label,
      size: hi.circles.size,
      bottom: hi.circles.size === 1,
      tracks: hi.lines.length + hi.walks.length,
      lands: Array.from(hi.circles).filter((v) => v !== id)
        .sort((a, b) => ord[a] - ord[b]),
    });
  }));
  return rows;
}

/* ---- the application ---------------------------------------------
   One decision in, pixels out. No policy lives here. */

/* make a decision visible: dim the rest, light the circles and
   the drawn lines, and trace the lit walks the map leaves
   undrawn — dashed, in the accent colour, only while hovered */
function applyHighlight(holder, svg, svgTop, hi) {
  holder.classList.toggle('dag-focusing', !!(hi && hi.dim));
  holder.querySelectorAll('.door[data-go]').forEach((n) => {
    n.classList.toggle('dag-hi',
      !!(hi && hi.circles.has(n.getAttribute('data-go'))));
  });
  svg.querySelectorAll('path[data-a]').forEach((p) => {
    const on = !!hi &&
      hi.circles.has(p.getAttribute('data-a')) &&
      hi.circles.has(p.getAttribute('data-b'));
    p.classList.toggle('dag-hi', on);
  });
  while (svgTop.firstChild) svgTop.removeChild(svgTop.firstChild);
  if (!hi) return;
  const box = holder.getBoundingClientRect();
  hi.walks.forEach((w) => {
    const a = holder.querySelector('[data-go="' + w[0] + '"]');
    const b = holder.querySelector('[data-go="' + w[1] + '"]');
    if (!a || !b) return;
    const ra = (a.querySelector('.d-ic') || a).getBoundingClientRect();
    const rb = (b.querySelector('.d-ic') || b).getBoundingClientRect();
    // the trace anchors on the facing rims, so it never crosses
    // an icon: down from the bottom of the upper circle into the
    // top of the lower one, or up from the top into the bottom
    // when the walk rises, level with itself when it runs level
    const x1 = ra.left + ra.width / 2 - box.left;
    const x2 = rb.left + rb.width / 2 - box.left;
    let y1 = ra.bottom - box.top;
    let y2 = rb.top - box.top;
    if (rb.bottom <= ra.top) { y1 = ra.top - box.top; y2 = rb.bottom - box.top; }
    const mx = (x1 + x2) / 2;
    const d = 'M' + x1 + ' ' + y1 +
      ' C' + mx + ' ' + (y1 + 44) + ', ' + mx + ' ' + (y2 - 44) + ', ' + x2 + ' ' + y2;
    const p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    p.setAttribute('d', d);
    p.setAttribute('class', 'dag-walk');
    p.setAttribute('marker-end', 'url(#dag-walk-arrow)');
    svgTop.appendChild(p);
  });
}

/* ---- the wiring ---------------------------------------------------
   The page: build the bands, draw the static lines, and let the
   mouse ask the decision layer what to show. */

/* a built-from arrow leaves the ingredient by the top of its
   circle, climbs through the empty gap, slips through the clear
   channel beside the built thing's name, and hooks into the rim
   of the circle itself */
function buildD(a, b, box) {
  const ga = (a.querySelector('.d-ic') || a).getBoundingClientRect();
  const gb = (b.querySelector('.d-ic') || b).getBoundingClientRect();
  const cx1 = ga.left + ga.width / 2 - box.left;
  const y1 = ga.top - 1 - box.top;
  const cxb = gb.left + gb.width / 2 - box.left;
  const cyb = gb.top + gb.height / 2 - box.top;
  const s = cx1 - cxb > 24 ? 1 : -1;
  const r = ga.width / 2;
  const tipX = cxb + s * r * 0.72;
  const tipY = cyb + r * 0.72;
  const nmEl = b.querySelector('.d-name');
  let chX = null;
  if (nmEl) {
    const nm = nmEl.getBoundingClientRect();
    chX = (s > 0 ? nm.right + 8 : nm.left - 8) - box.left;
    const sib = s > 0 ? b.nextElementSibling : b.previousElementSibling;
    if (sib && sib.classList.contains('door')) {
      const sn = sib.querySelector('.d-name');
      if (sn) {
        const sr = sn.getBoundingClientRect();
        chX = s > 0
          ? Math.min(chX, sr.left - 8 - box.left)
          : Math.max(chX, sr.right + 8 - box.left);
      }
    }
    if ((s > 0 && chX < nm.right + 3 - box.left) ||
        (s < 0 && chX > nm.left - 3 - box.left)) chX = null;
  }
  if (chX === null) {
    // no room beside the name: rise straight and touch the rim
    const ty = gb.bottom + 1 - box.top;
    return 'M' + cx1 + ' ' + y1 + ' C' + cx1 + ' ' + ty + ', ' +
      cxb + ' ' + (ty + 14) + ', ' + cxb + ' ' + ty;
  }
  const gy = ((a.closest('.dag-band') || a).getBoundingClientRect().top +
    (b.closest('.dag-band') || b).getBoundingClientRect().bottom) / 2 - box.top;
  return 'M' + cx1 + ' ' + y1 +
    ' C' + cx1 + ' ' + gy + ', ' + chX + ' ' + gy + ', ' + chX + ' ' + (gb.bottom + 4 - box.top) +
    ' C' + chX + ' ' + (tipY + 6) + ', ' + (tipX + s * 9) + ' ' + (tipY + 5) + ', ' + tipX + ' ' + tipY;
}

/* draw the map: bands of circles, the door lines that cross one
   band, the built-from chain — and the hover wired on top */
function renderFundDAG() {
  const holder = $('#fund-dag');
  if (!holder) return;
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('class', 'dag-svg');
  holder.appendChild(svg);
  // the traced walks ride above the circles, so a long walk
  // stays readable where it passes over dimmed bands
  const svgTop = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svgTop.setAttribute('class', 'dag-svg-top');
  holder.appendChild(svgTop);
  // the fork: once a band takes a side, the storeys split in two
  // columns drawn side by side — the abstract computers on the
  // left, the machine as built on the right — and the left side
  // ends in its own floor: mathematics itself, nothing drawn
  let fork = null;
  let forkLeft = null;
  let forkRight = null;
  MAP.forEach((b) => {
    const r = el('div', 'dag-row dag-band');
    r.insertAdjacentHTML('beforeend',
      '<span class="dag-band-label">' + b.label + '</span>');
    b.views.forEach((id) => {
      const ph = PLACEHOLDERS[id];
      if (ph) {
        r.insertAdjacentHTML('beforeend',
          '<span class="door soon" data-go="' + id + '" title="' + ph.line.replace(/"/g, '&quot;') + '">' +
          '<span class="d-ic">' + ic(ph.icon, 22) + '</span>' +
          '<span class="d-name">' + ph.title + '</span></span>');
      } else {
        const m = doorMeta(id);
        r.insertAdjacentHTML('beforeend',
          '<button class="door dgo" data-go="' + id + '">' +
          '<span class="d-ic">' + ic(m[0], 22) + '</span>' +
          '<span class="d-name">' + m[1] + '</span></button>');
      }
    });
    if (!b.col) {
      holder.appendChild(r);
      return;
    }
    if (!fork) {
      fork = el('div', 'dag-fork');
      forkLeft = el('div', 'dag-fork-col');
      forkRight = el('div', 'dag-fork-col');
      fork.appendChild(forkLeft);
      fork.appendChild(forkRight);
      holder.appendChild(fork);
    }
    if (b.col === 'left') {
      forkLeft.appendChild(r);
      const floor = el('div', 'dag-floor');
      floor.textContent = 'the floor beneath is mathematics itself — ' +
        'nothing is drawn under the abstract computers';
      forkLeft.appendChild(floor);
    } else {
      forkRight.appendChild(r);
    }
  });
  const edges = fundEdges();
  // the hover: the mouse asks, the decision answers, the
  // application shows — a bottom rings alone, without dimming
  let focusId = null;
  const apply = () => {
    applyHighlight(holder, svg, svgTop,
      focusId ? fundHighlight(focusId) : null);
  };
  const draw = () => {
    const box = holder.getBoundingClientRect();
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    while (svgTop.firstChild) svgTop.removeChild(svgTop.firstChild);
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    defs.innerHTML = '<marker id="dag-arrow" viewBox="0 0 10 10" refX="10" refY="5" ' +
      'markerWidth="9" markerHeight="9" markerUnits="userSpaceOnUse" orient="auto">' +
      '<path d="M0 0 L10 5 L0 10 z" class="dag-arrowhead"/></marker>';
    svg.appendChild(defs);
    const defsTop = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    defsTop.innerHTML = '<marker id="dag-walk-arrow" viewBox="0 0 10 10" refX="9" refY="5" ' +
      'markerWidth="7" markerHeight="7" markerUnits="userSpaceOnUse" orient="auto">' +
      '<path d="M0 0 L10 5 L0 10 z" class="dag-walk-arrowhead"/></marker>';
    svgTop.appendChild(defsTop);
    svg.setAttribute('viewBox', '0 0 ' + box.width + ' ' + box.height);
    svgTop.setAttribute('viewBox', '0 0 ' + box.width + ' ' + box.height);
    edges.forEach((e) => {
      const a = holder.querySelector('[data-go="' + e[0] + '"]');
      const b = holder.querySelector('[data-go="' + e[1] + '"]');
      if (!a || !b) return;
      const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
      const x1 = ra.left + ra.width / 2 - box.left, y1 = ra.top + ra.height / 2 - box.top;
      const x2 = rb.left + rb.width / 2 - box.left, y2 = rb.top + rb.height / 2 - box.top;
      const build = !!e[2];
      let d;
      if (build) {
        d = buildD(a, b, box);
      } else if (Math.abs(y1 - y2) < 8) {
        const dip = Math.max(y1, y2) + 34;
        d = 'M' + x1 + ' ' + y1 + ' C' + x1 + ' ' + dip + ', ' + x2 + ' ' + dip + ', ' + x2 + ' ' + y2;
      } else {
        const mx = (x1 + x2) / 2;
        d = 'M' + x1 + ' ' + y1 + ' C' + mx + ' ' + y1 + ', ' + mx + ' ' + y2 + ', ' + x2 + ' ' + y2;
      }
      const p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      p.setAttribute('d', d);
      p.setAttribute('class', 'dag-edge' + (build ? ' dag-build' : '')
        + (PLACEHOLDERS[e[1]] ? ' dag-soon' : ''));
      p.setAttribute('data-a', e[0]);
      p.setAttribute('data-b', e[1]);
      if (build) p.setAttribute('marker-end', 'url(#dag-arrow)');
      svg.appendChild(p);
    });
    // redraw after resize: restore the current focus, if any
    apply();
  };
  holder.addEventListener('mouseover', (ev) => {
    const d = ev.target.closest ? ev.target.closest('.door[data-go]') : null;
    const id = d ? d.getAttribute('data-go') : null;
    if (id !== focusId) { focusId = id; apply(); }
  });
  holder.addEventListener('mouseleave', () => {
    if (focusId) { focusId = null; apply(); }
  });
  draw();
  window.addEventListener('resize', draw);
}

/* the isolated build's report panel: every circle on the map,
   and what hovering it does — the full route down, or an honest
   bottom that rings alone */
function fundReport(mount) {
  if (!mount) return;
  const name = (id) => {
    const ph = PLACEHOLDERS[id];
    if (ph) return ph.title;
    return doorMeta(id)[1];
  };
  fundPaths().forEach((r) => {
    const row = el('div', 'row');
    row.innerHTML = '<span>' + name(r.id) + ' <em>' + r.band + '</em></span>' +
      (r.bottom
        ? '<span class="bottom">bottom — rings alone</span>'
        : '<span>' + r.size + ' circles · ' + r.tracks + ' tracks · lands on ' +
          r.lands.map(name).join(', ') + '</span>');
    mount.appendChild(row);
  });
}
