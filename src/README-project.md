# Everything to bits — the build

One page, one command. The reader receives a single self-contained
HTML file; this directory is where that file comes from, and the
canvas is build output: never edit it by hand.

The project is modular by design: the data is seven small XML
parts, the model is the source of truth every part is checked
against, the map is a module of its own laid out by its own
engine, and the build can validate a part alone or build the map
in isolation. No dependencies beyond Python 3 and Node for the
tests (no packages, no network):

```
deck.xsd        the single source of truth: what the data may be.
                Every part's root is declared here as a global
                element, so any part validates alone against it
data/           the deck data, one root per file:
  icons.xml       the icon library (one svg body per name)
  primers.xml     the primer index (level 2)
  placeholders.xml the named promises
  cards.xml       the seven stories (level 0)
  trails.xml      the twenty-five trails (level 1)
  ladder.xml      the one climb: rungs, an id and a chip each
  model.xml       the model, the source of truth: the strata of
                  the territory (what a person sees; the boundary
                  between the world and the data; machines
                  together; one machine, at work; the words and
                  numbers inside; the machinery of thought; then
                  the fork, drawn as two mirrored columns that
                  step down together — left: the tower of
                  abstractions, the ways of speaking, the formal
                  machines; right: the machine as built, its
                  components, the bedrock),
                  the nodes placing every view in exactly one
                  stratum, and the roads: land (where a trail
                  bottoms out), cross (a door inside a trail's
                  steps), build (ingredient to built thing)
template.html   the page skeleton: prose, CSS, JS, the live
                figures. Two markers receive the map module, and
                one `/*__DECK_DATA__*/{}` slot receives the data.
                The view stack keeps each view's place in the
                page and names the view in the address bar, so
                back, reload, and bookmark all return the reader
                to the same spot
fund.js         the map module's script: the panorama (the bands
                and doors painted from the engine's geometry,
                re-laid out whenever the width the window gives
                changes), the tap (a circle and its one-step
                neighbours light, the rest fades), the panel
                (name, stratum, roads, dive), the dive into the
                view itself, the report. One source, two builds
                (see below)
fund.css        the map module's styles: the panorama layout
                (every band placed by the engine's geometry,
                labels centred above the doors, doors full size
                at every width; nothing scaled, nothing wrapped
                by the browser, nothing scrolling sideways; the
                stage is the page's own design width, 1120px,
                centred on the column by a negative margin —
                margin:auto cannot centre a child wider than its
                parent), the focus dimming, the panel (stuck
                below the page's own bar), its accent dive
                button, and the door component the whole deck
                wears
engine/         the map's own engine, inlined ahead of fund.js
                by the build:
  layout.js      the pure layout function: the model, the
                widths, and the width available become one
                geometry — every storey a frame the width of
                its column, labels centred above it, rows
                centred and balanced within it, the fork side
                by side while 872px can hold it and stacked
                below, floors beneath their columns. No DOM,
                no CSS: geometry only, tested at 17 widths
                (engine/tests/engine.js)
  relations.js  the one relationship set the tap lights,
                pinned to the deck's own fundEdges: the roads
                that cross exactly one storey plus the
                built-from links, 47 relations, read from
                either end (engine/tests/relations.js)
  design.md     the engine's design record: the steps as they
                happened, the pivot to symmetry and no lines,
                the tap-and-dive interaction, the integration
  demo.html     the engine's demo page (make-demo.js writes
                it): the layout and the relations working
                together, with a width slider — the step-2
                prototype, superseded by the deck itself
tests/hover.js  the pure layer's contract as logic (the route
                down every circle, kept from the map's hover
                era and still the official test): lifts the
                built data, exercises every circle's decision,
                checks them against an independent
                reimplementation of the contract, and runs
                applyHighlight against a mock DOM. No
                dependencies beyond Node itself
build.py        validate → test → build (and --install the canvas)
build.sh        the one command: validate, test, build, install
CHANGELOG.md    the release record: what each version changed
STYLE.md        the deck's voice: the law, the registers, the
                banned list — read before writing prose anywhere
                in the project
```

`out/site.html` is regenerated by every build; `out/map.html` by
the isolated map build. This project is exported as artifacts
(deck.xsd, the data/ directory, template.html, fund.js,
fund.css, the engine/ directory — the layout engine, the
relations module, the design record, the demo and its tests —
build.py, build.sh, README.md, this file, STYLE.md,
tests/hover.js under
a `tests/` directory, and CHANGELOG.md). The working
environment can be reset between sessions; the artifacts are
the durable copies. To resume work, copy those files into one
directory (the seven parts under a `data/` subdirectory, the
test under `tests/`, the engine under `engine/`) and run `bash
build.sh`.

