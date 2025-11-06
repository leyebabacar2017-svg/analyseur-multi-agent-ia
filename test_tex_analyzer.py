#!/usr/bin/env python3
"""
Analyseur spécialisé pour test.tex
Utilise les API définies pour une analyse optimale
"""

import os, re, sys, json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import time

# ===============================================================
# IMPORTS DES APIS
# ===============================================================

print("📡 Initialisation des APIs...")

CLAUDE_AVAILABLE = False
GEMINI_AVAILABLE = False
OPENAI_AVAILABLE = False

try:
    import anthropic
    claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    CLAUDE_AVAILABLE = True
    print("✅ Claude disponible")
except:
    print("⚠️  Claude non disponible")

try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    gemini_model = genai.GenerativeModel(model_name="gemini-1.5-pro")
    GEMINI_AVAILABLE = True
    print("✅ Gemini disponible")
except:
    print("⚠️  Gemini non disponible")

try:
    from openai import OpenAI
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    OPENAI_AVAILABLE = True
    print("✅ OpenAI disponible")
except:
    print("⚠️  OpenAI non disponible")

if not any([CLAUDE_AVAILABLE, GEMINI_AVAILABLE, OPENAI_AVAILABLE]):
    print("❌ Aucune API disponible !")
    sys.exit(1)

# ===============================================================
# CONFIGURATION
# ===============================================================

FICHIER_SOURCE = "test.tex"
MAX_SECTIONS = 6  # Limiter pour test.tex

# ===============================================================
# APPELS API UNIFIÉS
# ===============================================================

def appel_api(system_prompt: str, user_prompt: str, api: str = "claude",
              temperature: float = 0.3, max_tokens: int = 1500) -> Optional[str]:
    """Appel unifié avec fallback automatique"""

    apis_preferees = {
        "claude": ["claude", "gemini", "openai"],
        "gemini": ["gemini", "claude", "openai"],
        "openai": ["openai", "gemini", "claude"]
    }

    priorite = apis_preferees.get(api, ["claude", "gemini", "openai"])

    for api_essai in priorite:
        if api_essai == "claude" and CLAUDE_AVAILABLE:
            try:
                response = claude_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                return response.content[0].text
            except Exception as e:
                print(f"  ⚠️  Claude échoué : {str(e)[:50]}")

        elif api_essai == "gemini" and GEMINI_AVAILABLE:
            try:
                response = gemini_model.generate_content(
                    contents=f"{system_prompt}\n\n{user_prompt}",
                    generation_config=genai.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens
                    )
                )
                return response.text
            except Exception as e:
                print(f"  ⚠️  Gemini échoué : {str(e)[:50]}")

        elif api_essai == "openai" and OPENAI_AVAILABLE:
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    temperature=temperature,
                    max_tokens=max_tokens,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"  ⚠️  OpenAI échoué : {str(e)[:50]}")

    return "[Erreur : aucune API disponible]"

# ===============================================================
# AGENTS SPÉCIALISÉS
# ===============================================================

def agent_scientifique(titre: str, texte: str) -> str:
    """Analyse scientifique avec Claude"""
    system = """Tu es un expert en analyse scientifique et en méthodologie de recherche.
Fournis une analyse critique concise et constructive."""

    prompt = f"""Analyse scientifique du chapitre/section : {titre}

Évalue (brièvement) :
1. Rigueur mathématique et scientifique
2. Cohérence logique
3. Validité des affirmations

Texte :
{texte[:2000]}

Réponse concise (150 mots max)."""

    return appel_api(system, prompt, api="claude", temperature=0.2)

def agent_style(titre: str, texte: str) -> str:
    """Analyse stylistique avec Gemini"""
    system = """Tu es un relecteur académique expert en rédaction scientifique française.
Analyse la qualité du texte et propose des améliorations."""

    prompt = f"""Analyse stylistique : {titre}

Évalue :
1. Clarté et fluidité de lecture
2. Vocabulaire académique
3. Suggestions d'amélioration (2-3 max)

Texte :
{texte[:2000]}

Réponse concise (150 mots max)."""

    return appel_api(system, prompt, api="gemini", temperature=0.35)

