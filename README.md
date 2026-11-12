# Everything to bits

You own a dozen computers. This page is a deck of doors into them — a single self-contained HTML page, entered through the things computers already do for you, walked down to the sand at whatever pace curiosity sets. The climb underneath every walk is the authors' own guidance; the reader is never told it, and may put it together.

## The way in

- **The deck.** The landing page opens like the cover of a book: an overline, the title, a subtitle, and one paragraph naming the walk — then three cards, each carrying its icon, its name, its question, and a small hint. No course, no lecture, no order. The reader picks a door.
- **The system.** Each card opens on a visual trail of the parts that make the thing happen, drawn as a vertical spine of tappable parts. Each part, tapped, explains itself in its own words and its own context: a short, concrete paragraph, no prerequisites.
- **The doors.** Every open step — part, trail step — ends in a row of round icons: doors into other paths, each wearing its target's icon and name, its question as a tooltip. Where a path is still to come, the circle is greyed and dashed but carries the missing path's own name, icon, and promise — a named placeholder, never filler. This is the one standard for leaving a path; blurbs carry no inline links, and nothing dangles at the bottom.
- **The ladder.** Every part carries a small label naming its rung of the universal ladder — *the world in, the world out, the manager, the program, the code, the machine, the dance, the fork, the bedrock, memory, the wire, the shared moment* — and parts always appear in ladder order, so every card walks the same descent from the world to the sand, whatever the thing.
- **The fundamentals.** Below the cards, one map of the whole deck: every view a circle, every door a line, cards on top, trails and greyed promises in the middle, the eleven primers at the bottom. Every circle opens its view; every line is a door that exists in the data. A sticky bar keeps *back* and *deck* one tap away from anywhere.

## The climb

Computation writ large, the one shape every answer shares: the world presses in and sensors turn it into numbers (input); programs decide what to make of the numbers, a manager shares the machine among them, and the machine obeys stored instructions, one at a time, on the beat (transformation); the decisions bottom out in logic gates and the numbers in bits (bedrock); and the result is turned back out into the world, in time (output). Three more rungs cut across the climb: memory (holding numbers against time), the wire (handing numbers between machines), and the shared moment (two hands, one instant).

This description is the authors' own guidance, kept as data and never rendered. There is no pattern page: the deck starts at the cards, and the reader drills down. The ladder is data only — one ordered list of slim rungs, an id and a chip each, the rails merged in as ordinary rungs — whose order sorts the parts of every card and whose chips label them. The reader walks the same descent many times and may put the shape together; nothing spells it out.

## The trails

Six self-contained lines of inquiry, each a vertical spine of tappable steps, each explaining *how the thing is done* rather than announcing that it can be. They cross-link mid-chain, so the whole deck is a directed graph, not a course:

- **How sound happens** — pressure, the diaphragm, sampling at 44,100, rounding to 65,536 steps, the WAV file, the bytes — landing on the Bit. Crosses to pictures (caught the same way: measured, rounded, numbered).
- **How an image happens** — one lamp, three numbers, the two-million-pixel grid, the frame buffer, drawing as arithmetic, the sixty-beat clock — landing on the Bit and the machine. Crosses to memory (how a circuit holds six million numbers) and to choices (who decides which numbers change).
- **How a message travels** — chopping, the numbered envelope, hop-to-hop routers, reassembly, keep-until-received — landing on the Bit and the machine. Crosses to time (the oldest bug and its cure).
- **Who runs the machine** — one instruction per instant, the switching illusion, the scheduler, files, the gatekeeper — landing on the machine and time. Crosses to choices and memory.
- **The machine itself** — the stored program, a number that means a command, fetch–decode–execute, the one design in every box — landing on the real-machine and Turing primers. Crosses to the manager.
- **How a machine decides** — one yes-or-no question, and/or/not from daily speech, the gate etched in sand, billions of forks — landing on Gates and the Bit. This is the strand that brings the reader to gates through *making choices*, not through arithmetic.

## The cards

**Playing games** — from the controller (two sticks, eight buttons, every one a switch) through the box under the television (a computer, wearing a costume) to memory, pixels, the shared world of multiplayer, and the save file that survives the off switch.