## Versioning

The version lives in `build.py` (`VERSION`), one constant, and
the build stamps it into both built pages — the `generator` meta
and the footer — refusing a template whose stamps disagree with
the constant, so a bump that forgets the footer fails the build.
A release is one set of files published together as
`everything-to-bits-vX.Y.Z.zip` (the unversioned
`everything-to-bits.zip` always mirrors the latest), and
`CHANGELOG.md` records what each release changed: minor for new
content or features, patch for fixes and wording. The footer of
both built pages also names the deck's sponsor, Naveo
(sociotechnical consulting), with its link; since 1.3.0 the
sponsorship also has a view of its own in the deck (`id="naveo"`,
titled *Supported by Naveo*), opened by doors from the deck's
front page and the footer, and three grey circles on the map —
how the team shapes the machine, how a program is a theory, how
an organization runs — hold the same perspective as
promises of views to come. The build refuses a template that
loses the view, its doors, or a static door that opens a section
the template does not carry, and it refuses any data part that
re-voices the sponsor's own line: the sponsor's words stay in
the footer, credited, and the deck writes its own version.

## Commands

```
python3 build.py                # validate + test + build out/site.html
python3 build.py --install     # also write the canvas
python3 build.py --data        # validate + test the data, no render
python3 build.py --part NAME   # schema-validate data/NAME.xml alone
python3 build.py --only map    # build out/map.html: the map in isolation
bash build.sh                  # the full build and install, one command
```

The isolation options exist so one piece can be tested thoroughly
on its own before it meets the whole — the lesson of the map
redesign: build it in isolation, get every relation right, then
integrate. `--only map` emits the same engine, module and
relations the deck inlines, the same data, none of the deck
around it, plus a per-circle report of the full route down each
circle (the hover contract the official test pins). The
decision layer is tested one level deeper still: `node
tests/hover.js` lifts the data off the built isolated page and
exercises the module's pure layer alone — every circle's route,
down-only and connected, bottoms that ring alone, parity with an
independent reimplementation of the contract, and applyHighlight
against a mock of the DOM calls it makes. The engine and the
relations module have their own batteries: `node
engine/tests/engine.js` (the layout's invariants across 17
widths) and `node engine/tests/relations.js` (the one-step set,
pinned to fundEdges).

Every check must pass before anything is written. A failure prints
every problem found at the failing stage, writes nothing, and exits
non-zero (`1` a check failed, `2` bad usage). On success the build
prints how many checks passed and what the page holds, including
the map census: the one relationship set a tap lights (cross
roads one storey each, built-from links, relations in all) and
what stays behind in the views (roads inside a layer, long
walks), plus the hover contract, reported as what it now is —
the tested contract, kept for the official test, not for the
tap.

## How the build works

`build.py` runs five stages, in order:

1. **parse** — all the files exist, and every data part is
   well-formed XML. A syntax error names the line and column.
2. **schema** — every part satisfies deck.xsd, checked alone or
   assembled. The assembled deck exists only in memory: the parts
   are the source, assembled in reading order (icons, primers,
   placeholders, cards, trails, ladder, model). The schema is
   checked by a small XSD interpreter carried inside build.py (the
   environment offers no XSD tooling). It pins the layers
   (`level="0"` cards, `"1"` trails and placeholders, `"2"`
   primers), the id patterns, the required attributes, the element
   order. Anything outside the interpreter's subset fails loudly
   rather than passing silently.
3. **data checks** — what the schema cannot express: door targets
   exist, icons and rungs are known, a card's doors never skip
   straight to a primer, a trail's first half never doors a primer
   (it starts high, on trails and promises, and reaches the sand
   only by degrees), every part and step offers at least two
   distinct doors, every named placeholder is referenced by
   something, and the template carries a section for every view the
   data names. The model is checked as its own contract: every view
   beneath the stories a node of exactly one labelled stratum, the
   stories kept off the territory (they are the cards above), every
   edge leading somewhere and each road owned once, only a trail
   opening a land or cross road, a landing never climbing, every
   door a trail opens being a road the model has (a trail walks
   only the roads the territory has; roads no trail walks still
   stand, unclaimed), each built-from edge spanning exactly one
   storey, staying on its side of the fork, and never touching a
   promise — and the hover contract: every trail, hovered, must
   light a path down that reaches at least one primer, and every
   circle's route — the drawn lines it lights plus the walks it
   traces — must connect the whole way down.
4. **build** — the JSON form of the data replaces the template's
   `/*__DECK_DATA__*/{}` slot, and the map module (fund.js, fund.css)
   is inlined into the template at its markers, so the reader still
   receives one self-contained page.
