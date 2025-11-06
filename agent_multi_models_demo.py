#!/usr/bin/env python3
# ===============================================================
# agent_multi_models_demo.py — Version DÉMO (nov. 2025)
# ===============================================================
# Cette version démontre le fonctionnement sans appels API
# Parfait pour tester la génération HTML/PDF
# ===============================================================

import os, re, time, sys, json
from typing import Optional, List, Dict
from datetime import datetime
from pathlib import Path

# ===============================================================
# MODES D'ANALYSE
# ===============================================================

class ModeAnalyse:
    NORMAL = {
        "nom": "Normal",
        "description": "Analyse chapitres + sections principales",
        "niveaux": ["chapter", "section"],
        "min_mots": 50,
    }

# ===============================================================
# STATISTIQUES GLOBALES
# ===============================================================

class Statistiques:
    def __init__(self):
        self.debut = time.time()
        self.nb_appels = 0
        self.nb_erreurs = 0
        self.nb_fallbacks = 0
        self.resultats = []

    def ajouter_resultat(self, chapitre: str, scientifique: str, style: str, synthese: str):
        self.resultats.append({
            "chapitre": chapitre,
            "scientifique": scientifique,
            "style": style,
            "synthese": synthese
        })

    def obtenir_rapport(self) -> Dict:
        temps_total = time.time() - self.debut
        return {
            "temps_total_sec": round(temps_total, 2),
            "temps_total_min": round(temps_total / 60, 2),
            "nb_appels": 3 * len(self.resultats),
            "nb_erreurs": 0,
            "taux_succes": 100.0,
        }

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
# ANALYSES SIMULÉES
# ===============================================================

def agent_scientifique_demo(titre: str) -> str:
    analyses = {
        "default": f"L'analyse scientifique du chapitre '{titre}' montre une bonne rigueur mathématique. Les formulations sont précises et les notations sont cohérentes. Quelques points peuvent être améliorés : clarifier les hypothèses initiales et ajouter des références aux théorèmes utilisés. Globalement, la qualité scientifique est satisfaisante."
    }
    return analyses.get(titre, analyses["default"])

def agent_style_demo(titre: str) -> str:
    analyses = {
        "default": f"Le style du chapitre '{titre}' est académique mais pourrait être plus fluide. Recommandations : raccourcir certaines phrases complexes, utiliser des transitions plus claires entre les paragraphes, et améliorer la structure logique. Le vocabulaire est approprié mais on pourrait réduire les répétitions."
    }
    return analyses.get(titre, analyses["default"])

def agent_synthese_demo(titre: str) -> str:
    syntheses = {
        "default": f"En synthèse, le chapitre '{titre}' traite de sujets importants avec une approche générale solide. Les principaux points clés incluent : clarté conceptuelle, rigueur méthodologique, et pertinence académique. Des améliorations mineures en présentation et en références enrichiraient le document."
    }
    return syntheses.get(titre, syntheses["default"])

# ===============================================================
# GÉNÉRATION HTML / PDF
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
                <div class="analysis-content">{resultat['scientifique']}</div>
            </div>

            <div class="analysis-section">
                <div class="analysis-title">✓ Style et Clarté</div>
                <div class="analysis-content">{resultat['style']}</div>
            </div>

            <div class="analysis-section">
                <div class="analysis-title">✓ Synthèse</div>
                <div class="analysis-content">{resultat['synthese']}</div>
            </div>
        </div>
"""

    html += f"""
        <div class="footer">
            <p>Rapport généré automatiquement le {datetime.now().strftime("%d/%m/%Y à %H:%M:%S")}</p>
            <p>Analyseur Multi-Modèles IA v3.1 (DÉMO)</p>
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
                "note": "Version DÉMO - pas d'appels API réels"
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
    print("="*60)
    print("🤖 ANALYSEUR MULTI-MODÈLES IA – VERSION DÉMO")
    print("="*60)

    fichier = "Manuscript28octobre2025.tex"
    if not os.path.exists(fichier):
        print(f"❌ Fichier introuvable : {fichier}")
        sys.exit(1)

    print(f"\n📖 Lecture du manuscrit...")
    contenu = lire_latex(fichier)
    mode = ModeAnalyse.NORMAL
    chapitres = extraire_chapitres(contenu, mode)

    if not chapitres:
        print("⚠️ Aucune section détectée. Vérifie ton fichier.")
        sys.exit(0)

    print(f"\n📊 {len(chapitres)} sections trouvées, {sum(c['nb_mots'] for c in chapitres)} mots")
    print(f"\n🔄 Simulation d'analyse de {min(len(chapitres), 5)} sections (premier 5 max)...\n")

    # Initialiser les statistiques
    stats = Statistiques()

    # Analyse (les 5 premiers)
    for i, ch in enumerate(chapitres[:5], 1):
        print(f"🔎 {i}: Analyse de '{ch['titre']}' ({ch['nb_mots']} mots)")
        time.sleep(0.5)  # Simulation

        sci = agent_scientifique_demo(ch["titre"])
        sty = agent_style_demo(ch["titre"])
        syn = agent_synthese_demo(ch["titre"])

        stats.ajouter_resultat(ch["titre"], sci, sty, syn)
        print(f"   ✅ Analyse terminée")

    rapport = stats.obtenir_rapport()
    print(f"\n⏱️ Temps total : {rapport['temps_total_min']} min")
    print(f"📈 Sections analysées : {len(stats.resultats)}")
    print("🏁 Analyse complète.")

    # Générer les exports
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nom_rapport = f"rapport_demo_{timestamp}"

    json_path = sauvegarder_json(stats, nom_rapport, fichier, mode["nom"])
    html_content = generer_html(stats, nom_rapport, fichier, mode["nom"])
    html_path = sauvegarder_html(html_content, nom_rapport)

    print(f"\n✨ Résultats sauvegardés !")
    if html_path:
        print(f"   📄 HTML : {html_path}")
    if json_path:
        print(f"   📊 JSON : {json_path}")
    print(f"\n💡 Ouvre le HTML dans un navigateur pour voir le rapport complet")
    print(f"   Ou convertis-le en PDF avec ton navigateur (Fichier > Imprimer > Enregistrer en PDF)")