**Delivering food** — from the phone and its touchscreen grid, through the app (a list of instructions, written down in advance) and the warehouse server, to the match (facts and rules, searched), the route (a recipe that contains a copy of itself), the courier's one-word-at-a-time phone, and the bug the whole system exists to prevent: one order, two riders.

**Watching movies** — from two million lamps told what to be, through sound measured 44,100 times a second, the stream, the buffer, and the codec (a program that decides what your eye will not miss), to the remote's language of a dozen words and the suggestions (facts about millions of evenings, walked to a guess).

## The primers

The Bit · Gates · Arithmetic (NAND, then the ripple-carry adder) · Memory (the SR latch) · The Turing machine · A real machine (the von Neumann computer) · Recursion at ground level · Two rivers, one sky (FORTH and LISP) · The third way (Prolog) · Time enters (races, locks, pipes, Rust) · The tower, and how to build well inside it.

Twelve numbered figures, every one computed live; seventeen margin notes carrying the history, the citations, and the confessions of simplification. Each primer is self-contained: it never assumes another was read first, and it points outward at its end.

## How it is built

One file arrives at the reader: self-contained, no framework, no network. Behind that file sits a small build: the deck data lives in one schema-governed XML file, the template holds the prose and the engines, and one command validates, builds, tests, and installs — the published page is build output, never hand-edited. The page is designed the way LISP and FORTH would design instructional software: structure and content are split, and the structure is data walked by four small words.

- The deck kernel: the data — cards, parts, blurbs, doors, rung tags, the named placeholders, the six trails, and the ladder — lives in one XML file governed by one XSD schema. A part and a step are prose and doors, nothing else; a rung is an id and a chip, nothing else. The diagrams that once rode along are gone, and the interactive figures live in the template, never the data. The schema is the single source of truth: the build validates the data against it before rendering anything (the validator is a small interpreter for the exact XSD subset the schema uses, since the environment offers none). Doors render as round icons wearing the target view's icon and name, at least two per open step; where a path is still to come the door points at a named placeholder, which renders as a greyed, dashed circle carrying its own name and icon — never anonymous filler. One `doorHTML` walks every row, dedupes targets, and pulls labels and icons from the views and the placeholders themselves; the same doors also draw the map on the landing page, every view a circle and every door a line. The bottoms keep their closing note and end in their authored doors.
- The deck is layered, and the layers are data: cards carry level 0, trails and level-1 placeholders level 1, primers level 2 — pinned in the schema by enumeration. The reader descends gradually: a card's doors lead to trails, placeholders, or other cards, never straight to a primer; the build rejects a jolt with the exact row and target, and also insists that every part and step carry at least two distinct doors and that every placeholder be referenced.
- The landing page opens like the cover of a book: an overline, the title, a subtitle, one paragraph naming the walk, three cards each carrying its icon, name, and question, and — under the fundamentals — the map of the whole deck. Four builders walk it all (`renderDeck`, `renderSystems`, `renderExplainers`, `renderFundDAG`) over two shared primitives (`buildStrand`, `buildBottom`); `renderSystems` sorts every spine into ladder order, so a card's parts can be authored in any order and still descend, and `renderFundDAG` draws every view and door straight from the data, greyed and dashed where the target is still a promise. The view stack is three words (`go`, `goBack`, `homeDeck`), a FORTH-style trail of views with the deck at the bottom. Adding a card is adding an XML element with rung-tagged parts; adding a trail is adding another; the deck grows both directions without new code.
- The pipeline: one command validates the XML against the schema, cross-checks the data (door targets, rung tags, icon names, the layered descent, door floors, placeholder references), injects it into the template, and checks the built page itself — its title, its views, its balanced tags — before installing. The checks are few and deliberate, each guarding a mistake that has actually happened; a failure prints every problem found, names the exact row and target, writes nothing, and the canvas is written only after all checks pass. The live figures in the primers live in the template and are not driven by the build.
- One table of gate definitions (`GATES`) computes every truth table and every wire colour on the page.
- One shared transport player (`makePlayer`) runs the four machines — the Turing machine, the teaching CPU, the recursion demo, and the Prolog search — with play (toggling to pause), step, and stop.
- The FORTH calculator, the LISP cons-cell sketchpad, the Prolog pond, and the race track are small engines over a shared handful of helpers.
- The Prolog section is a real mini-resolver: unification with variables renamed per rule use, backtracking with choice points, every attempt on the record (long runs of rejections fold to one line).
- The concurrency figure is one state machine in two postures: two workers racing on an unowned cell, then the same workers handing +1 through a pipe to a single owner — the lost update and its cure, both steppable by hand.
- The script is written in numbered sections; the CSS has one labelled block per figure plus one for the deck and systems. The view-source paragraph keeps itself honest with what the page actually contains.

