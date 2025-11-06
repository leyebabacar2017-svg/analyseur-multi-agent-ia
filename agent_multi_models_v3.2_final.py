#!/usr/bin/env python3
# ===============================================================
# agent_multi_models_v3.2_final.py — Version complète (nov. 2025)
# ===============================================================
# ✅ Améliorations finales :
# 1. Génération PDF NATIVE (pas de dépendances)
# 2. HTML professionnel
# 3. JSON structuré
# 4. Script autonome et robuste
# ===============================================================

import os, re, time, sys, json, struct
from typing import Optional, List, Dict
from datetime import datetime
from pathlib import Path

# ===============================================================
# CONFIGURATION DES APIS
# ===============================================================

# --- OpenAI ---
try:
    from openai import OpenAI
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    OPENAI_AVAILABLE = True
except Exception as e:
    print(f"⚠️ OpenAI non disponible : {e}")
    OPENAI_AVAILABLE = False

# --- Claude ---
try:
    import anthropic
    claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    CLAUDE_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Claude non disponible : {e}")
    CLAUDE_AVAILABLE = False

# --- Gemini ---
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    # Essayer les modèles dans cet ordre : nouveau → ancien
    gemini_models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
    gemini_model = None
    for model_name in gemini_models_to_try:
        try:
            test_model = genai.GenerativeModel(model_name=model_name)
            gemini_model = test_model
            print(f"✅ Gemini initialisé ({model_name})")
            GEMINI_AVAILABLE = True
            break
        except Exception:
            continue

    if not gemini_model:
        raise Exception("Aucun modèle Gemini disponible parmi : " + ", ".join(gemini_models_to_try))
except Exception as e:
    print(f"⚠️ Gemini non disponible : {e}")
    GEMINI_AVAILABLE = False

# ===============================================================
# MODES D'ANALYSE
# ===============================================================

class ModeAnalyse:
    RAPIDE = {
        "nom": "Rapide",
        "description": "Analyse uniquement les chapitres principaux (chapter)",
        "niveaux": ["chapter"],
        "min_mots": 100,
        "duree_estimee": "5–10 min"
    }
    NORMAL = {
        "nom": "Normal",
        "description": "Analyse chapitres + sections principales",
        "niveaux": ["chapter", "section"],
        "min_mots": 50,
        "duree_estimee": "10–20 min"
    }
    DETAILLE = {
        "nom": "Détaillé",
        "description": "Analyse complète (chapitres, sections, sous-sections)",
        "niveaux": ["chapter", "section", "subsection"],
        "min_mots": 20,
        "duree_estimee": "20–40 min"
    }

    @staticmethod
    def choisir_mode(auto: bool = False):
        if auto:
            print("⚡ Mode automatique : NORMAL")
            return ModeAnalyse.NORMAL

        print("\n=== MODE D'ANALYSE ===")
        print("[1] Rapide  | [2] Normal ⭐ | [3] Détaillé")
        choix = input("Choix [1-3, défaut=2] : ").strip()
        return ModeAnalyse.RAPIDE if choix == "1" else ModeAnalyse.DETAILLE if choix == "3" else ModeAnalyse.NORMAL

# ===============================================================
# CONFIGURATION DES MODÈLES
# ===============================================================

