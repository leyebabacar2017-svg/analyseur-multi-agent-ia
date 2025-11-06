#!/usr/bin/env python3
"""
Convertisseur HTML → PDF simple
Essaie weasyprint, sinon reportlab en fallback
"""

import sys
import os
from pathlib import Path

def convert_html_to_pdf(html_file, pdf_file):
    """Convertit un fichier HTML en PDF"""

    if not os.path.exists(html_file):
        print(f"❌ Fichier HTML introuvable : {html_file}")
        return False

    # Essai 1: WeasyPrint (meilleur rendu)
    try:
        from weasyprint import HTML, CSS
        print(f"📦 Utilisation de WeasyPrint...")
        HTML(html_file).write_pdf(pdf_file)
        print(f"✅ PDF généré : {pdf_file}")
        return True
    except ImportError:
        print("⚠️ WeasyPrint non disponible")
    except Exception as e:
        print(f"⚠️ WeasyPrint échoué : {e}")

    # Essai 2: ReportLab (basique mais fiable)
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet
        from html.parser import HTMLParser
        import re

        print(f"📦 Utilisation de ReportLab...")

        # Lire le HTML
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Extraire le texte (simplifié)
        # Enlever les balises HTML
        text = re.sub(r'<[^>]+>', '', html_content)
        text = re.sub(r'&nbsp;', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        # Créer le PDF
        doc = SimpleDocTemplate(pdf_file, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [Paragraph(text, styles['BodyText'])]

        doc.build(story)
        print(f"✅ PDF généré (version simplifiée) : {pdf_file}")
        return True

    except ImportError:
        print("⚠️ ReportLab non disponible")
    except Exception as e:
        print(f"⚠️ ReportLab échoué : {e}")

    print("\n💡 Solutions :")
    print("  1. Installer weasyprint : pip install weasyprint")
    print("  2. Ouvrir le HTML dans un navigateur et exporter en PDF")
    print("  3. Utiliser : wkhtmltopdf rapport.html rapport.pdf")
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 converter_html_to_pdf.py <fichier.html> [output.pdf]")
        sys.exit(1)

    html_file = sys.argv[1]
    pdf_file = sys.argv[2] if len(sys.argv) > 2 else html_file.replace('.html', '.pdf')

    convert_html_to_pdf(html_file, pdf_file)
