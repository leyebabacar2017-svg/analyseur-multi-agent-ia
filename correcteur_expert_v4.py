#!/usr/bin/env python3
"""
Correcteur IA Académique EXPERT - v4.0
Intègre un prompt d'évaluation scientifique de niveau expert (équivalent GPT-5)
Analyse multidimensionnelle : rigueur scientifique, logique, style, critique
"""

import os
import json
import re
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# ===============================================================
# CONFIGURATION
# ===============================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

OPENAI_MODEL = "gpt-4o"
CLAUDE_MODEL = "claude-opus-4-1"
GEMINI_MODEL = "gemini-2.0-flash"

# ===============================================================
# PROMPT EXPERT (GPT-5 equivalent)
# ===============================================================

PROMPT_EXPERT = """Tu es un évaluateur scientifique de niveau expert, doté des capacités d'analyse d'un modèle de génération avancé (équivalent GPT-5).
Ton rôle est d'examiner un texte académique avec une profondeur multidimensionnelle : rigueur scientifique, cohérence logique, clarté rédactionnelle, originalité, et pertinence du raisonnement.

### Objectif :
Produire une analyse complète et nuancée du texte fourni, en formulant des remarques constructives, structurées et hiérarchisées.

### Structure attendue de ta réponse :

1️⃣ **Analyse conceptuelle et scientifique**
- Vérifie la cohérence des définitions, notations et formulations mathématiques.
- Identifie les failles théoriques, oublis de justification, ou erreurs symboliques.
- Évalue la pertinence des équations, hypothèses et démonstrations.
- Compare implicitement avec les standards académiques du domaine.

2️⃣ **Analyse logique et méthodologique**
- Évalue la progression des idées (est-elle déductive, inductive, ou descriptive ?).
- Vérifie la cohérence entre les hypothèses, la méthodologie et les conclusions.
- Repère les manques de transitions, de liens entre les sections, ou de justification.

3️⃣ **Analyse stylistique et linguistique**
- Juge la clarté du discours, la fluidité des phrases et la qualité de la rédaction scientifique.
- Détecte les redondances, lourdeurs, imprécisions ou tournures maladroites.
- Propose des reformulations élégantes, précises et naturelles (niveau universitaire ou thèse).

4️⃣ **Appréciation critique globale**
- Dégage les forces du texte (originalité, cohérence, rigueur, lisibilité).
- Souligne les points faibles à améliorer (approfondissement, structure, argumentation).
- Suggère des pistes d'amélioration concrètes : ajout d'exemples, meilleure articulation théorie-pratique, clarification d'équations, etc.

5️⃣ **Évaluation synthétique**
- Termine par une appréciation globale en 3 lignes : *clarté, profondeur scientifique, cohérence argumentative*.
- Utilise des symboles pour la lisibilité : ✅ bon / ⚠️ moyen / ❌ faible.

### Consignes générales :
- Ne reformule pas tout le texte, analyse-le.
- Conserve un ton professionnel, neutre et académique.
- Sois précis, argumenté et non superficiel.
- Si le texte est trop court, signale les limites analytiques.
- Si des équations sont présentes, évalue leur validité et leur intégration dans le raisonnement."""

# ===============================================================
# APPELS API
# ===============================================================

def call_openai(system: str, user_msg: str, temperature: float = 0.3) -> str:
    """Appel OpenAI API via urllib"""
    if not OPENAI_API_KEY:
        return None

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": OPENAI_MODEL,
        "max_tokens": 3000,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg}
        ]
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            if "choices" in result and result["choices"]:
                return result["choices"][0]["message"]["content"]
    except Exception as e:
        return None

    return None

