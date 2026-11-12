# From Sand to Symbols

You own a dozen computers. This page is a deck of doors into them — a single self-contained HTML page, entered through the things computers already do for you, walked down to the sand at whatever pace curiosity sets. And underneath every walk, one shape: the pattern.

## The way in

- **The deck.** The landing page is a few cards, each naming something the reader already does with a computer — playing games, delivering food, watching movies — and asking one honest question about it: *how does a button under your thumb move a world?* No course, no lecture, no order; the reader picks a door.
- **The system.** Each card opens on a visual trail of the parts that make the thing happen, drawn as a vertical spine of tappable parts. Each part, tapped, explains itself in its own words and its own context: a short, concrete paragraph and a small character-drawn diagram of exactly what it says, no prerequisites.
- **The ladder.** Every part carries a small label naming its rung of the universal ladder — *the world in, the world out, the manager, the program, the code, the machine, the dance, the fork, the bedrock* — and parts always appear in ladder order, so every card walks the same descent from the world to the sand, whatever the thing.
- **The doors down.** Every open part can end in a red line: a question that opens a trail. The trails branch, so at almost any step the reader may leave one line of inquiry for another — sound for pictures, pictures for choices, messages for the machine that carries them — and nothing is ever more than *back* away.
- **The pattern.** One page, one door from the deck, shows the whole scaffold at once: the nine rungs in the abstract, each opening onto the trail that deepens it and the cards that walk it, plus the three rails (memory, the wire, the shared moment) that cut across every rung. Every bottom note in the deck leads here.
- **The fundamentals.** Below the cards, a quiet index of the eleven primers — each one phrased as the question a curious reader would ask. They are not waiting to be read in order; they are waiting to be needed. A sticky bar keeps *back* and *deck* one tap away from anywhere.

## The pattern

Computation writ large, the one shape every answer shares: the world presses in and sensors turn it into numbers (input); programs decide what to make of the numbers, a manager shares the machine among them, and the machine obeys stored instructions, one at a time, on the beat (transformation); the decisions bottom out in logic gates and the numbers in bits (bedrock); and the result is turned back out into the world, in time (output). Three rails run alongside every rung: memory (holding numbers against time), the wire (handing numbers between machines), and the shared moment (two hands, one instant).

Each rung of the pattern opens onto its trail — *how sound happens* for the world in, *how an image happens* for the world out, *who runs the machine* for the manager, *two rivers* for the program, *recursion* for the code, *the machine itself* for the machine, *a real machine* for the dance, *how a machine decides* for the fork, *the Bit* for the bedrock — and onto every card that instantiates it: *Playing games — the controller* for the world in, and so on. Lateral movement is data, not prose: the pattern view is assembled from the ladder and the cards alone.

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

One file. No framework, no build step, no network. The page is designed the way LISP and FORTH would design instructional software: structure and content are split, and the structure is data walked by four small words.

- The deck kernel: `SYSTEMS` is data — cards, parts, blurbs, doors, and each part's rung on the ladder. `EXPLAINERS` is data — six trails, their step chains, their cross doors. `LADDER` and `RAILS` are data — the pattern itself: nine rungs and three rails, each with its icon, its line, its generic explanation, and its door to the trail or primer that deepens it. Every part, step, rung, and rail also carries an `art:` field — a small diagram drawn in plain characters — and the one strand builder renders it inside the open step, so a diagram costs one field and no code. Four builders walk all three (`renderDeck`, `renderSystems`, `renderExplainers`, `renderPattern`) over two shared primitives (`buildStrand`, `buildBottom`); `lateralDoors` assembles the pattern-to-cards doors from rung tags alone; `renderSystems` sorts every spine into ladder order, so a card's parts can be authored in any order and still descend. The view stack is three words (`go`, `goBack`, `homeDeck`), a FORTH-style trail of views with the deck at the bottom. Adding a card is adding an entry with rung-tagged parts; adding a trail is adding another; the pattern grows both directions without new code.
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
- Every step is drawn. Each open step shows, alongside its blurb, a small diagram drawn in plain characters — a monospace sketch of exactly what the blurb says: the button's switches closing into a row of bits, a save copying arrows, a packet with its numbered envelope, the fetch–decode–execute loop closing on itself. The diagrams are data (`art:` fields), so new cards and trails get them by simply writing one.
- Every historical or technical claim is verified before it is written.
- New demo and deck logic is simulation-tested before it is wired into the page.

## Growth plan

The deck is built to grow; every layer takes new content without disturbing the others. A new card is now a filled-in scaffold, not a blank page: pick the thing, write its concrete parts, tag each part with its rung, and the spine, the chips, the pattern's lateral doors, and the ladder ordering all assemble themselves. Planned, one vertical at a time:

- **Hovering helicopters** — the gyroscope and pressure sensors (world in), the rotor told a number called throttle (world out), the flight controller (manager), the autopilot's hold-this-height promise (program), the measure-compare-correct loop (code), the little brain (machine).
- **Weather forecasting** — the sensors and satellites (world in), the map on the news (world out), the forecast computed while it is being read (shared moment), the model as a list walked again and again (code).
- **Drone choreography** — a swarm holding a shape: positions sensed and shown, one shared moment among many dancers, the wire keeping the copies in step.
- **More trails.** A payments trail (the ledger, the double spend, the trail of trust), a graphics-deeper trail (polygons, the pipeline, the GPU's thousand dancers), an encryption trail — each one only needs an `EXPLAINERS` entry and doors from the cards that raise its question.
- **New primers.** C, memory, compilation (pointers, the malloc/free bug taxonomy, ending at Rust's ownership); types as safe decoding; let-it-crash, much later.
- **Card-first additions:** anything fundamental enough to earn a card question gets a card, not a chapter.

## Discipline for extensions

Each primer: a few paragraphs, one live figure, one or two sidenotes, an ending that points outward. Each card: real things people do, parts that explain themselves alone, every part tagged with its rung, doors down that mean something. Every new destination earns a question phrased the way a curious reader would ask it. Keep figures and sidenotes numbered in order; keep the ladder, the fundamentals index, the system trails, and the view-source paragraph honest with what the page actually contains.