def agent_synthese(titre: str, texte: str) -> str:
    """Synthèse critique avec OpenAI"""
    system = """Tu es un examinateur académique rédigeant un rapport critique.
Synthétise les points clés de manière concise."""

    prompt = f"""Synthèse critique : {titre}

Résume en 100-150 mots :
- Points clés du contenu
- Forces de la section
- Points à améliorer

Texte :
{texte[:2000]}"""

    return appel_api(system, prompt, api="openai", temperature=0.3)

# ===============================================================
# UTILITAIRES LATEX
# ===============================================================

def lire_fichier_latex(path: str) -> str:
    """Lit un fichier LaTeX"""
    for enc in ['utf-8', 'latin-1', 'cp1252']:
        try:
            with open(path, 'r', encoding=enc) as f:
                return f.read()
        except:
            pass
    return ""

def compter_mots(txt: str) -> int:
    """Compte les mots sans les commandes LaTeX"""
    txt = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', txt)
    txt = re.sub(r'\\[a-zA-Z]+', '', txt)
    txt = re.sub(r'[\\{}$]', '', txt)
    return len([w for w in txt.split() if w.strip()])

def extraire_sections(contenu: str) -> List[Dict]:
    """Extrait les sections du fichier"""
    pattern = re.compile(r'\\(chapter|section)\s*\{([^}]*)\}', re.IGNORECASE)
    matches = list(pattern.finditer(contenu))

    sections = []
    for i, match in enumerate(matches):
        if len(sections) >= MAX_SECTIONS:
            break

        niveau = match.group(1)
        titre = match.group(2).strip()

        start = match.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(contenu)

        texte = contenu[start:end]
        mots = compter_mots(texte)

        if mots >= 30:
            sections.append({
                "type": niveau,
                "titre": titre,
                "texte": texte[:2500],
                "nb_mots": mots
            })

    return sections

# ===============================================================
# GÉNÉRATION DU RAPPORT
# ===============================================================

