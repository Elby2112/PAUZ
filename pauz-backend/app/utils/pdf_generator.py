from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from app.models import GuidedJournal, FreeJournal, Hint
from typing import List
from app.models import Prompt

def generate_pdf_guided_journal(guided_journal: GuidedJournal) -> bytes:
    """
    Generates a PDF for a given journal.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph(f"GuidedJournal: {guided_journal.topic}", styles['h1']))
    story.append(Spacer(1, 12))

    # Entries
    for entry in guided_journal.entries:
        story.append(Paragraph(f"Prompt: {entry.prompt.text}", styles['h3']))
        story.append(Spacer(1, 6))
        story.append(Paragraph(entry.response, styles['Normal']))
        story.append(Spacer(1, 12))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

def generate_pdf_free_journal(free_journal: FreeJournal, hints: List[Hint]) -> bytes:
    """
    Generates a PDF for a given FreeJournal and its associated Hints.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Free Journal", styles['h1']))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Content:", styles['h2']))
    story.append(Paragraph(free_journal.content, styles['Normal']))
    story.append(Spacer(1, 12))
    
    if hints:
        story.append(Paragraph("Hints Provided:", styles['h2']))
        for hint in hints:
            story.append(Paragraph(f"- {hint.hint_text}", styles['Normal']))
            story.append(Spacer(1, 6))
    else:
        story.append(Paragraph("No hints were generated for this session.", styles['Normal']))
    
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Created At: {free_journal.created_at.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))


    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
