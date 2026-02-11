#!/usr/bin/env python3
"""
Lecture PDF to Notes Format Converter
Combines multiple lecture slides onto single pages with space for handwritten notes.
Perfect for GoodNotes, Notability, and other note-taking apps.
Author: Gianelli Lagos
GitHub: https://github.com/gianelli-lagos/lecture-notes-converter
"""

import argparse
import sys
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    import io
except ImportError:
    print("📦 Installing required packages...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf", "reportlab", "--break-system-packages"])
        from pypdf import PdfReader, PdfWriter
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        import io
        print("✓ Packages installed successfully!\n")
    except Exception as e:
        print(f"❌ Failed to install packages: {e}")
        print("Please run manually: pip install pypdf reportlab")
        sys.exit(1)


def create_combined_pdf(input_pdf_path, output_pdf_path, slides_per_page=5, 
                       note_space_ratio=0.3, show_borders=False, custom_label=None,
                       show_page_numbers=True, show_slide_numbers=True, 
                       show_separator=True, separator_color=None):
    """
    Combine multiple PDF slides onto single pages with note space.
    
    Args:
        input_pdf_path: Path to input PDF file
        output_pdf_path: Path to output PDF file
        slides_per_page: Number of slides to fit on one page (default: 5)
        note_space_ratio: Fraction of page width to reserve for notes (default: 0.3 = 30%)
        show_borders: Whether to draw borders around each slide (default: False)
        custom_label: Custom text to prepend to "NOTES"
        show_page_numbers: Show page numbers at bottom (default: True)
        show_slide_numbers: Show slide range at bottom (default: True)
        show_separator: Show vertical line between slides and notes (default: True)
        separator_color: RGB tuple for separator line (default: gray (0.6, 0.6, 0.6))
    """
    # Read the input PDF
    try:
        reader = PdfReader(input_pdf_path)
    except Exception as e:
        raise ValueError(f"Failed to read PDF: {e}")
    
    writer = PdfWriter()
    
    total_slides = len(reader.pages)
    
    if total_slides == 0:
        raise ValueError("PDF has no pages")
    
    print(f"📄 Processing {total_slides} slide{'s' if total_slides != 1 else ''}...")
    
    # Page dimensions (letter size: 8.5" x 11")
    page_width, page_height = letter  # 612 x 792 points
    
    # Calculate available space for slides (leaving room for notes on the right)
    slides_width = page_width * (1 - note_space_ratio)
    notes_width = page_width * note_space_ratio
    
    # Calculate slide dimensions
    slide_height = page_height / slides_per_page
    
    # Process slides in batches
    pages_created = 0
    for batch_start in range(0, total_slides, slides_per_page):
        # Create a new blank page
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        
        batch_end = min(batch_start + slides_per_page, total_slides)
        slides_in_batch = batch_end - batch_start
        
        # Draw slide borders if requested
        if show_borders:
            can.setStrokeColorRGB(0.8, 0.8, 0.8)
            can.setLineWidth(0.5)
            for i in range(slides_in_batch):
                y_position = page_height - (i + 1) * slide_height
                can.rect(0, y_position, slides_width, slide_height)
        
        # Calculate where the vertical line should end (at the last slide)
        last_slide_y_position = page_height - slides_in_batch * slide_height
        
        # Draw vertical separator line between slides and notes (only as far as slides go)
        if show_separator:
            # Use custom color or default gray
            if separator_color:
                can.setStrokeColorRGB(*separator_color)
            else:
                can.setStrokeColorRGB(0.6, 0.6, 0.6)
            can.setLineWidth(1)
            can.line(slides_width, last_slide_y_position, slides_width, page_height)
        
        # Add header in notes section
        notes_label = f"{custom_label} NOTES" if custom_label else "NOTES"
        can.setFont("Helvetica-Bold", 9)
        can.setFillColorRGB(0.3, 0.3, 0.3)
        
        # Center the label in the notes area
        label_width = can.stringWidth(notes_label, "Helvetica-Bold", 11)
        label_x = slides_width + (notes_width - label_width) / 2
        can.drawString(label_x, page_height - 20, notes_label)
        
        # Add slide range indicator below NOTES header (centered)
        if show_slide_numbers:
            can.setFont("Helvetica", 7)
            can.setFillColorRGB(0.5, 0.5, 0.5)
            slide_range = f"Slides {batch_start + 1}-{batch_end}" if batch_end > batch_start + 1 else f"Slide {batch_start + 1}"
            slide_range_width = can.stringWidth(slide_range, "Helvetica", 8)
            slide_range_x = slides_width + (notes_width - slide_range_width) / 2
            can.drawString(slide_range_x, page_height - 35, slide_range)
        
        # Add page number at bottom right
        if show_page_numbers:
            can.setFont("Helvetica", 8)
            can.setFillColorRGB(0.5, 0.5, 0.5)
            page_num = pages_created + 1
            can.drawRightString(page_width - 10, 10, f"Page {page_num}")
        
        can.save()
        
        # Create the base page
        packet.seek(0)
        base_pdf = PdfReader(packet)
        base_page = base_pdf.pages[0]
        
        # Add the actual slide content
        for i, slide_idx in enumerate(range(batch_start, batch_end)):
            original_slide = reader.pages[slide_idx]
            
            # Get original slide dimensions
            orig_width = float(original_slide.mediabox.width)
            orig_height = float(original_slide.mediabox.height)
            
            # Calculate scaling to fit the slide into allocated space
            # Use 98% of available space to add small margins
            scale_x = (slides_width / orig_width) * 0.98
            scale_y = (slide_height / orig_height) * 0.98
            scale = min(scale_x, scale_y)
            
            # Calculate position to center the slide in its space
            y_position = page_height - (i + 1) * slide_height
            
            scaled_width = orig_width * scale
            scaled_height = orig_height * scale
            
            # Center horizontally in slide area
            x_offset = (slides_width - scaled_width) / 2
            # Center vertically in slide slot
            y_offset = y_position + (slide_height - scaled_height) / 2
            
            # Merge the slide onto the base page
            base_page.merge_transformed_page(
                original_slide,
                [scale, 0, 0, scale, x_offset, y_offset]
            )
        
        writer.add_page(base_page)
        pages_created += 1
        
        # Progress indicator
        progress = (batch_end / total_slides) * 100
        print(f"  ⏳ Progress: {progress:.0f}% ({batch_end}/{total_slides} slides)", end='\r')
    
    print("")
    
    # Write the output PDF
    try:
        with open(output_pdf_path, 'wb') as output_file:
            writer.write(output_file)
    except Exception as e:
        raise ValueError(f"Failed to write output PDF: {e}")
    
    # Success summary!!
    print(f"\n✅ Successfully created: {output_pdf_path}")
    print(f"   📊 Stats:")
    print(f"      • Original slides: {total_slides}")
    print(f"      • Output pages: {pages_created}")
    print(f"      • Slides per page: {slides_per_page}")
    print(f"      • Note space: {int(note_space_ratio * 100)}% of page width")
    print(f"      • Compression: {total_slides}→{pages_created} pages ({(1 - pages_created/total_slides)*100:.0f}% reduction)")


