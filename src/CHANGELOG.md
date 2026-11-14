# Changelog

The record of what each release changed. A release is one set of
files published together as one zip named
`everything-to-bits-vX.Y.Z.zip`; the unversioned
`everything-to-bits.zip` always mirrors the latest. The version
lives in `build.py` (`VERSION`), which stamps both built pages
(the generator meta and the footer) and refuses a template whose
stamps disagree with its own constant — bump them together, or
the build fails.

Numbers: minor for new content or features, patch for fixes and
wording. The deck's shape has not broken yet; a major number is
kept for the day it does.

## 1.8.1 — the note takes the bar, the story keeps its room

- A correction to 1.8.0's reading of the ask. The sponsorship's
  long story, the parable and the sidenote and the deck's own
  walk round the two programs, was never meant to sit in an
  always-visible banner; it has moved back to where it always
  lived, a view like any other, opened by its two doors. The
  words never changed, only the address did, and this is the
  old address again.
- What the ask meant was the closing line itself: the one that
  names the deck and the version, carries the sponsor's words
  verbatim, and offers "why this sponsorship" as a door. That
  line now rides in a bar of its own at the bottom of the
  window, the topbar's twin: sticky, always in sight wherever
  the page is scrolled, on the same translucent paper with the
  same hairline and blur. On the deck's page it sits centred,
  small and sans, and wraps when a narrow window asks it to.

## 1.8.0 — the land on request, the sponsor in plain sight

- The long note beneath the map now waits behind its own caption.
  "The territory beneath the stories, drawn from the model the
  whole deck is checked against" stays where it always was; the
  rest of it, the strata and the fork and the floors and the
  tap, folds under that line as a native `<details>`, offered
  rather than imposed, with an "unfold the land" cue in the
  deck's accent and a "fold it away" when it is open. The words
  inside are unchanged. The fold decides when they are read,
  not what they say.
- The sponsorship has its own banner now, and it never hides.
  The room it lived in was a view like any other, reached only
  through its doors; it has moved below the deck's wrapper,
  into a full-width band above the closing line, always
  visible on the deck's own paper. The parable, the sidenote
  and the sponsor's credit keep their places, and the sponsor's
  line in the footer stays verbatim.
- The doors still work, differently. The deck's header note and
  the footer's "why this sponsorship" now travel to the band
  instead of switching anything, and a hash that names an
  always-there section (#naveo, the map) opens the deck beneath
  it and then scrolls to it, so an old link still lands
  honestly. The banner keeps its id and its title, so the build
  still refuses a deck that loses it.

## 1.7.1 — the reading size, held to the research

- The type was set by feel; this release sets it by measurement.
  Wikipedia's own stylesheet (Vector 2022, the default an anonymous
  reader receives) sets its body at 14px in a sans face with a
  line-height of about 1.57. The deck's prose was already 21px
  Georgia at 1.6, so the feeling that Wikipedia reads larger was
  worth taking seriously but could not be settled by feel: the
  real problems were elsewhere, and the fixes below are each
  pinned to a published standard or study.
- Body text: 21px to 22px, and every reading surface up with it:
  figure captions 15 to 16px, the systems' part lines 14.5 to
  15.5px, their opened bodies and bottom notes 17 to 18px, margin
  notes 15.5 to 16.5px, the mirror table 16 to 17px, code blocks
  15 to 16px, the colophon 16 to 17px, the path report on the
  isolated map page 13.5 to 15px. The research consensus is that
  body text on screen belongs at 16px or above, and nothing the
  reader actually reads now sits below that floor by more than
  typography's own small-print customs allow.
- The measure: the research optimum for a line of prose is 50 to
  75 characters (Baymard Institute's finding; W3C WCAG 1.4.8
  holds 80 as the ceiling), and Dyson and Haselgrove (2001) found
  medium lines read more effectively than very long ones. The
  deck's prose column was running 84 to 94 characters on a
  desktop. Prose, lists and koans are now held to 36em, about 72
  characters at the new size, and the margin notes moved into the
  space that freed: the Tufte shape the page always wanted.
