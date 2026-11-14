# the map's layout engine — the design

The deck's map (the fundamentals diagram in fund.js/fund.css) went
through two drawing regimes and broke under both. This sub-project
builds the third: a bespoke layout engine, designed and prototyped
here, integrated into the deck only when the prototype is right.
The deck itself ships v1.4.0 untouched until then.

## why an engine at all

- **CSS reflow (v1.3.x)** dressed a drawing in flex bands; the
  geometry was traced after layout from getBoundingClientRect, so
  every window width re-drew the lines at new angles, wrapped
  bands raggedly, and produced scrollbars.
- **Uniform scaling (v1.4.0)** froze the figure and scaled it as a
  unit — correct geometry, but the widest storey measures ~1122px,
  so a 390px phone drew the whole map at ~33%: too small to read.
  Hover walks were also drawn into a second coordinate space.

The lesson: a fixed figure cannot be scaled, and a reflow cannot be
a drawing. What the map needs is a **layout engine**: a pure
function from the model and an available width to a geometry the
renderer simply paints, re-laid out deliberately at each width so
the doors stay full size everywhere.

## step 3 as it happened: the panorama pivot

The step-1/2 prototype (tiers, re-routed edges, hover walks drawn
from the same geometry) was reviewed and the direction changed:

1. **Symmetry at every scale.** The prototype's band frames had
   different sizes. The mandate: the whole drawing is symmetrical —
   every storey's frame is the same width as its column, its label
   centred above its doors, its rows centred in the frame. The map
   is a column of equal strata at any width.
2. **The connecting lines are gone.** They were dense, they met at
   strange angles, and they added little the strata and a tap do
   not carry better — and the model will only grow. Removing them
   subtracts a whole class of complexity (routing, crossings, the
   walk-space bug) rather than managing it.
3. **Tap to highlight, dive to enter.** The map's purpose is a
   panorama: how a whole story runs under each trail, explored
   sideways and entered from many doors, not just the cards up
   top. So: click or tap a circle → its roads light, the rest
   fades, and an option to dive into that view opens. No hover
   required — touch works the same as a mouse.
4. **One set of relationships (the review refinement).** The
   first cut of the tap lit the same set the deck's hover
   computed: the full transitive route down, which follows every
   land road — including roads that skip storeys, lighting
   distant circles straight down to the machine groupings. That
   was the hover's problem all along: it drew dashed walks
   straight from a hovered circle to the bottom, while the
   drawn lines quietly carried the intermediary relations.
   With the lines gone, only those long-distance relations
   would have remained, and they say little. Decision: the
   highlight uses exactly one set of relationships — the set
   the drawn lines represented, nothing else. A tap lights the
   tapped circle and its neighbours across those roads: one
   step, up or down, never further. The long-distance
   relations are left behind. (The set is the deck's own
   `fundEdges()`: the roads spanning exactly one storey — in
   the model, 39 cross roads — plus the 8 built-from links;
   the engine's test pins the two definitions together.)

## the engine's contract (layout.js)

```
layoutMap(model, widths, avail, cfg) → geo
```

- `model`: `{ bands, floors }` — bands are the map's own
  (`{ id, label, col: null|'left'|'right', views: [ids] }`),
  floors the two column footnotes.
- `widths`: `{ labels: { bandId: px } }` measured by the renderer;
  the engine estimates from text by default.
- `avail`: the container's content width in px.
- `cfg`: partial overrides of `defaults`.

`geo` carries, in ONE coordinate space: `bands` (each with frame
`x/y/w/h`, centred `label`, `rows` of doors, `doors` map), a flat
`doors` map (`{ id, x, y, w, h, cx, band, row }` — doors are ALWAYS
full size), `floors`, `width`, `height`, `fork` (`'side'` while half
the width holds a readable column — ≥ `2*minColW + colGap`, else
`'stacked'`), `natW` (the widest storey on one line; the width at
which nothing wraps), and `key` (for renderer change detection).

What is deliberately NOT in `geo`: edges, paths, crossings. The
engine lays out boxes; relation is carried by interaction.

Invariants (checked by engine/tests/engine.js at 17 widths,
1920→320, 25,492 checks): every view placed once at full size;
uniform frame widths per column; centred labels and rows; doors
inside their frames; no overlaps anywhere; authored order
preserved through every wrap; the fork rule; floors beneath their
own column; no lines in the geometry; determinism.

## the one relationship set (relations.js)

```
makeRelations(bands, edges) → { lines, rows, bandOf,
  neighborsOf(id), focusSet(id), degree(id) }
```

The pure definition of the one set of relationships: `lines` is
the deck's own drawn set (`fundEdges()` — a road spanning exactly
one storey, or a built-from link, both ends on the map; 39 cross
roads + 8 build links at v1.4.0), `focusSet(id)` is the tapped
circle plus its neighbours across those roads — one step, up or
down — and `neighborsOf(id)` reports each neighbour's direction
and whether the road is a built-from link, for the panel.