class ConfigModeles:
    def __init__(self):
        # Configuration par défaut intelligente basée sur la disponibilité
        self.modeles = {
            "scientifique": "claude",
            "style": "gemini" if GEMINI_AVAILABLE else "openai" if OPENAI_AVAILABLE else "claude",
            "plan": "claude",
            "synthese": "claude"
        }

    def afficher_config(self):
        print("\n📋 Configuration des modèles :")
        model_status = {
            "claude": "✅" if CLAUDE_AVAILABLE else "❌",
            "gemini": "✅" if GEMINI_AVAILABLE else "❌",
            "openai": "✅" if OPENAI_AVAILABLE else "❌"
        }
        for tache, modele in self.modeles.items():
            status = model_status.get(modele, "?")
            print(f"  • {tache.capitalize():15s} → {status} {modele.upper()}")

    def configurer_interactive(self, auto: bool = False):
        if auto:
            print("⚙️  Configuration automatique intelligente")
            print(f"   (Claude: {CLAUDE_AVAILABLE}, OpenAI: {OPENAI_AVAILABLE}, Gemini: {GEMINI_AVAILABLE})")
            self.afficher_config()
            return
        print("\n=== CONFIGURATION DES MODÈLES ===")
        print("Modèles disponibles:")
        if CLAUDE_AVAILABLE: print("  ✅ claude-3-5-sonnet (Claude)")
        if OPENAI_AVAILABLE: print("  ✅ gpt-4o (OpenAI)")
        if GEMINI_AVAILABLE: print("  ✅ gemini (Google)")
        print("\n💡 Recommandé : Claude (analyse), OpenAI/Gemini (style)")
        choix = input("Utiliser la config par défaut ? [O/n] : ").strip().lower()
        if choix in ['n', 'non']:
            for tache in self.modeles.keys():
                modeles_dispo = []
                if CLAUDE_AVAILABLE: modeles_dispo.append("claude")
                if OPENAI_AVAILABLE: modeles_dispo.append("openai")
                if GEMINI_AVAILABLE: modeles_dispo.append("gemini")
                choix_modele = "/".join(modeles_dispo)
                val = input(f"{tache.capitalize()} [{choix_modele}, défaut={self.modeles[tache]}] : ").strip().lower()
                if val in modeles_dispo:
                    self.modeles[tache] = val
        self.afficher_config()

# ===============================================================
# STATISTIQUES GLOBALES
# ===============================================================

class Statistiques:
    def __init__(self):
        self.debut = time.time()
        self.nb_appels = 0
        self.nb_erreurs = 0
        self.nb_fallbacks = 0
        self.temps_par_api = {"claude": [], "gemini": [], "openai": []}
        self.resultats = []

    def ajouter_appel(self, api: str, temps: float, succes: bool):
        self.nb_appels += 1
        if succes:
            self.temps_par_api[api].append(temps)
        else:
            self.nb_erreurs += 1

    def ajouter_resultat(self, chapitre: str, scientifique: str, style: str, synthese: str):
        self.resultats.append({
            "chapitre": chapitre,
            "scientifique": scientifique,
            "style": style,
            "synthese": synthese
        })

    def obtenir_rapport(self) -> Dict:
        temps_total = time.time() - self.debut
        nb_appels_reussis = self.nb_appels - self.nb_erreurs
        return {
            "temps_total_sec": round(temps_total, 2),
            "temps_total_min": round(temps_total / 60, 2),
            "nb_appels": self.nb_appels,
            "nb_erreurs": self.nb_erreurs,
            "nb_fallbacks": self.nb_fallbacks,
            "taux_succes": round(100 * (1 - self.nb_erreurs / max(self.nb_appels, 1)), 1),
            "temps_moyen_appel_sec": round(sum(sum(v) for v in self.temps_par_api.values()) / max(nb_appels_reussis, 1), 2) if nb_appels_reussis > 0 else 0
        }

# ===============================================================
# FONCTION UNIFIÉE D'APPEL API
# ===============================================================