5. **output checks** — the built page itself: the slots were filled,
   the title and every view survived, the tags balance, the payload
   is valid JSON. The isolated map build checks its own page the
   same way.

The checks are few on purpose. Each guards a mistake that has
actually happened in this project, and each failure names the exact
row and target involved — copy any message into your notes and the
fix is usually obvious.

## The map module: one source, two builds

The fundamentals map (the strata of circles, the tap, the panel
and its dive) is deliberately not entangled with the deck's page
code. It lives in engine/layout.js, engine/relations.js, fund.js
and fund.css, and both builds consume the same sources — and
both read the model: MAP is its strata, EDGES its roads, and
CHAIN is derived from EDGES (the kind="build" roads) in the
template's shared constants, so the deck and the isolated page
walk the same territory:

- **the deck build** inlines all of it into template.html: the
  engine and the relations module, then the map module, at the
  `/*__FUND_MODULE__*/` marker, and the styles at
  `/*__FUND_CSS__*/`. The shared helpers (`$`, `el`, `ic`,
  `doorMeta`) sit inside marked bounds in the template, above
  the module's slot.
- **the isolated build** (`--only map`) lifts the shared helpers
  out of the template, loads the same three sources, feeds them
  the same data, and renders them on a bare page with a report:
  one row per circle — the full route down it (the tested
  contract), or an honest bottom.

Test the map with `--only map` until the tap lights the right
set, then build the deck: by construction the two render the
same sources, so what passed in isolation passes in the whole.
And test the layers as logic first: `node engine/tests/engine.js`
runs the layout over 17 widths with no page at all,
`node engine/tests/relations.js` pins the one-step set to
fundEdges, and `node tests/hover.js` runs the module's pure
decision layer over the real data, so every rule is believed
before the wiring is.

## The hover contract (kept for the official test)

The map's tap lights one-step neighbours, but the full path down
still exists, and the official test still pins it: the contract
is the hover of 1.4.0, withdrawn from the page and kept as the
tested guarantee that every circle has an honest route down.
One rule for every circle: the path down lights — the land
roads of the model (where the trail bottoms out, not the cross
roads inside its steps), and beneath them the built-from roads
read downward, from the built thing to the ingredient it is
made of. Once any part of that construction is reached, the
whole web it belongs to lights with it — a trail landing on
the gate lights the machine the gate builds, adders, memory,
the processor — but nothing above the hovered circle ever
lights, and a circle with nothing beneath it — a promise, or
the bedrock itself — rings alone, without dimming the map.
The storeys are fork-aware: the left and right columns of the
fork share one row, so nothing on the left is ever below
anything on the right, and the web completion only adds circles
strictly below the hovered circle's row — the seam is never lit
across, in either direction. The lit route is one connected
path of tracks, lines plus walks, every step of it drawn or
traced by the old figure; the census reports it, and the logic
harness (tests/hover.js) enforces it against an independent
reimplementation of the same contract, all 51 circles.

The module is layered to make its rules checkable: the pure
decision layer (fundHighlight, fundPaths and their pure
helpers) computes what the contract lights, byte-unchanged
since 1.4.0 and still tested; the application layer
(applyHighlight) turns one decision into class toggles, owning
no policy; the wiring (renderFundDAG) paints the engine's
geometry, re-lays it out when the width changes, and listens
for the tap, the panel and the dive. The relations module
(engine/relations.js) owns the set the tap actually lights:
fundEdges read from either end, one step each way. The build
enforces the data side twice over: every trail's route must
reach at least one primer, and every circle's route must
connect the whole way down.

## Authoring

- **Deck content lives in the data parts.** A part and a step: an
  element with its attributes, a `<blurb>`, and `<door>` children.
  A rung: an id and a chip, nothing else — the ladder is data only,
  its order sorts the parts of every card and its chips label them.
  Prose needs no escaping beyond `&lt;` for `<` and `&amp;` for
  `&`. There are no diagrams: parts and steps are prose and doors,
  nothing else. The schema documents the exact shape, and any part
  can be validated alone (`python3 build.py --part trails`). There
  is no pattern page, by design: the deck starts at the cards and
  the reader drills down; the rails are merged into the ladder as
  ordinary rungs.
- **The deck is layered, and the layers are data.** Cards carry
  `level="0"`, trails `"1"`, primers `"2"`; the schema pins each
  value. From a card (or its bottom) a door may lead to a trail, a
  placeholder, or another card — never straight to a primer. Trails
  sit one layer down and may reach the primers; that is what they
  are for.
