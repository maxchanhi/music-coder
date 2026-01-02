# MusicCoder

MusicCoder is a musical esoteric programming language inspired by [Brainfuck](https://en.wikipedia.org/wiki/Brainfuck). It is designed as a superset of Brainfuck, making it **Turing complete**. The source code looks like a monophonic melody, where musical notes and rests represent instructions and memory operations.

## Features

- **Musical Syntax**: Code is written as a sequence of notes and rests.
- **Monophonic & Minimal**: Uses a single melodic line for logic, emphasizing a clean and minimal design.

## Hello World Example

Here is a "Hello World" program written as a Flute Solo. You can view and play the sheet music on MuseScore:
[**Hello World! for Flute Solo**](https://musescore.com/user/171617/scores/30570965?share=copy_link)

## Prerequisites

This project uses Python>=3.9. 

## Usage

### Running a MusicCoder Program

To execute a MusicCoder source file (`.mc`), use the interpreter:

```bash
python interpreter.py <source_file.mc>
```

Example:
```bash
python interpreter.py my_hello.mc
```

### Converting MusicCoder to MusicXML

You can convert your MusicCoder code into a standard MusicXML file, which can be opened in notation software like MuseScore, Finale, or Sibelius.

```bash
python mc2xml.py <source_file.mc> [output.musicxml]
```

If the output file is not specified, it defaults to the same name with a `.musicxml` extension.

### Converting MusicXML to MusicCoder

You can also write your code in a music notation program, export it as MusicXML, and convert it back to MusicCoder source code.

```bash
python xml2mc.py <input_file.musicxml>
```

## Language Specification

For a detailed guide on the syntax, memory model, and instruction set, please refer to the [Language Specification](spec.md).

## Similar Musical Esolangs

There are other esoteric programming languages that use music as code. One notable example is **Velato**, which uses MIDI files as source code. In Velato, the pitch of the first note in a measure determines the command, and the intervals between notes determine parameters. **Blue++** aims to produce code that sounds like actual music, composed in jazz scale. **Prelude** and **Fugue** uses polyphonic music as source code. Other examples include **Choon** where code is a sequence of notes the output stream itself acts as memory by allowing reference to previously played notes.