- Contrast: the deck's quiet grey carried real text at 4.44:1 on
  the paper background, just under WCAG 1.4.3's 4.5:1 minimum,
  and 4.03:1 on the code background. It is now a shade darker
  and clears the minimum on every surface it meets (5.69:1 on
  paper), and the ladder rung chips, which carried text at
  3.02:1, now meet it too. Line-heights of 1.4 on reading text
  came up to 1.45 or 1.6, past the W3C's space-and-a-half.
- Diagrams kept their own scale: the figures' internal labels,
  the keypad and the map's own geometry were left alone, save
  the map's panel, doors and floors, which rose half a step to
  a pixel each. The engine measures its labels live, so it
  re-centres them at the new sizes itself.
- Version stamped v1.7.1.

## 1.7.0 — every sentence, held to the standard

- The voice pass of 1.6.0 rewrote the connective tissue; the
  content had already passed the audition. This release holds
  every remaining sentence to the same standard, deck-wide: the
  audit that enforces STYLE.md (one em dash per paragraph at
  most, no banned LLMism vocabulary, no semicolon catalogs) was
  run over every text unit the deck owns, and everything it
  flagged was rewritten, then re-audited to zero flags.
- The data, by the diff against 1.6.1: 20 changed lines in
  `cards.xml` and 99 in `trails.xml` (blurbs, intros, bottoms,
  step lines and door questions).
- The template: 53 changed lines across the primers' prose,
  figure captions, sidenote-bearing paragraphs, the seven system
  views' how-to paragraphs, the map view's introduction, the
  view-source paragraph, the colophon, the sponsorship prose and
  the generated trail how-to. Dash-pair asides became parentheses, commas or
  colons; semicolon catalogs became sentences; the REPL loops of
  the two-rivers primer are now en-dashed compounds
  (`read–eval–print`), the typographically correct form.
- `build.py`: 20 changed lines. The map harness note on the
  isolated map page was brought into line with the template's
  version of the same paragraph, and the module docstring and
  three function docstrings were held to the standard too,
  since the deck invites its code to be read.
- Left alone, deliberately: the primer prose that already passes
  (the audit's flags were the target, not every sentence), the
  protected pure layer of `fund.js` and its two floor strings
  (each within the em-dash budget), the sponsor's footer line,
  which is the sponsor's, and `tests/hover.js`, which does not
  change.
- Version stamped v1.7.0.

- The type was set a notch too small for comfortable reading, and
  on a phone it strained. Every size a reader actually reads is up
  one step: the body from 20px to 21px, trail explanations from
  16px to 17px, the sys-how notes from 15px to 16px, the
  sidenotes from 14.5px to 15.5px, part names and one-line
  summaries a step larger, rung chips from 9.5px to 10.5px, card
  questions and hints a step up, the koan register from 19px to
  20px, figure captions, the colophon and the footer likewise.
  The mobile breakpoint keeps its steps and rises with them
  (subtitle 20px, card question 19px). The map panel follows
  (who 14px, roads 13.5px, the dive quote 14px, its buttons up
  to 12.5px), and the isolated map page's own body and report
  rise with it (17px, 13.5px). Two things are deliberately
  untouched: the map's storey labels, whose widths the layout
  engine estimates from the page's own font (a size change would
  have to travel into the engine's constants), and the
  diagram-and-figure labels inside the primers, which belong to
  their drawings.
- The two-rooms parable did not land: a master answering a
  riddle with a riddle. It is now the parable it should have
  been. A student reports the way the organization works written
  twice, once in its software and once in what its people
  actually do, the two disagreeing, and asks which copy to fix.
  The master replies with the one dry word the question deserves:
  “The one they obey.” The student is enlightened, and goes to
  watch what the people did. The sidenote's Gall now says the
  ground plainly: a system does what it does, not what it says
  it does, so the copy to fix is the one being obeyed.
- Version stamped v1.6.1.

## 1.6.0 — the deck finds its voice

- The prose read mechanical, clinical, patterned: the familiar
  shape of assistant writing. The offender was not the content.
  Every card blurb and trail blurb was auditioned and passed;
  the primer prose was already the deck's best. The offender was
  the connective tissue: seven identical "Tap a part to open
  it" instruction paragraphs across the system views, one
  generated instruction paragraph shared by all twenty-five
  trails, a landing paragraph that hedged, a map paragraph built
  as one enormous semicolon catalog, and em dashes doing the
  work of commas, colons and full stops roughly eight hundred
  times across the deck. All of it is rewritten; the content is
  kept, each instructional block now says the same things in
  its own words, and no sentence appears twice unless it earned
  it twice.
- STYLE.md is new, the deck's style guide: the law (everything
  bottoms out in a voltage that means yes or no; language serves
  transparency), the voice (direct, a little academic, with an
  irreverent side), the three borrowed registers — the Old
  Master, flat as a modern Tao, for bedrock truths; Master Foo
  parables, always original and credited to the manner, for
  forks and judgments; the deadpan systems law, after Gall,
  for sociotechnical ground — a banned list with the LLMisms
  itemized, and a syntax kit after Virginia Tufte's Artful
  Sentences. Future prose answers to it.
