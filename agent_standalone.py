#!/usr/bin/env python3
"""
Version Standalone du Correcteur IA (sans dépendances pip)
Utilise les APIs via HTTP directement
"""

import os
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path

# ===============================================================
# CONFIGURATION
# ===============================================================

APIS = {
    "claude": {
        "key_env": "ANTHROPIC_API_KEY",
        "model": "claude-3-5-sonnet-20241022",
        "available": bool(os.getenv("ANTHROPIC_API_KEY"))
    },
    "openai": {
        "key_env": "OPENAI_API_KEY",
        "model": "gpt-4o",
        "available": bool(os.getenv("OPENAI_API_KEY"))
    },
    "gemini": {
        "key_env": "GEMINI_API_KEY",
        "model": "gemini-2.0-flash",
        "available": bool(os.getenv("GEMINI_API_KEY"))
    }
}

# ===============================================================
# APPELS API VIA CURL
# ===============================================================

def call_claude(system: str, user_prompt: str) -> str:
    """Appel Claude via curl"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    data = {
        "model": APIS["claude"]["model"],
        "max_tokens": 2000,
        "temperature": 0.3,
        "system": system,
        "messages": [{"role": "user", "content": user_prompt}]
    }

    cmd = f"""curl -s -X POST https://api.anthropic.com/v1/messages \
        -H "x-api-key: {api_key}" \
        -H "anthropic-version: 2023-06-01" \
        -H "content-type: application/json" \
        -d '{json.dumps(data)}'"""

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        response = json.loads(result.stdout)

        if "content" in response and response["content"]:
            return response["content"][0]["text"]
        else:
            error = response.get("error", {}).get("message", "Erreur inconnue")
            print(f"  ⚠️ Claude API error: {error}")
            return None
    except Exception as e:
        print(f"  ⚠️ Erreur Claude: {e}")
        return None

def call_openai(system: str, user_prompt: str) -> str:
    """Appel OpenAI via curl"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    data = {
        "model": APIS["openai"]["model"],
        "max_tokens": 2000,
        "temperature": 0.3,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt}
        ]
    }

    cmd = f"""curl -s -X POST https://api.openai.com/v1/chat/completions \
        -H "Authorization: Bearer {api_key}" \
        -H "content-type: application/json" \
        -d '{json.dumps(data)}'"""

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        response = json.loads(result.stdout)

        if "choices" in response and response["choices"]:
            return response["choices"][0]["message"]["content"]
        else:
            error = response.get("error", {}).get("message", "Erreur inconnue")
            print(f"  ⚠️ OpenAI API error: {error}")
            return None
    except Exception as e:
        print(f"  ⚠️ Erreur OpenAI: {e}")
        return None

def safe_call(system: str, user_prompt: str, model: str = "claude", attempt: int = 0) -> str:
    """Appel sécurisé avec fallback"""
    max_attempts = 3

    if attempt >= max_attempts:
        # Fallback à un autre modèle
        if model == "claude" and APIS["openai"]["available"]:
            print(f"  🔄 Fallback → OpenAI")
            return safe_call(system, user_prompt, model="openai", attempt=0)
        elif model == "openai" and APIS["claude"]["available"]:
            print(f"  🔄 Fallback → Claude")
            return safe_call(system, user_prompt, model="claude", attempt=0)
        else:
            print(f"  ❌ Aucun modèle disponible")
            return None

    if not APIS[model]["available"]:
        print(f"  ⚠️ {model.upper()} non disponible")
        # Essayer un autre modèle
        alt_model = "openai" if model == "claude" else "claude"
        if APIS[alt_model]["available"]:
            print(f"  🔄 Essai → {alt_model.upper()}")
            return safe_call(system, user_prompt, model=alt_model, attempt=0)
        return None

    print(f"  → Tentative {attempt+1}/3 ({model.upper()})...", end="", flush=True)

    if model == "claude":
        response = call_claude(system, user_prompt)
    elif model == "openai":
        response = call_openai(system, user_prompt)
    else:
        response = None

    if response:
        print(" ✅")
        return response
    else:
        print(" ❌")
        time.sleep(2)
        return safe_call(system, user_prompt, model=model, attempt=attempt+1)

# ===============================================================
# AGENTS
# ===============================================================

def agent_scientifique(txt: str) -> str:
    """Analyse scientifique"""
    system = "Tu es un expert en mathématiques et modélisation. Analyse la rigueur scientifique en 100-150 mots."
    prompt = f"Texte:\n{txt[:2000]}"
    return safe_call(system, prompt, "claude") or "❌ Indisponible"

def agent_style(txt: str) -> str:
    """Amélioration de style"""
    system = "Tu es un relecteur académique. Améliore le style et la clarté en 100-150 mots."
    prompt = f"Texte:\n{txt[:2000]}"
    return safe_call(system, prompt, "openai") or "❌ Indisponible"

