#!/usr/bin/env python3
"""
Script optimisé pour analyser test.tex avec les meilleures API disponibles
Utilise Claude pour l'analyse scientifique, Gemini pour le style, OpenAI pour la synthèse
"""

import os, re, time, sys, json
from typing import Optional, List, Dict
from datetime import datetime
from pathlib import Path

# ===============================================================
# CONFIGURATION DES APIS
# ===============================================================

APIS_DISPONIBLES = {}

# --- OpenAI ---
try:
    from openai import OpenAI
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    APIS_DISPONIBLES["openai"] = True
    print("✅ OpenAI initialisé")
except Exception as e:
    APIS_DISPONIBLES["openai"] = False
    print(f"⚠️  OpenAI non disponible : {str(e)[:80]}")

# --- Claude ---
try:
    import anthropic
    claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    APIS_DISPONIBLES["claude"] = True
    print("✅ Claude initialisé")
except Exception as e:
    APIS_DISPONIBLES["claude"] = False
    print(f"⚠️  Claude non disponible : {str(e)[:80]}")

# --- Gemini ---
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    gemini_model = genai.GenerativeModel(model_name="gemini-1.5-pro")
    APIS_DISPONIBLES["gemini"] = True
    print("✅ Gemini initialisé")
except Exception as e:
    APIS_DISPONIBLES["gemini"] = False
    print(f"⚠️  Gemini non disponible : {str(e)[:80]}")

if not any(APIS_DISPONIBLES.values()):
    print("❌ Aucune API disponible !")
    sys.exit(1)

# ===============================================================
# APPEL UNIFIÉ AUX APIS
# ===============================================================

def appel_api(system_prompt: str, user_prompt: str, api: str = "claude",
              temperature: float = 0.3, max_tokens: int = 2000) -> Optional[str]:
    """Appel unifié aux APIs disponibles"""

    if not APIS_DISPONIBLES.get(api):
        print(f"⚠️  {api.upper()} non disponible, fallback...")
        for alt_api in ["claude", "gemini", "openai"]:
            if APIS_DISPONIBLES.get(alt_api):
                api = alt_api
                break

    try:
        if api == "claude":
            response = claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return response.content[0].text

        elif api == "gemini":
            response = gemini_model.generate_content(
                contents=f"{system_prompt}\n\n{user_prompt}",
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )
            return response.text

        elif api == "openai":
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Modèle plus rapide et moins cher
                temperature=temperature,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content

    except Exception as e:
        print(f"❌ Erreur {api.upper()} : {str(e)[:80]}")
        return None

    return None

# ===============================================================
# AGENTS SPÉCIALISÉS
# ===============================================================

def agent_scientifique(titre: str, texte: str) -> str:
    """Claude pour analyser la rigueur scientifique"""
    system = """Tu es un expert en validation scientifique et en méthodologie de recherche.
Analyse avec rigueur le texte fourni."""

    prompt = f"""Analyse du chapitre/section : {titre}

Évalue les aspects suivants :
1. Rigueur scientifique (théories, preuves, logique)
2. Pertinence des équations/concepts mathématiques
3. Cohérence des arguments
4. Exactitude des affirmations

Texte à analyser :
{texte[:3000]}

Fournis une analyse structurée et constructive."""

    return appel_api(system, prompt, api="claude", temperature=0.2) or "[Analyse scientifique indisponible]"

def agent_style(titre: str, texte: str) -> str:
    """Gemini pour analyser le style et la clarté"""
    system = """Tu es un relecteur académique expert en rédaction scientifique en français.
Analyse la qualité du style, la clarté et la pertinence du ton."""

    prompt = f"""Analyse stylistique du chapitre/section : {titre}

Évalue :
1. Clarté de l'expression (vocabulaire, construction de phrases)
2. Fluidité de la lecture
3. Cohérence du ton académique
4. Suggestions de correction/amélioration

Texte :
{texte[:3000]}

Sois constructif et pratique."""

    return appel_api(system, prompt, api="gemini", temperature=0.4) or "[Analyse stylistique indisponible]"