Invariants (checked by engine/tests/relations.js, 437 checks):
the line set is pinned to fund.js's `fundEdges` — the test fails
if the engine and the deck ever drift; every line spans exactly
one storey (no climbs, no level runs, no skips); every focus set
is its door plus its neighbours, symmetric, and nothing more than
one storey away — the long-distance relations cannot come back by
accident. Census at v1.4.0: 38 doors have a road to light (the
old closure lit more on 24 doors — those extras are the
long-distance relations, gone; the one-step set exceeds the old
down-only closure on 13 doors, because the drawn cross roads run
both ways and the old hover never followed them).

## the interaction model (the demo, then the deck)

- **Tap/click a door** → `relations.focusSet(id)` lights the
  tapped door and its drawn-road neighbours, everything else
  (doors, labels, frames) fades. Tap another door to move; tap
  the same door or blank space to clear. Touch and mouse behave
  identically.
- **The panel** shows the tapped door's story: name, stratum, and
  the roads by direction — "leads down to …", "built from …",
  "comes from …", "builds into …" — or an honest "no drawn roads:
  it rings alone". No counts, no distant lands.
- **Dive** reveals the view's own opening (a trail's intro, a
  card's question, a placeholder's line). In the deck this opens
  the view itself, as a door click does today.

## the steps

1. **The engine** — done. Pure `layoutMap`, tested in Node across
   the width sweep.
2. **The demo** — done (lines era), reviewed, and superseded by
   step 3's pivot.
3. **The pivot** — done. Engine rewritten for symmetry with no
   edges; demo rebuilt as the panorama (tap to highlight, dive to
   enter); this document updated to match.
   Refined after review: the highlight now uses the one
   relationship set (relations.js), not the old hover's
   transitive closure — one step along the drawn roads, the
   long-distance relations left behind.
4. **Integration** — done (v1.5.0). fund.js rewired:
   `renderFundDAG` renders the engine's geometry (measuring
   label widths, computing avail from the container, re-laying
   out on resize by `geo.key`), the SVG overlays are gone, the
   tap lights the relations module's `focusSet` through the
   unchanged `applyHighlight`, the panel and the dive strip tell
   the story (`dagFullscreen` is removed with the reason on
   record: the panorama never shrinks a door, so there is
   nothing left to zoom). tests/hover.js stayed UNCHANGED and
   green: it tests the pure `fundHighlight`/`fundPaths` layer,
   which stays in the module untouched even though the map no
   longer calls it for its tap.
5. **Guards** — done (v1.5.0). build.py's 7 startup guards for
   the v1.4.0 map became 12 for the engine's invariants: the
   engine and relations sources present and actually called
   (ETBLayout/ETBRelations), the stage width, absolute
   engine-placed frames, the rounded-rectangle border, no
   transform-origin, no flex-wrap inside a band rule, no
   sideways scroll, no lines anywhere (dag-svg, dag-edge), the
   tap's panel and dive present, the full-screen view gone, and
   the shared helper block intact.
6. **Negtests + release** — done (v1.5.0). The negative-test
   battery was rewritten around the new guards, the changelog
   entry written, the version bumped, and the release published.
7. **Integration polish** — done (v1.5.1), from Tess's reading
   of the integrated map. Three fixes: the stage joins the page
   grid (it was 1340px inside the 1120px column, and
   margin:auto cannot centre a child wider than its parent, so
   the map hung past the column's right edge; now the stage is
   the page's own design width, min(1120px, 100vw − 48px),
   centred by the negative margin calc(50% − min(560px, 50vw −
   24px)), verified centred and contained from 320 to 1920);
   the panel clears the page's own bar (it stuck at the
   viewport top behind the deck's #topbar, so the tap's story
   and the dive were never seen once the reader scrolled; the
   module now measures the bar and sticks below it); and the
   dive button is filled with the accent, the panel's one loud
   action, instead of a small ghost pill. The stage guard grew
   the centring margin, and two guards joined the battery for
   these (fourteen startup checks in all), and the negtests
   were rewritten again.

## what stays untouched

`fundHighlight` / `fundPaths` (pure, and the deck's official hover
test depends on them — the new tap simply stops using them), the
door component's markup, the data model, deck.xsd, and the built
pages until integration ships as a release.