def agent_synthese(titre: str, analyses: list) -> str:
    """Synthèse"""
    system = "Tu es un examinateur. Synthétise les analyses en 80-100 mots."
    prompt = f"Chapitre: {titre}\n\nAnalyses:\n" + "\n\n".join(analyses)
    return safe_call(system, prompt, "claude") or "❌ Indisponible"

# ===============================================================
# UTILITAIRES
# ===============================================================

def lire_latex(fichier: str) -> str:
    """Lire un fichier LaTeX"""
    for encoding in ['utf-8', 'latin-1', 'cp1252']:
        try:
            with open(fichier, 'r', encoding=encoding) as f:
                return f.read()
        except:
            continue
    return ""

def extraire_chapitres(content: str, max_chapitres: int = 5) -> list:
    """Extraire les 5 premiers chapitres"""
    import re

    pattern = re.compile(r'\\chapter\{([^}]+)\}(.*?)(?=\\chapter|$)', re.DOTALL)
    matches = list(pattern.finditer(content))[:max_chapitres]

    chapitres = []
    for match in matches:
        titre = match.group(1)
        texte = match.group(2)
        # Limiter à 500 mots par chapitre
        mots = len(texte.split())
        if mots > 10:
            chapitres.append({
                "titre": titre,
                "texte": texte[:2000],
                "mots": mots
            })

    return chapitres

def generer_rapport(chapitres_analyses: list, temps_total: float) -> str:
    """Générer un rapport HTML"""
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Rapport d'Analyse Académique</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
        h1 {{ color: #1f4788; border-bottom: 3px solid #1f4788; padding-bottom: 15px; }}
        h2 {{ color: #2e5c8a; margin-top: 30px; }}
        .chapter {{ background: #f9f9f9; padding: 20px; margin: 20px 0; border-left: 4px solid #2e5c8a; }}
        .analysis {{ margin: 15px 0; padding: 15px; background: white; border-left: 3px solid #667eea; }}
        .analysis-title {{ color: #667eea; font-weight: bold; }}
        .meta {{ background: #e8f0f7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Rapport d'Analyse Académique</h1>
        <div class="meta">
            <p><strong>Date:</strong> {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
            <p><strong>Chapitres analysés:</strong> {len(chapitres_analyses)}</p>
            <p><strong>Temps total:</strong> {temps_total:.1f} secondes</p>
        </div>
"""

    for i, ch in enumerate(chapitres_analyses, 1):
        html += f"""
        <div class="chapter">
            <h2>{i}. {ch['titre']}</h2>
            <div class="analysis">
                <div class="analysis-title">✓ Rigueur Scientifique</div>
                <p>{ch['scientifique'][:300]}...</p>
            </div>
            <div class="analysis">
                <div class="analysis-title">✓ Style et Clarté</div>
                <p>{ch['style'][:300]}...</p>
            </div>
            <div class="analysis">
                <div class="analysis-title">✓ Synthèse</div>
                <p>{ch['synthese'][:300]}...</p>
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
    print("🤖 ANALYSEUR IA - VERSION STANDALONE")
    print("=" * 70)

    # Vérifier les APIs disponibles
    print("\n📋 APIs disponibles:")
    for api, info in APIS.items():
        status = "✅" if info["available"] else "❌"
        print(f"  {status} {api.upper()}")

    if not any(info["available"] for info in APIS.values()):
        print("\n❌ Aucune API configurée. Configurez:")
        print("   export ANTHROPIC_API_KEY='votre_clé'")
        print("   export OPENAI_API_KEY='votre_clé'")
        exit(1)

    # Demander le fichier
    fichier = input("\n📄 Fichier .tex à analyser: ").strip()
    if not os.path.exists(fichier):
        print(f"❌ Fichier introuvable: {fichier}")
        exit(1)

    # Lire et analyser
    print("\n🔍 Extraction des chapitres...")
    contenu = lire_latex(fichier)
    chapitres = extraire_chapitres(contenu)

    if not chapitres:
        print("❌ Aucun chapitre trouvé")
        exit(1)

    print(f"✅ {len(chapitres)} chapitres trouvés\n")

    # Analyser chaque chapitre
    debut = time.time()
    resultats = []

    for i, ch in enumerate(chapitres, 1):
        print(f"🔎 {i}/{len(chapitres)}: {ch['titre']}")

        sci = agent_scientifique(ch["texte"])
        sty = agent_style(ch["texte"])
        syn = agent_synthese(ch["titre"], [sci, sty])

        resultats.append({
            "titre": ch["titre"],
            "scientifique": sci,
            "style": sty,
            "synthese": syn
        })

    temps_total = time.time() - debut

    # Générer les rapports
    print("\n📊 Génération des rapports...")
    Path("rapports").mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # HTML
    html = generer_rapport(resultats, temps_total)
    html_path = f"rapports/rapport_standalone_{timestamp}.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ HTML: {html_path}")

    # JSON
    json_path = f"rapports/rapport_standalone_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({"analyses": resultats, "temps_secondes": temps_total}, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON: {json_path}")

    print(f"\n⏱️ Temps total: {temps_total:.1f}s")
    print("✨ Analyse terminée!")