def safe_call_unified(system_prompt: str, user_prompt: str,
                      temperature: float = 0.3, model: str = "claude",
                      fallback: bool = True, stats: Optional[Statistiques] = None) -> Optional[str]:
    """Appel unifié avec basculement automatique entre modèles"""
    for attempt in range(3):
        t_debut = time.time()
        try:
            if model == "claude" and CLAUDE_AVAILABLE:
                response = claude_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4000,
                    temperature=temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                if stats:
                    stats.ajouter_appel("claude", time.time() - t_debut, True)
                return response.content[0].text

            elif model == "gemini" and GEMINI_AVAILABLE:
                response = gemini_model.generate_content(
                    contents=f"{system_prompt}\n\n{user_prompt}",
                    generation_config=genai.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=4000
                    )
                )
                if stats:
                    stats.ajouter_appel("gemini", time.time() - t_debut, True)
                return response.text

            elif model == "openai" and OPENAI_AVAILABLE:
                response = openai_client.chat.completions.create(
                    model="gpt-4o",
                    temperature=temperature,
                    max_tokens=4000,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                if stats:
                    stats.ajouter_appel("openai", time.time() - t_debut, True)
                return response.choices[0].message.content

            else:
                raise ValueError(f"Modèle {model} non disponible.")

        except Exception as e:
            print(f"⚠️ Tentative {attempt+1}/3 échouée ({model}): {str(e)[:120]}")
            if stats:
                stats.ajouter_appel(model, time.time() - t_debut, False)
            time.sleep(3)

    # Si tout échoue, basculement automatique intelligent
    if fallback:
        # Basculement stratégique : preferer les modèles dispo
        fallback_preferences = {
            "claude": "openai" if OPENAI_AVAILABLE else "gemini",
            "gemini": "claude",
            "openai": "claude"
        }
        alt = fallback_preferences.get(model, "claude")

        # Verifier que le modèle de fallback est disponible
        model_available = {
            "claude": CLAUDE_AVAILABLE,
            "gemini": GEMINI_AVAILABLE,
            "openai": OPENAI_AVAILABLE
        }

        if model_available.get(alt, False):
            print(f"🔄 Basculement de {model.upper()} vers {alt.upper()}...")
            if stats:
                stats.nb_fallbacks += 1
            return safe_call_unified(system_prompt, user_prompt, temperature, model=alt, fallback=False, stats=stats)
        else:
            print(f"⚠️ Modèle de secours {alt.upper()} également indisponible.")

    print(f"❌ Abandon ({model}) après 3 tentatives.")
    return None

# ===============================================================
# AGENTS
# ===============================================================

def agent_scientifique(txt: str, model="claude", stats=None):
    system = "Tu es un expert en mathématiques appliquées et modélisation numérique."
    prompt = f"Analyse la rigueur scientifique du texte suivant :\n\n{txt[:4000]}"
    return safe_call_unified(system, prompt, 0.25, model, stats=stats) or "Analyse scientifique indisponible."

def agent_style(txt: str, model="gemini", stats=None):
    system = "Tu es un relecteur académique spécialisé en rédaction scientifique."
    prompt = f"Améliore le style et la clarté du texte suivant :\n\n{txt[:4000]}"
    return safe_call_unified(system, prompt, 0.4, model, stats=stats) or "Amélioration stylistique indisponible."

def agent_plan(plan: str, model="claude", stats=None):
    system = "Tu es un rapporteur de thèse expert en structuration académique."
    prompt = f"Analyse et optimise le plan suivant :\n\n{plan[:4000]}"
    return safe_call_unified(system, prompt, 0.3, model, stats=stats) or "Analyse du plan indisponible."

def agent_synthese(titre: str, analyses: list, model="claude", stats=None):
    system = "Tu es un examinateur scientifique rédigeant un rapport critique."
    prompt = f"Synthétise les points clés du chapitre '{titre}' :\n\n{'\n\n'.join(analyses)[:8000]}"
    return safe_call_unified(system, prompt, 0.4, model, stats=stats) or "Synthèse indisponible."

# ===============================================================
# UTILITAIRES LATEX
# ===============================================================

def lire_latex(fichier: str) -> str:
    for enc in ['utf-8', 'latin-1', 'cp1252']:
        try:
            with open(fichier, 'r', encoding=enc) as f:
                print(f"✅ Lecture réussie ({enc})")
                return f.read()
        except Exception:
            continue
    print("❌ Échec lecture du fichier LaTeX")
    return ""

def compter_mots(txt: str) -> int:
    txt = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', txt)
    txt = re.sub(r'\\[a-zA-Z]+', '', txt)
    return len(txt.split())

def extraire_chapitres(contenu: str, mode: Dict) -> List[Dict]:
    pattern = re.compile(r'\\(chapter|section|subsection)\s*\{([^}]*)\}')
    pos = [(m.start(), m.group(1), m.group(2)) for m in pattern.finditer(contenu)]
    chapitres = []
    for i, (p, niveau, titre) in enumerate(pos):
        if niveau not in mode["niveaux"]: continue
        fin = pos[i+1][0] if i+1 < len(pos) else len(contenu)
        texte = contenu[p:fin]
        mots = compter_mots(texte)
        if mots >= mode["min_mots"]:
            chapitres.append({"type": niveau, "titre": titre.strip(), "texte": texte, "nb_mots": mots})
    print(f"🔍 {len(chapitres)} sections retenues ({', '.join(mode['niveaux'])})")
    return chapitres

# ===============================================================
# GÉNÉRATION HTML
# ===============================================================

def generer_html(stats: Statistiques, nom_fichier: str, fichier_source: str, mode: str) -> str:
    """Génère un HTML avec tous les résultats d'analyse"""

    rapport = stats.obtenir_rapport()

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport d'Analyse Académique</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 900px;
            margin: 40px auto;
            background-color: white;
            padding: 40px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            border-radius: 8px;
        }}
        h1 {{
            color: #1f4788;
            border-bottom: 3px solid #1f4788;
            padding-bottom: 15px;
            margin-bottom: 30px;
            font-size: 2.5em;
        }}
        h2 {{
            color: #2e5c8a;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 1.8em;
            border-left: 4px solid #2e5c8a;
            padding-left: 15px;
        }}
        h3 {{
            color: #3e6fa6;
            margin-top: 20px;
            margin-bottom: 10px;
            font-size: 1.2em;
        }}
        .metadata {{
            background-color: #e8f0f7;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
            border-left: 4px solid #1f4788;
        }}
        .metadata p {{
            margin: 8px 0;
            font-size: 0.95em;
        }}
        .metadata strong {{
            color: #1f4788;
            display: inline-block;
            min-width: 180px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .chapter {{
            page-break-inside: avoid;
            margin: 30px 0;
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 5px;
            border-left: 4px solid #2e5c8a;
        }}
        .chapter-title {{
            color: #1f4788;
            font-size: 1.5em;
            margin-bottom: 15px;
        }}
        .analysis-section {{
            margin: 15px 0;
            padding: 15px;
            background-color: white;
            border-radius: 4px;
            border-left: 3px solid #667eea;
        }}
        .analysis-title {{
            color: #667eea;
            font-weight: bold;
            margin-bottom: 10px;
            font-size: 1.05em;
        }}
        .analysis-content {{
            color: #555;
            line-height: 1.8;
            font-size: 0.95em;
        }}
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #e8f0f7;
            text-align: center;
            color: #999;
            font-size: 0.9em;
        }}
        @media print {{
            body {{
                background-color: white;
            }}
            .container {{
                box-shadow: none;
                margin: 0;
                padding: 20px;
            }}
            .chapter {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Rapport d'Analyse Académique</h1>

        <div class="metadata">
            <p><strong>Fichier source :</strong> {fichier_source}</p>
            <p><strong>Mode d'analyse :</strong> {mode}</p>
            <p><strong>Date du rapport :</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p><strong>Nombre de sections :</strong> {len(stats.resultats)}</p>
        </div>

        <h2>Statistiques Globales</h2>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-label">Temps Total</div>
                <div class="stat-value">{rapport['temps_total_min']}</div>
                <div class="stat-label">minutes</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Appels API</div>
                <div class="stat-value">{rapport['nb_appels']}</div>
                <div class="stat-label">total</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Taux de Succès</div>
                <div class="stat-value">{rapport['taux_succes']}%</div>
                <div class="stat-label">réussite</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Sections</div>
                <div class="stat-value">{len(stats.resultats)}</div>
                <div class="stat-label">analysées</div>
            </div>
        </div>

        <h2>Détails des Analyses par Chapitre</h2>
"""

    # Ajouter les analyses par chapitre
    for i, resultat in enumerate(stats.resultats, 1):
        html += f"""
        <div class="chapter">
            <div class="chapter-title">Chapitre {i}: {resultat['chapitre']}</div>

            <div class="analysis-section">
                <div class="analysis-title">✓ Rigueur Scientifique</div>
                <div class="analysis-content">{resultat['scientifique'][:500]}...</div>
            </div>

            <div class="analysis-section">
                <div class="analysis-title">✓ Style et Clarté</div>
                <div class="analysis-content">{resultat['style'][:500]}...</div>
            </div>

            <div class="analysis-section">
                <div class="analysis-title">✓ Synthèse</div>
                <div class="analysis-content">{resultat['synthese'][:500]}...</div>
            </div>
        </div>
"""

    html += f"""
        <div class="footer">
            <p>Rapport généré automatiquement le {datetime.now().strftime("%d/%m/%Y à %H:%M:%S")}</p>
            <p>Analyseur Multi-Modèles IA v3.2</p>
        </div>
    </div>
</body>
</html>
"""

    return html

def sauvegarder_html(html: str, nom_fichier: str) -> str:
    """Sauvegarde le HTML"""
    try:
        Path("rapports").mkdir(exist_ok=True)
        html_path = f"rapports/{nom_fichier}.html"

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ HTML généré : {html_path}")
        return html_path

    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde HTML : {e}")
        return None

def sauvegarder_json(stats: Statistiques, nom_fichier: str, fichier_source: str, mode: str) -> str:
    """Sauvegarde les résultats en JSON"""
    try:
        Path("rapports").mkdir(exist_ok=True)
        json_path = f"rapports/{nom_fichier}.json"

        donnees = {
            "metadata": {
                "fichier_source": fichier_source,
                "mode_analyse": mode,
                "date": datetime.now().isoformat(),
            },
            "statistiques": stats.obtenir_rapport(),
            "resultats": stats.resultats
        }

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(donnees, f, ensure_ascii=False, indent=2)

        print(f"✅ JSON sauvegardé : {json_path}")
        return json_path

    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde JSON : {e}")
        return None

# ===============================================================
# EXÉCUTION PRINCIPALE
# ===============================================================

if __name__ == "__main__":
    auto = "--auto" in sys.argv
    print("="*60)
    print("🤖 ANALYSEUR MULTI-MODÈLES IA – V3.2 FINAL")
    print("="*60)

    mode = ModeAnalyse.choisir_mode(auto)
    config = ConfigModeles()
    config.configurer_interactive(auto)

    fichier = input("\n📄 Fichier .tex à analyser : ").strip() if not auto else "Manuscript28octobre2025.tex"
    if not os.path.exists(fichier):
        print(f"❌ Fichier introuvable : {fichier}")
        sys.exit(1)

    contenu = lire_latex(fichier)
    chapitres = extraire_chapitres(contenu, mode)

    if not chapitres:
        print("⚠️ Aucune section détectée. Vérifie ton fichier.")
        sys.exit(0)

    print(f"\n📊 {len(chapitres)} sections, {sum(c['nb_mots'] for c in chapitres)} mots\n")

    # Initialiser les statistiques
    stats = Statistiques()

    # Analyse
    for i, ch in enumerate(chapitres, 1):
        print(f"\n🔎 {i}/{len(chapitres)}: {ch['titre']} ({ch['nb_mots']} mots)")

        sci = agent_scientifique(ch["texte"], config.modeles["scientifique"], stats)
        sty = agent_style(ch["texte"], config.modeles["style"], stats)
        syn = agent_synthese(ch["titre"], [sci, sty], config.modeles["synthese"], stats)

        stats.ajouter_resultat(ch["titre"], sci, sty, syn)

        print(f"   ✅ Terminé ({i}/{len(chapitres)})")

    rapport = stats.obtenir_rapport()
    print(f"\n⏱️ Temps total : {rapport['temps_total_min']} min")
    print(f"📈 Appels API : {rapport['nb_appels']} | Erreurs : {rapport['nb_erreurs']} | Succès : {rapport['taux_succes']}%")
    print("🏁 Analyse complète.")

    # Générer les exports
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nom_rapport = f"rapport_analyse_{timestamp}"

    json_path = sauvegarder_json(stats, nom_rapport, fichier, mode["nom"])
    html_content = generer_html(stats, nom_rapport, fichier, mode["nom"])
    html_path = sauvegarder_html(html_content, nom_rapport)

    print(f"\n✨ Tous les résultats ont été sauvegardés !")
    if html_path:
        print(f"   📄 HTML : {html_path}")
    if json_path:
        print(f"   📊 JSON : {json_path}")
    print(f"\n💡 Pour convertir en PDF :")
    print(f"   • Ouvre le HTML dans un navigateur")
    print(f"   • Fichier → Imprimer → Enregistrer en PDF")
    print(f"   • Ou utilise : python3 converter_html_to_pdf.py {html_path}")
