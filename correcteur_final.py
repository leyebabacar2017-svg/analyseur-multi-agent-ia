#!/usr/bin/env python3
"""
Correcteur IA Académique - Version Finale (OpenAI compatible)
Sans dépendances externes, utilise urllib (stdlib)
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
CLAUDE_MODEL = "claude-opus-4-1"  # Corrigé (le modèle 3.5-sonnet n'était pas disponible)
GEMINI_MODEL = "gemini-2.0-flash"

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
        "max_tokens": 2000,
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

    # Nettoyer la clé (enlever espaces/newlines)
    api_key = ANTHROPIC_API_KEY.strip()

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }

    data = {
        "model": CLAUDE_MODEL,
        "max_tokens": 2000,
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

    # Combiner system + user message
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
            "maxOutputTokens": 2000
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
    # Ordre de fallback: préféré → alternance → dernier recours
    available_models = []
    if OPENAI_API_KEY:
        available_models.append("openai")
    if GEMINI_API_KEY:
        available_models.append("gemini")
    if ANTHROPIC_API_KEY:
        available_models.append("claude")

    # Commencer par le modèle préféré
    if prefer_model in available_models:
        available_models.remove(prefer_model)
    models = [prefer_model] + available_models

    for model in models:
        for attempt in range(2):  # 2 tentatives par modèle
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
# AGENTS
# ===============================================================

def agent_scientifique(txt: str) -> str:
    """Analyse scientifique"""
    system = """Tu es un expert en mathématiques et modélisation scientifique.
Analyse la rigueur scientifique du texte. Sois concis (100-150 mots)."""
    prompt = f"Analyser ce texte:\n\n{txt[:2000]}"
    result = safe_call(system, prompt, "openai")
    return result or "❌ Analyse indisponible"

def agent_style(txt: str) -> str:
    """Amélioration de style"""
    system = """Tu es un relecteur académique spécialisé en rédaction scientifique.
Améliore le style et la clarté. Sois concis (100-150 mots)."""
    prompt = f"Analyser ce texte:\n\n{txt[:2000]}"
    result = safe_call(system, prompt, "openai")
    return result or "❌ Amélioration indisponible"

def agent_synthese(titre: str, analyses: list) -> str:
    """Synthèse finale"""
    system = """Tu es un examinateur rédigeant une synthèse critique.
Synthétise les points clés en 80-100 mots."""
    prompt = f"Chapitre: {titre}\n\nAnalyses:\n" + "\n\n".join(analyses)
    result = safe_call(system, prompt, "openai")
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

        # Compter les mots
        mots = len(re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', texte).split())

        if mots > 10:
            chapitres.append({
                "titre": titre,
                "texte": texte[:2000],
                "mots": mots
            })

    return chapitres

def generer_html(analyses: list, temps_total: float) -> str:
    """Générer rapport HTML"""
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Rapport d'Analyse</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #1f4788; border-bottom: 3px solid #1f4788; padding-bottom: 15px; }}
        h2 {{ color: #2e5c8a; margin-top: 30px; }}
        .meta {{ background: #e8f0f7; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .chapter {{ background: #f9f9f9; padding: 20px; margin: 20px 0; border-left: 4px solid #2e5c8a; border-radius: 5px; }}
        .analysis {{ margin: 15px 0; padding: 15px; background: white; border-left: 3px solid #667eea; }}
        .analysis-title {{ color: #667eea; font-weight: bold; margin-bottom: 10px; }}
        .analysis-text {{ color: #555; line-height: 1.6; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Rapport d'Analyse Académique</h1>
        <div class="meta">
            <p><strong>Date:</strong> {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
            <p><strong>Chapitres analysés:</strong> {len(analyses)}</p>
            <p><strong>Temps total:</strong> {temps_total:.1f}s</p>
        </div>

        <h2>Détails des Analyses</h2>
"""

    for i, ch in enumerate(analyses, 1):
        html += f"""
        <div class="chapter">
            <h3>{i}. {ch['titre']}</h3>
            <div class="analysis">
                <div class="analysis-title">✓ Rigueur Scientifique</div>
                <div class="analysis-text">{ch['scientifique'][:400]}...</div>
            </div>
            <div class="analysis">
                <div class="analysis-title">✓ Style et Clarté</div>
                <div class="analysis-text">{ch['style'][:400]}...</div>
            </div>
            <div class="analysis">
                <div class="analysis-title">✓ Synthèse</div>
                <div class="analysis-text">{ch['synthese'][:400]}...</div>
            </div>
        </div>
"""

    html += """
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
    print("🤖 CORRECTEUR IA ACADÉMIQUE - VERSION FINALE")
    print("=" * 70)

    # Vérifier les APIs
    print("\n📋 APIs disponibles:")
    print(f"  {'✅' if OPENAI_API_KEY else '❌'} OpenAI (gpt-4o)")
    print(f"  {'✅' if GEMINI_API_KEY else '❌'} Gemini (gemini-2.0-flash)")
    print(f"  {'✅' if ANTHROPIC_API_KEY else '❌'} Claude (claude-3-5-sonnet)")

    if not OPENAI_API_KEY and not ANTHROPIC_API_KEY and not GEMINI_API_KEY:
        print("\n❌ Aucune API configurée!")
        print("Configurez au minimum une clé:")
        print("   export OPENAI_API_KEY='sk-...'")
        print("   ou export ANTHROPIC_API_KEY='sk-ant-...'")
        print("   ou export GEMINI_API_KEY='AIza-...'")
        exit(1)

    # Fichier
    fichier = input("\n📄 Fichier .tex à analyser: ").strip()
    if not os.path.exists(fichier):
        print(f"❌ Fichier introuvable: {fichier}")
        exit(1)

    # Analyser
    print("\n🔍 Extraction des chapitres...")
    contenu = lire_latex(fichier)
    chapitres = extraire_chapitres(contenu, max_chapitres=5)

    if not chapitres:
        print("❌ Aucun chapitre trouvé dans le fichier")
        exit(1)

    print(f"✅ {len(chapitres)} chapitres détectés\n")

    # Analyser chaque chapitre
    debut = time.time()
    resultats = []

    for i, ch in enumerate(chapitres, 1):
        print(f"🔎 {i}/{len(chapitres)}: {ch['titre'][:40]}...", end="", flush=True)

        sci = agent_scientifique(ch["texte"])
        sty = agent_style(ch["texte"])
        syn = agent_synthese(ch["titre"], [sci, sty])

        resultats.append({
            "titre": ch["titre"],
            "scientifique": sci,
            "style": sty,
            "synthese": syn
        })

        print(" ✅")

    temps_total = time.time() - debut

    # Générer rapports
    print("\n📊 Génération des rapports...")
    Path("rapports").mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # HTML
    html = generer_html(resultats, temps_total)
    html_path = f"rapports/rapport_final_{timestamp}.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ HTML: {html_path}")

    # JSON
    json_path = f"rapports/rapport_final_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            "metadata": {
                "date": datetime.now().isoformat(),
                "fichier": fichier,
                "chapitres": len(resultats)
            },
            "analyses": resultats,
            "stats": {
                "temps_secondes": temps_total,
                "temps_minutes": round(temps_total / 60, 1)
            }
        }, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON: {json_path}")

    print(f"\n⏱️ Temps total: {temps_total:.1f}s ({round(temps_total/60, 1)}min)")
    print("✨ Analyse terminée avec succès!")