def agent_synthese(titre: str, contenu: str, analyses_precedentes: dict) -> str:
    """OpenAI pour la synthèse critique"""
    system = """Tu es un examinateur académique rédigeant un rapport de thèse.
Synthétise de manière concise et critique."""

    prompt = f"""Synthèse critique du chapitre : {titre}

Analyses précédentes :
- Rigueur scientifique: {analyses_precedentes.get('scientifique', '')[:500]}
- Style: {analyses_precedentes.get('style', '')[:500]}

Contenu à synthétiser :
{contenu[:2000]}

Propose une synthèse de 150-200 mots avec conclusions principales."""

    return appel_api(system, prompt, api="openai", temperature=0.3) or "[Synthèse indisponible]"

# ===============================================================
# UTILITAIRES
# ===============================================================

def lire_fichier_latex(path: str) -> str:
    """Lit un fichier LaTeX avec gestion des encodages"""
    for enc in ['utf-8', 'latin-1', 'cp1252']:
        try:
            with open(path, 'r', encoding=enc) as f:
                print(f"✅ Fichier lu ({enc})")
                return f.read()
        except Exception:
            pass
    print(f"❌ Impossible de lire {path}")
    return ""

def compter_mots(txt: str) -> int:
    """Compte les mots en supprimant les commandes LaTeX"""
    txt = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', txt)  # Commandes
    txt = re.sub(r'\\[a-zA-Z]+', '', txt)  # Commandes simples
    txt = re.sub(r'[\\{}$]', '', txt)  # Caractères spéciaux
    return len([w for w in txt.split() if w.strip()])

def extraire_sections(contenu: str, max_sections: int = 10) -> List[Dict]:
    """Extrait les sections du fichier LaTeX"""
    # Recherche des \chapter et \section
    pattern = re.compile(r'\\(chapter|section|subsection)\s*\{([^}]*)\}', re.IGNORECASE)
    matches = list(pattern.finditer(contenu))

    sections = []
    for i, match in enumerate(matches):
        if len(sections) >= max_sections:
            break

        niveau = match.group(1)
        titre = match.group(2).strip()

        # Ne prendre que chapter et section
        if niveau not in ["chapter", "section"]:
            continue

        start = match.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(contenu)

        texte = contenu[start:end]
        mots = compter_mots(texte)

        if mots >= 30:  # Minimum 30 mots
            sections.append({
                "type": niveau,
                "titre": titre,
                "texte": texte[:2500],  # Limiter
                "nb_mots": mots
            })

    return sections

# ===============================================================
# GÉNÉRATION HTML
# ===============================================================

