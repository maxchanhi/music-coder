# MusicCoder Language Specification

## Concept

A musical esoteric programming language. The source code mimics a musical score.

## Memory Model

- Standard Brainfuck tape (array of byte cells initialized to 0).
- A data pointer starts at the first cell.

## 1. Pointer Movement (Rests)

Rests control the movement of the memory pointer.

* **Quarter Rest (`R4`):** Move Pointer **Right** (`ptr++`). Resets "Previous Note".
* **Half Rest (`R2`):** Move Pointer **Left** (`ptr--`). Resets "Previous Note".
* **Bar Lines (`|`):** Ignored (Cosmetic).

## 2. Arithmetic (Interval-Based)

Arithmetic is determined by the transition between the **previous note** and the **current note**.

* **Ascending (Current > Previous):** `*ptr += Current`
  * Example: `C4` (60) to `D4` (62) $\rightarrow$ `62 > 60`. Adds `62`.
* **Descending (Current < Previous):** `*ptr -= Current`
  * Example: `C#4` (61) to `C4` (60) $\rightarrow$ `60 < 61`. Subtracts `60`.
* **Equal (Current == Previous):** Addition and Subtraction like in Brainfuck.
  * Example: `C4` (60) to `C4` (60) than `C#4` (61) $\rightarrow$ `61 - 60 = 1`. Adds `1` (Same as `+`).
  * Example: `C4` (60) to `C4` (60) than `B3` (59) $\rightarrow$ `69 - 60 = -1`. Subtracts `1` (Same as `-`).
  **It can add or subtract more than one:**
  * Example: `C4` (60) to `C4` (60) than `D4` (61) $\rightarrow$ `62 - 60 = 2`. Adds `+2`.
  * Example: `C4` (60) to `C4` (60) than `A#3` (58) $\rightarrow$ `58 - 60 = -2`. Subtracts `-2`.
  * See equal_arithmetic.md for examples.
  
* **Note after Rest:** When moving to a new cell (via `R4` or `R2`), the "Previous Note" value is reset to **0**.
  * This ensures calculations in the new cell start fresh relative to 0.
  * Example: `C4 R4 D4` $\rightarrow$ 
    1. `C4` (60): `prev=0` -> `Ascending (60>0)` -> `*ptr += 60`.
    2. `R4`: Move Right, Reset `prev=0`.
    3. `D4` (62): `prev=0` -> `Ascending (62>0)` -> `*ptr += 62`.

## 3. Loops (Repeats)

* **Start Repeat (`|:`):** Start of a loop block.
* **End Repeat (`:|`):** End of a loop block.
* **Repetition:**
  * By default (no suffix), the block behaves like a **Brainfuck Loop (`[...]`)**:
    * **Start (`|:`):** If `*ptr == 0`, jump to the end.
    * **End (`:|`):** If `*ptr != 0`, jump to the start.
  * Append `xN` to run **N times** (e.g., `:|x2`).
  * Append `x00` to run **infinitely**.
  * Append `R4` to run **N times**, where N is:
    1. Calculated from the **notes immediately following** the loop (e.g., `:|R4 C#5 C5` runs 1 time).
    2. If no notes follow, N is the value at the **next pointer position** (`ptr + 1`).
  * See loop.md for examples.
  

## 4. Articulation (I/O)

* **Staccato (`.`):** Output (`.`)
  * e.g., `C'.` $\rightarrow$ Add 60 and Print.
  * e.g., `G.` $\rightarrow$ Pass (No Add) and Print.
* **Legato (`_`):** Input (`,`)
  * e.g., `C_` $\rightarrow$ Read char.

## 5. Token Reference

`C-1=0 ... G9=127` (Standard MIDI Note Numbers)

* `C4` = 60
* `C5` = 72
* Rest `R4` (Quarter), `R2` (Half) : Pointer Movement (`>`, `<`)
* Barline `|` : Ignored / Separator

## 6. Comments

* **Comment Block (`<!-- ... >`):** Text between `<!--` and `>` is ignored by the interpreter.
  * Example: `<!-- This is a comment >`
  * Example: `C4 <!-- Play Middle C > D4`
