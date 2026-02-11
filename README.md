# Lecture Notes Converter

Convert lecture slide PDFs into note-taking format by combining multiple slides per page with dedicated space for handwritten notes.

Perfect for GoodNotes, Notability, and other digital note-taking apps.

## Why I Built This

I was spending more time screenshotting, resizing, and organizing lecture slides than actually *learning* the material. After manually arranging slides for the third time in one week, I decided enough was enough and automated the whole thing. Now I spend 30 seconds prepping my notes instead of 20 minutes. 

If you're reading this at 2am before an exam frantically organizing slides... you're welcome. 😅

---

## The Problem

Lecture slides are typically one slide per page, which:
- Wastes screen space when taking digital notes
- Makes it hard to see context across multiple slides
- Requires constant scrolling and zooming
- Turns note prep into a tedious chore

## The Solution

This tool automatically combines multiple slides (default: 5) onto each page and reserves space on the right for your handwritten notes.

**Result:** A 50-slide lecture becomes just 10 pages with plenty of room to write.

---

## Installation

Requires Python 3.7+ and two dependencies:

```bash
pip install pypdf reportlab
```

The script will auto-install these if missing.

---

## Usage

### Basic

```bash
python lecture_notes_converter.py lecture.pdf
```

Creates `lecture_notes.pdf` with 5 slides per page and 30% notes area.

### Common Examples

**Fewer slides per page (bigger slides):**
```bash
python lecture_notes_converter.py lecture.pdf -s 3
```

**More note space:**
```bash
python lecture_notes_converter.py lecture.pdf -n 0.4
```
(40% of page width for notes)

**Custom output filename:**
```bash
python lecture_notes_converter.py lecture.pdf -o my_notes.pdf
```

**Personalized header:**
```bash
python lecture_notes_converter.py lecture.pdf -l "CS101" --emoji rocket
```
Creates header: "🚀 CS101 NOTES"

---

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `-s, --slides` | Slides per page (1-10) | 5 |
| `-n, --note-space` | Notes area width (0-1) | 0.3 (30%) |
| `-l, --label` | Custom header text | None |
| `--emoji` | Add emoji (brain/rocket/star/fire/book) | None |
| `-o, --output` | Output filename | `{input}_notes.pdf` |
| `-b, --borders` | Show slide borders | Off |
| `--no-separator` | Hide vertical line between slides/notes | Off |
| `--separator-color` | Custom separator color (RGB) | Gray |
| `--no-page-numbers` | Hide page numbers | Off |
| `--no-slide-numbers` | Hide slide indicators | Off |

---

## Layout

```
┌─────────────────────────┬──────────────┐
│   SLIDE 1               │              │
│                         │   NOTES      │
├─────────────────────────┤              │
│   SLIDE 2               │              │
│                         │   (blank     │
├─────────────────────────┤   space for  │
│   SLIDE 3               │   your       │
│                         │   writing)   │
├─────────────────────────┤              │
│   SLIDE 4               │              │
│                         │              │
├─────────────────────────┤              │
│   SLIDE 5               │              │
│                         │              │
└─────────────────────────┴──────────────┘
```

---

## Tips

**Dense slides with lots of text?**
```bash
python lecture_notes_converter.py lecture.pdf -s 3 -n 0.4
```
Bigger slides, more writing space.

**Simple slides with mostly images?**
```bash
python lecture_notes_converter.py lecture.pdf -s 7 -n 0.25
```
More slides visible, less note space needed.

**Batch process multiple lectures:**
```bash
for file in *.pdf; do
    python lecture_notes_converter.py "$file" -l "CS101"
done
```

**Clean minimal look (no separator line):**
```bash
python lecture_notes_converter.py lecture.pdf --no-separator
```

**Custom separator color:**
```bash
# Black separator
python lecture_notes_converter.py lecture.pdf --separator-color "0,0,0"

# Light gray separator
python lecture_notes_converter.py lecture.pdf --separator-color "0.8,0.8,0.8"
```

---

## FAQ

**Q: Does this work with all PDFs?**  
A: Yes, any PDF will work.

**Q: Will this modify my original file?**  
A: No, it creates a new file. Your original is untouched.

**Q: Can I change the page size?**  
A: Currently outputs US Letter (8.5"×11").

**Q: What if slides are different sizes?**  
A: The tool auto-scales each slide to fit while preserving aspect ratio.

---
Built by Gianelli Lagos because organizing slides shouldn't be harder than learning the actual material.

## License

MIT License - free to use, modify, and share.