def main():
    parser = argparse.ArgumentParser(
        description='Convert lecture PDF slides to note-taking format with space for handwritten notes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Basic Usage:
    %(prog)s lecture.pdf                           # Default: 5 slides/page, 30%% notes
    %(prog)s lecture.pdf -o output.pdf             # Custom output filename
    %(prog)s lecture.pdf -s 4 -n 0.35              # 4 slides/page, 35%% notes
  
  Personalization:
    %(prog)s lecture.pdf -l "CS101"                # Header: "CS101 NOTES"
    %(prog)s lecture.pdf -l "Sarah's"              # Header: "Sarah's NOTES"
    %(prog)s lecture.pdf --emoji rocket            # Header: "🚀 NOTES"
    %(prog)s lecture.pdf -l "Biology" --emoji book # Header: "📚 Biology NOTES"
  
  Customization:
    %(prog)s lecture.pdf -b                        # Show borders around slides
    %(prog)s lecture.pdf --no-page-numbers         # Hide page numbers
    %(prog)s lecture.pdf -s 3 -n 0.4               # 3 bigger slides, 40%% notes

Available Emojis: brain (🧠), rocket (🚀), star (⭐), fire (🔥), book (📚)
        """
    )
    
    parser.add_argument('input', type=str, 
                       help='Input PDF file path')
    parser.add_argument('-o', '--output', type=str, 
                       help='Output PDF file path (default: {input}_notes.pdf)')
    parser.add_argument('-s', '--slides', type=int, default=5, 
                       help='Number of slides per page (default: 5)')
    parser.add_argument('-n', '--note-space', type=float, default=0.3,
                       help='Fraction of page width for notes, 0-1 (default: 0.3 = 30%%)')
    parser.add_argument('-l', '--label', type=str, default=None,
                       help='Custom text before "NOTES"')
    parser.add_argument('--emoji', type=str, 
                       choices=['brain', 'rocket', 'star', 'fire', 'book'], 
                       help='Add emoji to header')
    parser.add_argument('-b', '--borders', action='store_true',
                       help='Show borders around each slide')
    parser.add_argument('--no-page-numbers', action='store_true',
                       help='Hide page numbers')
    parser.add_argument('--no-slide-numbers', action='store_true',
                       help='Hide slide range indicators')
    parser.add_argument('--no-separator', action='store_true',
                       help='Hide vertical line between slides and notes')
    parser.add_argument('--separator-color', type=str, default=None,
                       help='Separator line color as RGB (e.g., "0.5,0.5,0.5" for gray, "0,0,0" for black)')
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Error: Input file not found: {args.input}")
        return 1
    
    if not input_path.suffix.lower() == '.pdf':
        print(f"❌ Error: Input file must be a PDF, got: {input_path.suffix}")
        return 1
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / f"{input_path.stem}_notes.pdf"
    
    # Check if output file already exists
    if output_path.exists():
        response = input(f"⚠️  Output file already exists: {output_path}\n   Overwrite? [y/N]: ")
        if response.lower() not in ['y', 'yes']:
            print("❌ Cancelled")
            return 0
    
    # Validate parameters
    if args.slides < 1 or args.slides > 10:
        print(f"❌ Error: Slides per page must be between 1 and 10, got: {args.slides}")
        return 1
    
    if not 0 < args.note_space < 1:
        print(f"❌ Error: Note space ratio must be between 0 and 1, got: {args.note_space}")
        return 1
    
    # Build custom label with emoji if specified
    custom_label = args.label
    if args.emoji:
        emoji_map = {
            'brain': '🧠',
            'rocket': '🚀',
            'star': '⭐',
            'fire': '🔥',
            'book': '📚'
        }
        emoji = emoji_map[args.emoji]
        if custom_label:
            custom_label = f"{emoji} {custom_label}"
        else:
            custom_label = emoji
    
    # Parse separator color if provided
    separator_color = None
    if args.separator_color:
        try:
            rgb_values = [float(x.strip()) for x in args.separator_color.split(',')]
            if len(rgb_values) == 3 and all(0 <= x <= 1 for x in rgb_values):
                separator_color = tuple(rgb_values)
            else:
                print("⚠️  Warning: Invalid separator color format. Using default gray.")
                print("   Format: --separator-color '0.5,0.5,0.5' (values 0-1)")
        except ValueError:
            print("⚠️  Warning: Invalid separator color format. Using default gray.")
    
    # Process the PDF
    try:
        create_combined_pdf(
            str(input_path),
            str(output_path),
            slides_per_page=args.slides,
            note_space_ratio=args.note_space,
            show_borders=args.borders,
            custom_label=custom_label,
            show_page_numbers=not args.no_page_numbers,
            show_slide_numbers=not args.no_slide_numbers,
            show_separator=not args.no_separator,
            separator_color=separator_color
        )
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if '--verbose' in sys.argv:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())