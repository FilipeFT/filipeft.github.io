# Style guide

The voice of *Everything to bits*, written down so it survives the next
pass of writing. The deck's language is part of its argument: a machine
that follows instructions is not made clearer by prose that hedges,
decorates, or repeats itself. Every sentence teaches or amuses,
preferably both, and gets deleted if it does neither.

## The law

Everything in a computer bottoms out in a voltage that means yes or
no. Every walk in the deck ends at that floor, and so does every
sentence: language serves transparency. The reader's goal is to make
an opaque black box see-through; the prose's job is to hand them the
next pane. When a passage is unclear, it is not "stylistically weak",
it has broken the deck's one promise.

Say the deep thing plainly when it appears, and say it at the moment
the reader can see it, not before:

> The Old Master said: the largest computer and the smallest switch
> answer the same question. Is the voltage high, or is it low.

## The voice

Direct, a little academic, with an irreverent side. A good professor
over coffee: knows the material cold, delights in it, refuses to
condescend to the reader or to the machine. The register is warm, not
chatty; precise, not clinical.

House habits, in brief (capture the spirit, not the letter):

- Address the reader directly. Invite, walk alongside: "Let's take
  the ladder down."
- Parenthetical asides are welcome, one per paragraph at most, and
  the aside should be the joke or the exception, not a second
  sentence hiding in brackets.
- "see," mid-sentence, when pointing at something on the page.
- Exclamations are earned, not sprinkled.
- Concrete jokes beat abstract wit. A console is a computer whose
  program tells it to behave like a toy.
- The specific verb over the nominalization. Trails walk, doors open,
  the wire answers with a wobbling voltage.
- Sentences may run long when the road is long, and a short
  declarative after a long one lands hard. Rhythm follows content.

## The other registers

Three borrowed registers, each used sparingly and always at the
right altitude.

**The Old Master** (after Ron Hogan's flat modern rendering of the
Tao Te Ching). Short lines, plain words, flat paradox, no incense.
For the bedrock truths: the bit, the floor beneath the map, the
founding argument. One or two lines, at most once per primer, at the
moment the ground is reached. The Master states; the Master does not
advertise.

**Master Foo** (after the manner of Eric S. Raymond's *Rootless
Root*). Short parables for forks and judgment calls: a student asks
an either/or, the master reframes, the student is enlightened and
returns to work. Always original: write the parable, credit the
manner ("a koan, after the manner of Master Foo"), never quote
Raymond. The parable must carry a real point of the surrounding
text; if the deck argues about it, the parable is decoration and
must go.

**The deadpan systems law** (after John Gall's *Systemantics*).
Mock-academic laws about how systems actually behave, saved for the
sociotechnical material: organizations, teams, the seam between the
people who live in a system and the people who write it. Deadpan,
not cynical. Never quote Gall at length; capture the tone.

## Banned

The mechanical and the clinical, itemized. These are the tells the
deck was guilty of at v1.5.x, and none of them come back.

- **The dash chain.** At most one em dash per paragraph of new
  prose, and only when the interruption is the point. Otherwise a
  comma, a colon, a parenthesis, or a full stop does the work better.
- **"It's not just X, it's Y."** And its cousins "isn't merely",
  "is more than". State Y directly and let it be Y.
- **The vocabulary of the assistant:** delve, tapestry, testament,
  seamless, crucial, vibrant, landscape (figurative), unlock,
  elevate, "the power of", "In a world where", unprecedented.
- **The triple catalog.** Three appositive phrases in a row read as
  generated. Two, or a list with a colon and a reason.
- **The semicolon catalog as a default shape.** Semicolons separate
  clauses that dance; they do not replace paragraphs.
- **Templated instruction blocks.** The seven identical "Tap a part
  to open it" paragraphs were the deck's original sin. Any sentence
  that appears twice in the deck must earn it both times or die the
  second time.
- **Rhetorical openers.** "Have you ever wondered", "What if I told
  you". The reader came for the machine; get them to it.
- **Summary closers.** If the last paragraph restates the first,
  the last paragraph is the one to cut.
- **"serves as", "stands as", "acts as"** where "is" will do.

## Syntax kit

After Virginia Tufte's *Artful Sentences*, kept at the desk while
writing:

- Vary sentence shape, and let the shapes mean something: the
  free modifier trailing a main clause ("The film is not inside your
  television. It arrives continuously, as numbers, and the
  television paints it") moves the way the subject moves.
- A short declarative after a long sentence lands hard. Save it for
  the thing that must land.
- Parallelism with a purpose: the ladder rungs and the "from X to
  Y" trail spans are parallel because the deck's structure is
  parallel. Everywhere else, break the pattern once it is
  established; the pattern is a chord, not a wallpaper.
- The interruptive dash only when the interruption is the point.
- The colon promises; the semicolon connects two clauses that could
  stand alone but refuse to; the parenthesis whispers.

## Where prose lives, and what the build constrains

- **template.html:** the landing, the fund section, the seven system
  views' intros and sys-how notes, the generated trails sys-how.
- **data/cards.xml, data/trails.xml:** the blurbs. The v1.6.0
  audition passed them; they are the deck's best prose and the
  style guide governs what is added to them.
- **fund.js:** user-visible strings (floors, panel, dive).
- **build.py:** the map harness note, user-visible on the map page.

Constraints the build enforces, not to be fought: the sponsor line in
the footer is verbatim and no data part may quote it; version stamps
appear in the template head and footer; sidenotes are hand-numbered
in reading order, so a new sidenote renumbers everything after it.

## The self-check

Read the passage aloud. If it sounds like an FAQ, an announcement,
or a very polite stranger, rewrite it. If two sentences do one
sentence's work, cut one. If a phrase could survive in any website
about anything, it does not belong in this deck. And when in doubt,
remember the law: does the sentence make the black box more
see-through? Keep it. Otherwise, out.