def call_claude(system: str, user_msg: str, temperature: float = 0.3) -> str:
    """Appel Claude API via urllib"""
    if not ANTHROPIC_API_KEY:
        return None

    api_key = ANTHROPIC_API_KEY.strip()

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }

    data = {
        "model": CLAUDE_MODEL,
        "max_tokens": 3000,
        "temperature": temperature,
        "system": system,
        "messages": [
            {"role": "user", "content": user_msg}
        ]
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            if "content" in result and result["content"]:
                return result["content"][0]["text"]
    except Exception as e:
        return None

    return None

def call_gemini(system: str, user_msg: str, temperature: float = 0.3) -> str:
    """Appel Gemini API via urllib"""
    if not GEMINI_API_KEY:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }

    full_prompt = f"{system}\n\n{user_msg}"

    data = {
        "contents": [
            {
                "parts": [
                    {"text": full_prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": 3000
        }
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            if "candidates" in result and result["candidates"]:
                return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return None

    return None

def safe_call(system: str, prompt: str, prefer_model: str = "openai") -> str:
    """Appel sécurisé avec fallback automatique"""
    available_models = []
    if OPENAI_API_KEY:
        available_models.append("openai")
    if GEMINI_API_KEY:
        available_models.append("gemini")
    if ANTHROPIC_API_KEY:
        available_models.append("claude")

    if prefer_model in available_models:
        available_models.remove(prefer_model)
    models = [prefer_model] + available_models

    for model in models:
        for attempt in range(2):
            if model == "openai":
                response = call_openai(system, prompt)
            elif model == "gemini":
                response = call_gemini(system, prompt)
            elif model == "claude":
                response = call_claude(system, prompt)
            else:
                response = None

            if response:
                return response
            if attempt == 0:
                time.sleep(1)

    return None

# ===============================================================
# AGENTS EXPERT
# ===============================================================

def agent_evaluation_expert(txt: str, titre_section: str) -> str:
    """Évaluation expert multidimensionnelle du texte (prompt GPT-5)"""
    prompt = f"""Analyse cette section académique avec la profondeur d'un expert :

TITRE DE LA SECTION : {titre_section}

TEXTE À ANALYSER :
---
{txt[:3000]}
---

Procède à une analyse structurée selon les 5 dimensions demandées."""

    result = safe_call(PROMPT_EXPERT, prompt, "openai")
    return result or "❌ Évaluation indisponible"

def agent_scientifique(txt: str) -> str:
    """Analyse rapide : rigueur scientifique"""
    system = """Tu es un expert en sciences académiques.
Analyse UNIQUEMENT la rigueur scientifique du texte en 100-150 mots.
Sois direct et précis."""
    prompt = f"Texte à analyser:\n\n{txt[:2000]}"
    result = safe_call(system, prompt, "claude")
    return result or "❌ Analyse indisponible"

def agent_style(txt: str) -> str:
    """Analyse rapide : style et clarté"""
    system = """Tu es un relecteur académique spécialisé en rédaction scientifique.
Analyse UNIQUEMENT le style et la clarté en 100-150 mots.
Propose des reformulations si nécessaire."""
    prompt = f"Texte à analyser:\n\n{txt[:2000]}"
    result = safe_call(system, prompt, "gemini")
    return result or "❌ Amélioration indisponible"

def agent_synthese(titre: str, txt: str) -> str:
    """Synthèse critique"""
    system = """Tu es un examinateur expert rédigeant une synthèse critique.
Résume les points clés et critiques en 80-100 mots."""
    prompt = f"Section: {titre}\n\nTexte:\n{txt[:2000]}"
    result = safe_call(system, prompt, "claude")
    return result or "❌ Synthèse indisponible"

# ===============================================================
# UTILITAIRES
# ===============================================================

def lire_latex(fichier: str) -> str:
    """Lire un fichier LaTeX avec support encodage"""
    for enc in ['utf-8', 'latin-1', 'cp1252']:
        try:
            with open(fichier, 'r', encoding=enc) as f:
                return f.read()
        except:
            continue
    return ""

def extraire_chapitres(content: str, max_chapitres: int = 5) -> list:
    """Extraire les chapitres du fichier LaTeX"""
    pattern = re.compile(r'\\chapter\{([^}]+)\}(.*?)(?=\\chapter|\\end\{document\}|$)', re.DOTALL)
    matches = list(pattern.finditer(content))[:max_chapitres]

    chapitres = []
    for match in matches:
        titre = match.group(1).strip()
        texte = match.group(2).strip()
        mots = len(re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', texte).split())

        if mots > 10:
            chapitres.append({
                "titre": titre,
                "texte": texte[:3000],
                "mots": mots
            })

    return chapitres

def generer_html(analyses: list, temps_total: float) -> str:
    """Générer rapport HTML avec analyses expert"""
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Rapport d'Analyse Expert</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #1f4788; border-bottom: 4px solid #1f4788; padding-bottom: 15px; font-size: 2.2em; }}
        h2 {{ color: #2e5c8a; margin-top: 40px; border-bottom: 2px solid #2e5c8a; padding-bottom: 10px; }}
        h3 {{ color: #3e6fa6; margin-top: 30px; font-size: 1.1em; }}
        .meta {{ background: #e8f0f7; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #1f4788; }}
        .chapter {{ background: #f9f9f9; padding: 25px; margin: 25px 0; border-left: 5px solid #2e5c8a; border-radius: 5px; }}
        .expert-analysis {{ background: #fff9e6; padding: 20px; margin: 15px 0; border-left: 4px solid #ff9800; border-radius: 4px; }}
        .expert-title {{ color: #ff9800; font-weight: bold; margin-bottom: 10px; font-size: 1.05em; }}
        .section-title {{ color: #667eea; font-weight: bold; margin-top: 15px; margin-bottom: 8px; }}
        .analysis-text {{ color: #555; line-height: 1.8; margin: 10px 0; font-size: 0.95em; }}
        .footer {{ margin-top: 50px; padding-top: 20px; border-top: 2px solid #e8f0f7; text-align: center; color: #999; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Rapport d'Analyse Académique EXPERT</h1>
        <div class="meta">
            <p><strong>Date:</strong> {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
            <p><strong>Chapitres analysés:</strong> {len(analyses)}</p>
            <p><strong>Temps total:</strong> {temps_total:.1f}s</p>
            <p><strong>Mode:</strong> Évaluation Expert GPT-5 (5 dimensions)</p>
        </div>

        <h2>Détails des Analyses Expertes</h2>
"""

    for i, ch in enumerate(analyses, 1):
        html += f"""
        <div class="chapter">
            <h3>Chapitre {i}: {ch['titre']}</h3>

            <div class="expert-analysis">
                <div class="expert-title">🎯 ÉVALUATION EXPERT MULTIDIMENSIONNELLE</div>
                <div class="analysis-text">{ch['expert']}</div>
            </div>

            <div class="expert-analysis" style="background: #f0f7ff; border-left-color: #2196F3;">
                <div class="section-title">✓ Rigueur Scientifique</div>
                <div class="analysis-text">{ch['scientifique'][:500]}...</div>
            </div>

            <div class="expert-analysis" style="background: #f0f7ff; border-left-color: #2196F3;">
                <div class="section-title">✓ Style et Clarté</div>
                <div class="analysis-text">{ch['style'][:500]}...</div>
            </div>

            <div class="expert-analysis" style="background: #f0f7ff; border-left-color: #2196F3;">
                <div class="section-title">✓ Synthèse Critique</div>
                <div class="analysis-text">{ch['synthese'][:500]}...</div>
            </div>
        </div>
"""

    html += f"""
        <div class="footer">
            <p>Rapport généré le {datetime.now().strftime("%d/%m/%Y à %H:%M:%S")}</p>
            <p>Correcteur IA Académique EXPERT v4.0 - Évaluation multidimensionnelle</p>
        </div>
    </div>
</body>
</html>
"""
    return html

# ===============================================================
# MAIN
# ===============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🤖 CORRECTEUR IA ACADÉMIQUE EXPERT - v4.0")
    print("Évaluation multidimensionnelle (5 dimensions)")
    print("=" * 70)

    print("\n📋 APIs disponibles:")
    print(f"  {'✅' if OPENAI_API_KEY else '❌'} OpenAI (gpt-4o)")
    print(f"  {'✅' if GEMINI_API_KEY else '❌'} Gemini (gemini-2.0-flash)")
    print(f"  {'✅' if ANTHROPIC_API_KEY else '❌'} Claude (claude-opus-4-1)")

    if not OPENAI_API_KEY and not ANTHROPIC_API_KEY and not GEMINI_API_KEY:
        print("\n❌ Aucune API configurée!")
        exit(1)

    fichier = input("\n📄 Fichier .tex à analyser: ").strip()
    if not os.path.exists(fichier):
        print(f"❌ Fichier introuvable: {fichier}")
        exit(1)

    print("\n🔍 Extraction des chapitres...")
    contenu = lire_latex(fichier)
    chapitres = extraire_chapitres(contenu, max_chapitres=5)

    if not chapitres:
        print("❌ Aucun chapitre trouvé")
        exit(1)

    print(f"✅ {len(chapitres)} chapitres détectés\n")

    debut = time.time()
    resultats = []

    for i, ch in enumerate(chapitres, 1):
        print(f"🔎 {i}/{len(chapitres)}: {ch['titre'][:40]}...", end="", flush=True)

        # Évaluation EXPERT (multidimensionnelle)
        print(" [EXPERT]", end="", flush=True)
        expert = agent_evaluation_expert(ch["texte"], ch["titre"])

        # Analyses rapides (pour comparaison)
        sci = agent_scientifique(ch["texte"])
        sty = agent_style(ch["texte"])
        syn = agent_synthese(ch["titre"], ch["texte"])

        resultats.append({
            "titre": ch["titre"],
            "expert": expert,
            "scientifique": sci,
            "style": sty,
            "synthese": syn
        })

        print(" ✅")

    temps_total = time.time() - debut

    print("\n📊 Génération des rapports...")
    Path("rapports").mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # HTML
    html = generer_html(resultats, temps_total)
    html_path = f"rapports/rapport_expert_{timestamp}.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ HTML: {html_path}")

    # JSON
    json_path = f"rapports/rapport_expert_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            "metadata": {
                "date": datetime.now().isoformat(),
                "fichier": fichier,
                "chapitres": len(resultats),
                "mode": "EXPERT_MULTIDIMENSIONNEL"
            },
            "analyses": resultats,
            "stats": {
                "temps_secondes": temps_total,
                "temps_minutes": round(temps_total / 60, 1)
            }
        }, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON: {json_path}")

    print(f"\n⏱️ Temps total: {temps_total:.1f}s ({round(temps_total/60, 1)}min)")
    print("✨ Analyse EXPERT terminée!")