- The trope Tess asked for is now a fixture of the deck. The
  map's sys-how ends on the Old Master's word for the deep
  truth the whole deck serves: the largest computer and the
  smallest switch answer the same question, is the voltage
  high or is it low, and everything your machines have ever
  done for you is that question, answered very fast, very
  many times. The Bit primer closes on the same register:
  ten thousand programs, two states, one switch. The naveo
  view carries an original Master Foo parable — the student
  with two rooms, the people who live in the system and the
  people who write it — with a sidenote crediting the Rootless
  Root tradition and naming John Gall's Systemantics as the
  ground it lands on (sidenote 18, the first in the naveo
  view).
- Version stamped v1.6.0: build.py, the template's generator
  meta and footer, kept in step as the build demands.

## 1.5.1 — the stage joins the page, the panel clears the bar, the dive speaks up

- The map's stage could not centre: it was 1340px wide inside
  the deck's 1120px column, and `margin:auto` cannot centre a
  child wider than its parent, so on a desktop the map hung to
  the right, past the text column's design width, and read
  skewed. The stage is now the page's own design width, held in
  step with it: `width:min(1120px,calc(100vw - 48px))` (the
  width the deck's own .wrap carries), centred on the column by
  `margin-left:calc(50% - min(560px,calc(50vw - 24px)))` — the
  negative-margin centre, which centres a child wider than its
  parent where auto cannot. Verified across the width sweep:
  at every viewport from 320 to 1920 the map is centred to the
  pixel and never leaves the page; above 1168px its edges align
  exactly with the column's own edges.
- The tap's panel stuck at the top of the viewport — behind the
  deck's own topbar, which pins there first with a higher
  z-index — so once the reader scrolled into the map, the panel
  and the dive were never seen. The module now measures the
  bar the page wears (the deck's #topbar) and sticks the panel
  below it; the isolated build has no bar and keeps the CSS
  default.
- The dive button is the panel's one loud action now: filled
  with the accent (crimson on paper), larger, instead of a small
  ghost pill. The way further down reads before the words do.
- Two startup guards join the twelve of 1.5.0 (fourteen now):
  the stage (width plus the centring margin, so the
  overflow-to-the-right bug cannot return unnoticed) and the
  topbar clearance (so the panel cannot hide behind the bar
  again), plus one for the dive button's accent fill. The
  negative-test battery was rewritten around all of them.

## 1.5.0 — the map is a panorama, tapped, not a figure hovered

- The connecting lines are gone, by decision. They were dense,
  busy, and ran at odd angles for the little they carried; with
  the map's geometry re-laid-out they would only have grown
  worse. The map draws no lines at all now: the roads the lines
  once carried are the tap's to show, and the roads they never
  carried (the long-distance jumps the old hover invented
  between a circle and the bottom groupings) are left behind
  entirely — they were never informative, and no one will miss
  what was never drawn.
- In their place, one relationship set, shown one step at a
  time: tap a circle and it lights with its one-step neighbours
  — the roads that cross exactly one storey, and the built-from
  links — while the rest of the map fades back. Tap another
  circle to move the light, tap it again (or the space around)
  to clear. The set is the deck's own `fundEdges`, the drawn
  set of 1.4.0, read symmetrically: 47 relations (39 cross
  roads, 8 built-from links), pinned in a module of its own
  (`engine/relations.js`) with its own test
  (`node engine/tests/relations.js`, 437 checks).
- The map is laid out by a bespoke engine, at every width, in
  real geometry — not scaled as one figure. Every storey is a
  frame the width of its column, its label centred above it,
  its circles centred in balanced rows the engine itself
  chooses; the fork stands side by side while the window can
  hold two columns and stacks below that; the doors are always
  full size. Nothing scales, nothing wraps in the browser,
  nothing ever scrolls sideways: the engine re-lays the map
  out whenever the width it is given changes (ResizeObserver,
  with a resize listener behind it). The engine is a pure
  function with its own test
  (`node engine/tests/engine.js`, 25,492 checks over a sweep
  of 17 widths from 1920 down to 320).
- A panel under the controls tells the story of the tap: the
  circle's name, its stratum, a one-step count of its roads,
  and a dive button that opens the circle's view in the deck
  (in the isolated build, where no view exists, the dive
  reveals the intro the view would open with; a promise
  reveals its line). Every full circle opens its view this
  way.
- The full-screen zoom-and-pan view of 1.4.0 is removed, with
  the reason on record: it existed because the scaled figure
  could shrink past reading. The panorama never shrinks a
  door, so there is nothing left to zoom.
- The hover of 1.4.0 is withdrawn from the page but not from
  the contract: the pure decision layer (fundHighlight,
  fundPaths and the five functions around them) is kept
  byte-identical, and `node tests/hover.js` still exercises
  all 51 circles against it (31 full routes down, 20 bottoms
  ringing alone), so the official test keeps passing and the
  removal stays honest. The map's tap shows the one-step set
  instead of lighting the full route down.
- Twelve startup guards replace the seven of 1.4.0: the
  engine and relations modules are present and are what
  fund.js actually calls, the stage width, the absolute
  engine-placed frames, the rounded-rectangle border, no
  scaling (transform-origin), no browser wrapping in a band
  (the panel may still wrap its own text), no sideways
  scroll, no lines anywhere (dag-svg, dag-edge), the tap's
  panel and dive present, and the full-screen view gone.
- The build's census now reads the one set: 39 cross roads one
  storey each and 8 built-from links make 47 relations a tap
  can light; 70 roads inside a layer and 165 long walks stay
  behind, in the views, and the hover contract is reported as
  what it now is — the tested contract, kept for the official
  test, not for the tap.

## 1.4.0 — the map is a figure, not a layout

- The map stops reflowing, entirely. Every fix before this one
  tuned a CSS layout (bands that wrap or do not wrap, columns
  that stack or stand side by side), and every one of them still
  asked the drawing to re-measure itself at each window size —
  so each width drew a different map, and the layers came out
  ragged. The map was a reflow layout wearing a drawing's
  clothes. It is now one fixed figure: the module builds the
  bands once, locks the canvas at the width the widest storey's
  one line needs, draws every line once in those fixed
  coordinates, and then scales the whole canvas as a unit to
  the width the window gives it. No resize ever redraws, no band
  ever wraps, no column ever stacks, and no breakpoint exists
  anywhere in the map's styles. The picture is the same at every
  size, whole — smaller on a narrow window, identical in shape.
- A full-screen view reads the drawing large: a control under
  the figure opens it as a dialog that fits the whole map to
  the screen, with scroll or pinch to zoom, drag to pan, and a
  fit button to return. A door clicked full screen opens its
  view and gives the window back. A real drag swallows its own
  click, so panning never navigates.
- Seven startup checks replace the three layout guards of
  1.3.2: the stage width, the scale's transform origin, the
  one-line band rule, the rounded-rectangle band border, a
  refusal of any sideways scroll in the map's styles, and the
  full-screen view's markup and module — a layout regression
  now fails the build before it can ship.
- The hover is untouched: same decisions, same traced walks,
  the same logic harness passing unchanged (its mock measures
  no live scale, so the module's new scale correction falls
  back to 1 there, by design).

## 1.3.2 — nothing overflows, at any size

- The map no longer overflows, at any window size. The 1.2.0
  fix (bands forbidden to wrap) stopped the old capsule border
  cutting across circles, but it forced each storey into one
  line, and a storey's line is wider than a narrow panel can
  hold. Storeys now wrap again — the drawing stays inside the
  panel at every width — and the group border is a wrap-safe
  rounded rectangle (radius 12px, its padding keeping the
  curves off the circles), so no wrapped band's border can ever
  touch a node. The old capsule bug stays dead: the border can
  no longer be a capsule anywhere.
- The fork stacks: below 968px the thought column and the built
  column stand one above the other instead of side by side,
  each built pair still directly beneath what it builds, and
  the seam resting while they stack. On a wide window the
  drawing is still the one-line, widened view of 1.3.1.
- Nothing scrolls sideways anymore, at any size: sideways
  scroll is gone from the map. Two new startup checks guard the
  wrap-safe band rule and the fork's stacking breakpoint in
  fund.css, alongside the drawing-width check of 1.3.1.

## 1.3.1 — the drawing gets the window

- The map no longer scrolls on a desktop: the map is a drawing,
  and on a wide window it now steps outside the text column,
  centred on it, as wide as the window can hold (never wider
  than the widest storey needs). Sideways scrolling remains
  only below the width a storey's line needs, as designed. A
  startup check guards the drawing-width rule in fund.css.
- The organization promise is reworded: *how an organization
  runs*, with the line *rules nobody wrote, compiled from its
  own doing*. The sponsor's own line is now credited only in
  the footer, in the sponsor's words — never re-voiced by the
  deck — and a new build check refuses it in any data part.
- The sponsorship view gestures at the sponsor's line instead
  of quoting it: the deck keeps the long way round, and says so.

## 1.3.0 — the sociotechnical turn

- The sponsorship is explained in the deck itself: a new view,
  *Supported by Naveo*, opened by doors from the deck's front
  page and the footer. It walks the sponsor's thesis — an
  organization is a program that writes itself — from the deck's
  own ground: instructions followed exactly, and the people who
  write them. The build guards the view and its doors.
- Three grey circles join the map as promises of the same
  perspective: how the team shapes the machine (Conway's
  observation), how a program is a theory (the text as residue,
  the knowing in the team), and how an organization writes
  itself. They close the storey of the words and numbers, where
  software is written; the written-software trail doors into the
  first two and the facts trail into the third.
- Every static door the template carries must now open a section
  the template actually has — a new build check.
- The census moved to 15 promises, 70 walked roads inside a
  storey, 20 bottoms; 51 circles on the map, 31 still lighting
  full paths down. Lines (51), long walks (153) and the 65
  crossings of the drawn map are unchanged: the new roads run
  inside their own storey, walked in the views, never drawn.

## 1.2.0 — the versioned deck

- Versioning introduced: `VERSION` in `build.py`, stamped into
  both built pages and guarded by the build; releases delivered as
  versioned zips; this file is the record.
- Favicon: the Bit itself — one symbol filled, one hollow —
  inlined as a data URI, so the page stays one self-contained
  file with no second request.
- The map's wide bands no longer wrap: on a narrow window every
  storey stays one line and the map scrolls sideways, as the fork
  always did. The rounded storey borders no longer stretch into
  tall capsules that cut across their own circles on a phone.
- The sponsor is named in the footer of both built pages: Naveo,
  sociotechnical consulting — an organization is a program that
  writes itself.
- Content: unchanged from 1.1.0; this release is the machinery
  around the deck.

## 1.1.0 — the one-word language

Delivered before versioning was introduced; snapshotted as
`everything-to-bits-v1.1.0.zip` from the published artifacts.

- The promise of the one-word language became the trail
  `x-words`: the dictionary, the stack, the inner interpreter,
  the compiler that runs, the keypad — landing on memory and a
  real machine, crossing to ten views, with all sixteen doors
  that pointed at the promise re-pointed at the real trail.
- Twelve promises remain; the census moved to 25 trails, 51
  lines, 31 full hover paths, 17 bottoms.

## 1.0.0 — the live checkpoint

Delivered before versioning was introduced; no zip of this state
survives (it was overwritten by 1.1.0 in the unversioned
delivery).

- The deck went live: 7 cards, 24 trails, 10 primers, the map
  with its fork and its hover contract, the view stack with place
  memory and the URL hash, the left-aligned bands, the fork
  geometry fix, and the 28 negative tests guarding the build.
