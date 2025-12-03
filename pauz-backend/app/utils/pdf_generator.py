from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from app.models import GuidedJournal, FreeJournal, Hint
from typing import List
from app.models import Prompt

def generate_pdf_guided_journal(guided_journal) -> bytes:
    """
    Generates a PDF for a given journal. Accepts both dict and SQLModel objects.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Handle both dict and object formats
    if isinstance(guided_journal, dict):
        topic = guided_journal.get('topic', 'Unknown Topic')
        entries = guided_journal.get('entries', [])
        prompts = guided_journal.get('prompts', [])
    else:
        topic = guided_journal.topic
        entries = guided_journal.entries
        prompts = guided_journal.prompts

    # Title
    story.append(Paragraph(f"GuidedJournal: {topic}", styles['h1']))
    story.append(Spacer(1, 12))

    # Create prompt lookup for efficiency
    prompt_lookup = {}
    if isinstance(guided_journal, dict):
        for prompt in prompts:
            prompt_lookup[prompt.get('id')] = prompt.get('text', '')
    else:
        for prompt in prompts:
            prompt_lookup[prompt.id] = prompt.text

    # Entries
    for entry in entries:
        if isinstance(entry, dict):
            prompt_id = entry.get('prompt_id')
            response = entry.get('response', '')
            prompt_text = entry.get('prompt_text') or prompt_lookup.get(prompt_id, 'Unknown Prompt')
        else:
            prompt_text = entry.prompt.text if hasattr(entry, 'prompt') else prompt_lookup.get(entry.prompt_id, 'Unknown Prompt')
            response = entry.response
        
        story.append(Paragraph(f"Prompt: {prompt_text}", styles['h3']))
        story.append(Spacer(1, 6))
        story.append(Paragraph(response, styles['Normal']))
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
