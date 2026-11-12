# From Sand to Symbols

How a machine that only knows *on* and *off* comes to understand `(fact 4)` — and to answer `?- grandparent(G, zeus).`

A ground-up primer on computing, written as a single self-contained HTML page. Every figure is live and expects hands. Nothing is hidden: view source, and the page explains its own making.

## The chapters

**Part I · The Machine**
1. The Bit — two states, the entire alphabet
2. Gates — AND, OR, NOT…, and NAND, the one gate that impersonates the rest
3. Arithmetic — a ripple-carry adder built from one-bit boxes
4. Memory — the SR latch, a loop of mutual justification
5. Turing — the minimal machine, stated honestly
6. A real machine — fetch, decode, execute, on a teaching computer
7. Recursion — factorial, and the stack underneath it

**Part II · Ways of Speaking**
8. Two rivers, one sky — FORTH facing the earth, LISP facing the sky, continuations where they meet
9. The third way — Prolog: facts, rules, and a search that grows its own frames

**Part III · The Long View**
10. The tower — abstractions, their leaks, and the habits of building well inside them

Eleven numbered figures, every one computed live, and a closing tower diagram. Fifteen margin notes carry the history, the citations, and the confessions of simplification.

## How it is built

One file. No framework, no build step, no network.

- One table of gate definitions (`GATES` in the script) computes every truth table and every wire colour on the page.
- One shared Step/Run/Reset player (`makePlayer`) runs the four machines: the Turing machine, the teaching CPU, the recursion demo, and the Prolog search.
- The FORTH calculator, the LISP cons-cell sketchpad, and the Prolog pond are small engines over a shared handful of helpers.
- The Prolog section is a real mini-resolver: unification with variables renamed per rule use, backtracking with choice points, every attempt on the record in its trail (long runs of rejections fold to one line).
- The script is written in numbered sections that follow the chapters; the CSS likewise has one labelled block per figure.
- Wires in diagrams end at the gate outline, not short of it. The OR-shaped gates are concave on the left — their edge sits well right of where a straight-edged gate would put it — and the geometry constants encode that.

## Working conventions

- Prose voice: short declaratives, long clause-linked sentences, committed claims, no hedges, no filler. Curly quotes and em dashes throughout.
- Sidenotes are numbered in reading order; history and citations live there, not in the running text.
- Every historical or technical claim is verified before it is written.
- New demo logic is simulation-tested before it is wired into the page.

## Growth plan

The primer is built to grow; each part can take further chapters without disturbing the others. Planned, in order:

- **Time enters** — concurrency: Hoare’s CSP (1978), Go’s channels, Erlang’s actors and let-it-crash, Rust’s compile-time race freedom.
- **C, memory, compilation** — pointers, the malloc/free bug taxonomy, the cons-stack compiler pipeline as a worked example, ending at Rust’s ownership.
- **What things may be** — types as safe decoding, Curry–Howard, Haskell, homotopy type theory.

These three form Part III · The Machine and the World, as chapters 10–12; the tower then becomes chapter 13 under Part IV · The Long View.

## Discipline for extensions

Each chapter: a few paragraphs, one live figure, one or two sidenotes, an ending that points outward. Renumber chapters, figures, and sidenotes in reading order; keep the table of contents, the part dividers, and the view-source paragraph honest with what the page actually contains.
