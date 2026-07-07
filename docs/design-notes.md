# Design notes

## The core idea

A person asks a question. The system turns it into SQL. That translation is the
whole product, and the design identity is built around making that translation
visible and legible, not around decoration.

## The warm and cool duality

Two typefaces carry two sides of the same event. Fraunces, a humanist serif,
renders natural language: the question the person typed, headlines, prose that
talks about the product. JetBrains Mono renders everything mechanical: SQL,
schema names, column types, result rows. A reader should be able to tell which
side of the translation they are looking at without reading a single word,
just from the letterforms.

Color reinforces the same split. `signal-warm` (#E8A13C) marks the human
question side: input focus rings, the cursor in the hero sequence, the badge
on a natural-language example. `signal-cool` (#57C7B4) marks the SQL and data
side: the generated query, the schema browser, the result grid header. `ok`
and `err` are reserved for execution outcomes only, never used decoratively.

## Restraint

Everything outside the hero translation sequence stays quiet: flat surfaces,
one hairline border color, no gradients, no drop shadows beyond a subtle one
on raised cards. The palette has no purple, violet, or indigo tone anywhere,
including in shadows or gradients, because that combination reads as generic
generated output rather than a considered choice.

## Motion

Framer Motion drives one orchestrated sequence in the landing page hero: a
question typed in Fraunces, the schema linking highlighting the tables it
uses, the SQL materializing line by line in mono, then the result grid
resolving. That sequence is the single memorable moment in the product.
Everywhere else, motion is a scroll reveal: a 20 pixel translate with a fade,
staggered across siblings, using a custom cubic-bezier easing rather than
linear or the default ease. `prefers-reduced-motion` disables the orchestrated
sequence and the scroll reveals fall back to an immediate, static state.