def generer_rapport_html(resultats: List[Dict], temps_total: float, fichier_source: str) -> str:
    """Génère un rapport HTML professionnel"""

    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport d'Analyse - {fichier_source}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; background: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: 30px auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }}

        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; text-align: center; }}
        .header h1 {{ font-size: 2.2em; margin-bottom: 10px; }}
        .header p {{ font-size: 0.95em; opacity: 0.9; }}

        .meta {{ background: #f8f9fa; padding: 20px; border-bottom: 1px solid #ddd; display: flex; justify-content: space-between; font-size: 0.9em; }}

        .content {{ padding: 40px; }}
        .summary {{ background: #f8f9fa; border-left: 4px solid #667eea; padding: 15px; margin-bottom: 30px; border-radius: 4px; }}
        .summary strong {{ color: #667eea; }}

        .section {{ margin-bottom: 40px; padding-bottom: 30px; border-bottom: 1px solid #eee; }}
        .section:last-child {{ border-bottom: none; }}

        .section-title {{ font-size: 1.4em; color: #667eea; margin-bottom: 15px; display: flex; align-items: center; }}
        .section-icon {{ margin-right: 10px; font-size: 1.3em; }}

        .analysis-box {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 4px; border-left: 3px solid #764ba2; }}
        .analysis-box h4 {{ color: #764ba2; margin-bottom: 8px; font-size: 1em; }}
        .analysis-box p {{ line-height: 1.6; font-size: 0.95em; }}

        .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 20px; }}
        .stat-card {{ background: white; border: 1px solid #ddd; padding: 15px; border-radius: 4px; text-align: center; }}
        .stat-card .value {{ font-size: 1.8em; color: #667eea; font-weight: bold; }}
        .stat-card .label {{ color: #666; font-size: 0.9em; margin-top: 5px; }}

        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 0.85em; border-top: 1px solid #ddd; }}

        .badge {{ display: inline-block; background: #667eea; color: white; padding: 4px 8px; border-radius: 3px; font-size: 0.85em; margin-right: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Rapport d'Analyse Multi-Modèles IA</h1>
            <p>Analyse académique approfondie avec Claude, Gemini et OpenAI</p>
        </div>

        <div class="meta">
            <div>📄 Fichier : <strong>{fichier_source}</strong></div>
            <div>📅 Généré : {timestamp}</div>
            <div>⏱️  Durée : {temps_total:.1f}s</div>
        </div>

        <div class="content">
            <div class="summary">
                <strong>📋 Résumé :</strong> {len(resultats)} sections analysées avec trois modèles IA différents.
                Chaque section bénéficie d'une analyse scientifique, stylistique et d'une synthèse critique.
            </div>
"""

    # Ajouter chaque section
    for i, result in enumerate(resultats, 1):
        html += f"""
        <div class="section">
            <div class="section-title">
                <span class="section-icon">#{i}</span>
                {result['titre']}
            </div>
            <div class="badge">{result['type'].upper()}</div>
            <div class="badge">{result['nb_mots']} mots</div>

            <div class="analysis-box">
                <h4>🔬 Analyse Scientifique (Claude)</h4>
                <p>{result['scientifique'][:800]}...</p>
            </div>

            <div class="analysis-box">
                <h4>✏️  Analyse Stylistique (Gemini)</h4>
                <p>{result['style'][:800]}...</p>
            </div>

            <div class="analysis-box">
                <h4>🎯 Synthèse Critique (OpenAI)</h4>
                <p>{result['synthese'][:600]}...</p>
            </div>
        </div>
"""

    # Statistiques
    total_mots = sum(r['nb_mots'] for r in resultats)
    html += f"""
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
        </div>

        <div class="footer">
            <p>Rapport généré par l'Analyseur Multi-Modèles IA v3.2 | Claude 3.5 Sonnet + Gemini 1.5 + GPT-4o-mini</p>
        </div>
    </div>
</body>
</html>
"""
    return html

# ===============================================================
# FONCTION PRINCIPALE
# ===============================================================

def main():
    print("\n" + "="*60)
    print("🚀 ANALYSE DE test.tex AVEC MEILLEURES API")
    print("="*60)

    # Vérifier les APIs disponibles
    print("\n📡 APIs disponibles :")
    for api, disponible in APIS_DISPONIBLES.items():
        status = "✅" if disponible else "❌"
        print(f"  {status} {api.upper()}")

    # Lire le fichier
    print("\n📖 Lecture du fichier...")
    contenu = lire_fichier_latex("test.tex")
    if not contenu:
        print("❌ Impossible de lire test.tex")
        return

    # Extraire les sections
    print("\n🔍 Extraction des sections...")
    sections = extraire_sections(contenu, max_sections=5)  # Limiter à 5 pour tester
    if not sections:
        print("❌ Aucune section trouvée")
        return

    print(f"✅ {len(sections)} sections trouvées :")
    for s in sections:
        print(f"   - {s['titre']} ({s['nb_mots']} mots)")

    # Analyser chaque section
    print("\n⚙️  Analyse des sections...")
    debut = time.time()
    resultats = []

    for i, section in enumerate(sections, 1):
        print(f"\n[{i}/{len(sections)}] {section['titre']}")

        # Analyse scientifique (Claude)
        print("  → Analyse scientifique (Claude)...", end=" ", flush=True)
        sci = agent_scientifique(section['titre'], section['texte'])
        print("✅")

        # Analyse stylistique (Gemini)
        print("  → Analyse stylistique (Gemini)...", end=" ", flush=True)
        sty = agent_style(section['titre'], section['texte'])
        print("✅")

        # Synthèse (OpenAI)
        print("  → Synthèse critique (OpenAI)...", end=" ", flush=True)
        syn = agent_synthese(section['titre'], section['texte'],
                           {'scientifique': sci, 'style': sty})
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

    # Générer le rapport HTML
    print("\n📄 Génération du rapport HTML...")
    html = generer_rapport_html(resultats, temps_total, "test.tex")

    # Sauvegarder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"rapports/rapport_test_{timestamp}.html"

    Path("rapports").mkdir(exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n✅ Rapport généré : {output_file}")
    print(f"⏱️  Durée totale : {temps_total:.1f}s")
    print(f"📊 Sections analysées : {len(resultats)}")
    print(f"📈 Mots totaux : {sum(r['nb_mots'] for r in resultats)}")
    print("\n✨ Analyse complète !")

if __name__ == "__main__":
    main()
