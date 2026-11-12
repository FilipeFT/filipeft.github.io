# From Sand to Symbols

You own a dozen computers. This page is a deck of doors into them — a single self-contained HTML page, entered through the things computers already do for you, walked down to the sand at whatever pace curiosity sets.

## The way in

- **The deck.** The landing page is a few cards, each naming something the reader already does with a computer — playing games, delivering food, watching movies — and asking one honest question about it: *how does a button under your thumb move a world?* No course, no lecture, no order; the reader picks a door.
- **The system.** Each card opens on a visual trail of the parts that make the thing happen — the controller, the box under the television, the memory, the screen — drawn as a vertical spine of tappable parts. Each part, tapped, explains itself in its own words and its own context: a short, concrete paragraph, no prerequisites.
- **The doors down.** Every open part can end in a red line: a question that opens a primer. The trail runs from the concrete to the fundamental — first the machine doing visible work, then the parts, then the parts underneath the parts — until it lands on bits, gates, and instructions. At the bottom of every system, one note says it plainly: follow any part far enough down and it dissolves into switches.
- **The fundamentals.** Below the cards, a quiet index of the eleven primers — each one phrased as the question a curious reader would ask. They are not waiting to be read in order; they are waiting to be needed. A sticky bar keeps *back* and *deck* one tap away from anywhere.

## The cards

**Playing games** — from the controller (two sticks, eight buttons, every one a switch) through the box under the television (a computer, wearing a costume) to memory, pixels, the shared world of multiplayer, and the save file that survives the off switch.

**Delivering food** — from the phone and its touchscreen grid, through the app (a list of instructions, written down in advance) and the warehouse server, to the match (facts and rules, searched), the route (a recipe that contains a copy of itself), the courier's one-word-at-a-time phone, and the bug the whole system exists to prevent: one order, two riders.

**Watching movies** — from two million lamps told what to be, through sound measured 44,100 times a second, the stream, the buffer, and the codec (a program that decides what your eye will not miss), to the remote's language of a dozen words and the suggestions (facts about millions of evenings, walked to a guess).

## The primers

The Bit · Gates · Arithmetic (NAND, then the ripple-carry adder) · Memory (the SR latch) · The Turing machine · A real machine (the von Neumann computer) · Recursion at ground level · Two rivers, one sky (FORTH and LISP) · The third way (Prolog) · Time enters (races, locks, pipes, Rust) · The tower, and how to build well inside it.

Twelve numbered figures, every one computed live; seventeen margin notes carrying the history, the citations, and the confessions of simplification. Each primer is self-contained: it never assumes another was read first, and it points outward at its end.

## How it is built

One file. No framework, no build step, no network. The page is designed the way LISP and FORTH would design instructional software: structure and content are split, and the structure is data walked by four small words.

- The deck kernel: `SYSTEMS` is data — cards, parts, blurbs, and their doors, all declared in one place. Three words render it (`renderDeck`, `renderSystems`, `deepHTML`); the view stack is three more (`go`, `goBack`, `homeDeck`), a FORTH-style trail of views with the deck at the bottom. Adding a card is adding an entry; nothing else changes.
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
- Every historical or technical claim is verified before it is written.
- New demo and deck logic is simulation-tested before it is wired into the page.

## Growth plan

The deck is built to grow; every layer takes new content without disturbing the others. Planned:

- **More cards.** *Finding your way* (maps, GPS, the sensors underneath), *talking to friends* (messages, the network, encryption's one bright idea), *listening to music* — each a spine of parts over the same fundamentals.
- **Deeper parts.** Each system can grow intermediate layers between the visible thing and the sand — a graphics part on the games card, a payments part on the food card.
- **New primers.** C, memory, compilation (pointers, the malloc/free bug taxonomy, ending at Rust's ownership); types as safe decoding; let-it-crash, much later.
- **Card-first additions:** anything fundamental enough to earn a card question gets a card, not a chapter.

## Discipline for extensions

Each primer: a few paragraphs, one live figure, one or two sidenotes, an ending that points outward. Each card: real things people do, parts that explain themselves alone, doors down that mean something. Every new destination earns a question phrased the way a curious reader would ask it. Keep figures and sidenotes numbered in order; keep the fundamentals index, the system trails, and the view-source paragraph honest with what the page actually contains.