## Working conventions

- Prose voice: short declaratives, long clause-linked sentences, committed claims, no hedges, no filler. Curly quotes and em dashes throughout.
- Structure and content are split: the structure is visual and mobile-first (a spine of tappable parts, one thing per screen, a sticky way back), and the content arrives only on interaction — the reader asks, the part answers, in its own context.
- Curiosity first: the reader is brought to the fundamentals, never spoon-fed them. Each part must represent a question a real person has about a thing they really use, and each interaction must make one small idea sink deeper. No epigraphs, no surveys of the ground to be covered.
- Novice-first, by design: every piece of notation is read aloud where it first appears, the prose says what to do with each interactive figure before the figure appears, and where the reader can predict an outcome (Zeus's grandparents, 1011 plus one) the prose invites the prediction first. Sidenotes carry the history; the running text carries the explanation.
- No tropes for tropes' sake: the point is to wake the reader to the road less taken, so each topic is explained by what it *means* and what it *costs*, not by the shape it wore in the last textbook.
- Sidenotes are numbered; history and citations live there, not in the running text.
- Doors are round icons, uniformly: every open step ends in a row of at least two round doors into other paths, each labelled with its target's icon and name; where a path is still to come the door is a named placeholder — greyed and dashed, carrying the missing path's own name, icon, and one-line promise. Never an empty placeholder; no inline links inside blurbs, no dangling links at the bottom, no exceptions.
- The climb is guidance for the authors, not a lesson for the reader: it lives as data (the ladder, rung tags, ladder ordering in the XML) and no page shows it. The deck starts at the cards, and the reader drills down; walking the same descent many times is left to do its own teaching.
- Every historical or technical claim is verified before it is written.
- Deck content is entered as XML against the schema; the schema changes first when the data's shape must grow.
- The deck data is checked by the build before anything is written: schema, references, descent, floors, and the built page itself, all in one Python script with no dependencies. The live figures in the template are exercised by hand; the build does not drive them.

## Growth plan

The deck is built to grow; every layer takes new content without disturbing the others. A new card is now a filled-in scaffold, not a blank page: pick the thing, write its concrete parts, tag each part with its rung, and the spine, the chips, the doors (with named placeholders until real doors exist), and the ladder ordering all assemble themselves. Planned, one vertical at a time:

- **Hovering helicopters** — the gyroscope and pressure sensors (world in), the rotor told a number called throttle (world out), the flight controller (manager), the autopilot's hold-this-height promise (program), the measure-compare-correct loop (code), the little brain (machine).
- **Weather forecasting** — the sensors and satellites (world in), the map on the news (world out), the forecast computed while it is being read (shared moment), the model as a list walked again and again (code).
- **Drone choreography** — a swarm holding a shape: positions sensed and shown, one shared moment among many dancers, the wire keeping the copies in step.
- **More trails.** A payments trail (the ledger, the double spend, the trail of trust), a graphics-deeper trail (polygons, the pipeline, the GPU's thousand dancers), an encryption trail — each one only needs a trail element in the XML and doors from the cards that raise its question.
- **New primers.** C, memory, compilation (pointers, the malloc/free bug taxonomy, ending at Rust's ownership); types as safe decoding; let-it-crash, much later.
- **Card-first additions:** anything fundamental enough to earn a card question gets a card, not a chapter.

## Discipline for extensions

Each primer: a few paragraphs, one live figure, one or two sidenotes, an ending that points outward. Each card: real things people do, parts that explain themselves alone, every part tagged with its rung, doors down that mean something. Every new destination earns a question phrased the way a curious reader would ask it. Keep figures and sidenotes numbered in order; keep the ladder, the fundamentals map, the system trails, and the view-source paragraph honest with what the page actually contains.