def generer_html(resultats: List[Dict], temps_total: float) -> str:
    """Génère un rapport HTML"""

    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    total_mots = sum(r['nb_mots'] for r in resultats)

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analyse test.tex</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; background: #f5f5f5; }}
        .container {{ max-width: 1100px; margin: 30px auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}

        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; text-align: center; }}
        .header h1 {{ font-size: 2.2em; margin-bottom: 10px; }}
        .header p {{ font-size: 0.95em; opacity: 0.9; }}

        .meta {{ background: #f8f9fa; padding: 20px; border-bottom: 1px solid #ddd; display: flex; justify-content: space-around; font-size: 0.9em; text-align: center; }}

        .content {{ padding: 40px; }}

        .section {{ margin-bottom: 40px; padding-bottom: 30px; border-bottom: 1px solid #eee; }}
        .section:last-child {{ border-bottom: none; }}

        .section-header {{ font-size: 1.4em; color: #667eea; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #667eea; }}
        .section-info {{ color: #666; font-size: 0.9em; margin-bottom: 15px; }}

        .analysis {{ background: #f8f9fa; padding: 15px; margin: 15px 0; border-radius: 4px; border-left: 4px solid #764ba2; }}
        .analysis h4 {{ color: #764ba2; margin-bottom: 8px; font-size: 1em; }}
        .analysis p {{ line-height: 1.6; font-size: 0.95em; }}

        .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 30px 0; }}
        .stat-card {{ background: #f8f9fa; border: 1px solid #ddd; padding: 20px; border-radius: 4px; text-align: center; }}
        .stat-card .value {{ font-size: 2em; color: #667eea; font-weight: bold; }}
        .stat-card .label {{ color: #666; font-size: 0.9em; margin-top: 5px; }}

        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 0.85em; border-top: 1px solid #ddd; }}

        .badge {{ display: inline-block; background: #667eea; color: white; padding: 4px 8px; border-radius: 3px; font-size: 0.85em; margin-right: 8px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Analyse de test.tex</h1>
            <p>Rapport d'analyse multi-modèles IA - Claude, Gemini, OpenAI</p>
        </div>

        <div class="meta">
            <div>📄 <strong>{FICHIER_SOURCE}</strong></div>
            <div>📅 {timestamp}</div>
            <div>⏱️  {temps_total:.1f}s</div>
            <div>📈 {total_mots:,} mots</div>
        </div>

        <div class="content">
            <div class="stats">
                <div class="stat-card">
                    <div class="value">{len(resultats)}</div>
                    <div class="label">Sections analysées</div>
                </div>
                <div class="stat-card">
                    <div class="value">{total_mots:,}</div>
                    <div class="label">Mots totaux</div>
                </div>
                <div class="stat-card">
                    <div class="value">{temps_total:.1f}s</div>
                    <div class="label">Durée totale</div>
                </div>
            </div>
"""

    for i, result in enumerate(resultats, 1):
        html += f"""
        <div class="section">
            <div class="section-header">
                #{i} {result['titre']}
            </div>
            <div class="section-info">
                <span class="badge">{result['type'].upper()}</span>
                <span class="badge">{result['nb_mots']} mots</span>
            </div>

            <div class="analysis">
                <h4>🔬 Analyse Scientifique (Claude)</h4>
                <p>{result['scientifique']}</p>
            </div>

            <div class="analysis">
                <h4>✏️  Analyse Stylistique (Gemini)</h4>
                <p>{result['style']}</p>
            </div>

            <div class="analysis">
                <h4>🎯 Synthèse Critique (OpenAI)</h4>
                <p>{result['synthese']}</p>
            </div>
        </div>
"""

    html += f"""
        </div>

        <div class="footer">
            <p>Rapport généré par l'Analyseur test.tex | Claude 3.5 + Gemini 1.5 + GPT-4o-mini</p>
            <p>Généré le {timestamp}</p>
        </div>
    </div>
</body>
</html>
"""
    return html

# ===============================================================
# MAIN
# ===============================================================

def main():
    print("\n" + "="*60)
    print("🚀 ANALYSE DE test.tex")
    print("="*60)

    # Vérifier le fichier
    if not os.path.exists(FICHIER_SOURCE):
        print(f"❌ {FICHIER_SOURCE} non trouvé")
        return

    # Lire et extraire
    print(f"\n📖 Lecture de {FICHIER_SOURCE}...")
    contenu = lire_fichier_latex(FICHIER_SOURCE)
    if not contenu:
        print("❌ Impossible de lire le fichier")
        return

    print("🔍 Extraction des sections...")
    sections = extraire_sections(contenu)
    if not sections:
        print("❌ Aucune section trouvée")
        return

    print(f"✅ {len(sections)} sections trouvées")

    # Analyser
    print("\n⚙️  Analyse en cours...\n")
    debut = time.time()
    resultats = []

    for i, section in enumerate(sections, 1):
        print(f"[{i}/{len(sections)}] {section['titre']}")

        print("  → Analyse scientifique (Claude)...", end=" ", flush=True)
        sci = agent_scientifique(section['titre'], section['texte'])
        print("✅")

        print("  → Analyse stylistique (Gemini)...", end=" ", flush=True)
        sty = agent_style(section['titre'], section['texte'])
        print("✅")

        print("  → Synthèse critique (OpenAI)...", end=" ", flush=True)
        syn = agent_synthese(section['titre'], section['texte'])
        print("✅")

        resultats.append({
            'titre': section['titre'],
            'type': section['type'],
            'nb_mots': section['nb_mots'],
            'scientifique': sci,
            'style': sty,
            'synthese': syn
        })

    temps_total = time.time() - debut

    # Sauvegarder
    print(f"\n📄 Génération du rapport...")
    Path("rapports").mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_file = f"rapports/rapport_test_{timestamp}.html"

    html = generer_html(resultats, temps_total)
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)

    # Résumé
    print(f"\n✨ Analyse complète !")
    print(f"📄 Rapport HTML : {html_file}")
    print(f"⏱️  Durée : {temps_total:.1f}s")
    print(f"📊 Sections : {len(resultats)}")
    print(f"📈 Mots : {sum(r['nb_mots'] for r in resultats):,}")

if __name__ == "__main__":
    main()