- **Never an anonymous gap.** Where a path is still to come, point
  the door at a named `<placeholder>` and declare it in
  `data/placeholders.xml`: an id, a level, an icon, a title, one
  line. It renders as a greyed round door with its own name and
  icon. Every placeholder must be referenced by at least one door,
  and every row must offer at least two distinct doors; the build
  enforces both.
- **Fleshing a placeholder out** = writing the trail (or primer) it
  promises, deleting the placeholder, and re-pointing its doors at
  the new view.
- **Adding a card** = a `<card>` element in `data/cards.xml` with
  rung-tagged parts, the section and spine in template.html
  (`id="the-card"`, `id="the-card-parts"`), and doors from the
  paths that raise its question. The doors and the ladder ordering
  assemble themselves; the stories stay off the map by design.
  **Adding a trail** is one element in `data/trails.xml` plus a
  `<node ref>` in its stratum of the model plus the roads it
  walks (each door a `<edge kind="land|cross">`, each bottom door
  a land road); trails are built at runtime and need no template
  anchor. **Adding a primer** needs a section in template.html and
  a node in one of the construction strata; the map draws it and
  gives it its door.
- **The model: the territory and its roads.** Everything
  structural about the whole lives in `data/model.xml`: the
  strata, the nodes, the roads. A stratum runs the full width by
  default; `col="left"` opens the fork and builds the left
  column (the machine as thought, bottoming in mathematics
  itself) and `col="right"` continues the machine-as-built side
  down to the bedrock (bottoming in physics itself, a voltage
  high or low: each column closes on its own floor, and the
  drawing names both); the two columns mirror one another,
  storey for storey, and each carries its own built-from chain.
  The order of the nodes inside a stratum is the deck's canon —
  the trails page walks it too — authored, then tuned against a
  simulation of the drawing, and the tune never moves a node
  across strata and never breaks the grammar (trails open each
  stratum, promises close it, a primer grounds it last). A road is `<edge from="…" to="…" kind="…"/>`:
  `land` where a trail bottoms out (a road the tap's one-step
  set does not carry: the views walk it), `cross` a door inside
  a trail's steps (lit on tap when it crosses exactly one
  storey), `build` from ingredient to built thing (lit on tap,
  read from either end). Change the model first; the rest follows. The build
  refuses a road that ends nowhere, one the territory has twice,
  a landing that climbs, a door a trail opens that the model has
  no road for, and a built-from edge that skips a storey, crosses
  the fork, or touches a promise.
- **The live figures** (the interactive engines inside the
  primers) live in template.html, not the data. The build checks
  the page around them; it does not drive them. Exercise them by
  hand after changing them. The map's tap, panel and dive are
  exercised by the engine's own batteries and the demo smoke
  test instead, and its pure layers by the logic harnesses.

## When the build refuses you

Examples of what a mistake actually prints (paraphrased):

```
BUILD FAILED at schema validation (deck.xsd):
  /deck/cards[1]/card[1]/part[1]: unexpected element <art> (this
  deck carries no ASCII art — delete the <art> element; a part and
  a step is prose and doors, nothing else)
  nothing was written.

BUILD FAILED at data checks:
  card games, part 1 (the controller): door to 'bits' jolts straight
  to level 2 — ease down through a trail or a named placeholder
  nothing was written.

BUILD FAILED at data checks:
  placeholder p-memory (how it remembers) is never referenced — a
  promise nothing points at
  nothing was written.

BUILD FAILED at data checks:
  built-from edge 'adders'→'cpu' skips a storey — a built-from
  link reaches exactly one storey up
  nothing was written.

BUILD FAILED at data checks:
  the model has no road 'x-measure'→'x-clock' — a trail walks
  only the roads the territory has; add the edge to the model
  first
  nothing was written.

BUILD FAILED at data checks:
  trail x-clock, hovered, never reaches the construction — its
  landing must door at least one primer, so every circle lights a
  full path down
  nothing was written.

BUILD FAILED at data checks:
  view x-measure, hovered, lights a broken route — cpu lit but
  never reached, the tracks must connect the whole way down
  nothing was written.
```

The schema's error messages carry hints for the shapes that have
bitten before: pasting an `<art>` element back, confusing the
ladder's children (`<rung>` inside `<ladder>`, one ordered list of
id + chip), and off-pinned levels.

## Why the XSD interpreter

The environment offers no `xmllint`, no Java, no `lxml`, and package
installation is not allowed. Rather than let deck.xsd rot into
documentation the build merely hopes to follow, build.py carries a
small interpreter for exactly the subset the schema uses. The schema
stays the single source of truth: edit deck.xsd first when the
data's shape must grow, and the interpreter will tell you if it
cannot check a new construct.
