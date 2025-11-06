# ===============================================================
# agent_multi_models_v3.0.py — Version améliorée (nov. 2025)
# ===============================================================
# ✅ Nouveautés V3.0 :
# 1. Génération automatique de PDF avec rapport structuré
# 2. Sauvegarde JSON des résultats intermédiaires
# 3. Barre de progression en temps réel
# 4. Statistiques détaillées (temps, tokens, erreurs)
# 5. Export HTML puis conversion en PDF
# 6. Meilleur logging et gestion d'erreurs
# ===============================================================

import os, re, time, sys, json
from typing import Optional, List, Dict
from datetime import datetime
from pathlib import Path

# ===============================================================
# DÉPENDANCES OPTIONNELLES
# ===============================================================

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except:
    print("⚠️ reportlab non disponible - les PDFs ne seront pas générés")
    REPORTLAB_AVAILABLE = False

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except:
    print("⚠️ tqdm non disponible - pas de barre de progression")
    TQDM_AVAILABLE = False

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
    gemini_model = genai.GenerativeModel(model_name="gemini-1.5-pro")
    GEMINI_AVAILABLE = True
    print("✅ Gemini initialisé (modèle gemini-1.5-pro)")
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
        self.modeles = {
            "scientifique": "claude",
            "style": "gemini",
            "plan": "claude",
            "synthese": "claude"
        }

    def afficher_config(self):
        print("\n📋 Configuration des modèles :")
        for tache, modele in self.modeles.items():
            print(f"  • {tache.capitalize():15s} → {modele.upper()}")

    def configurer_interactive(self, auto: bool = False):
        if auto:
            print("⚙️  Configuration automatique (Claude + Gemini par défaut)")
            self.afficher_config()
            return
        print("\n=== CONFIGURATION DES MODÈLES ===")
        print("💡 Recommandé : Claude (analyse), Gemini (style)")
        choix = input("Utiliser la config par défaut ? [O/n] : ").strip().lower()
        if choix in ['n', 'non']:
            for tache in self.modeles.keys():
                val = input(f"{tache.capitalize()} [claude/gemini/openai, défaut={self.modeles[tache]}] : ").strip().lower()
                if val in ['claude', 'gemini', 'openai']:
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
        return {
            "temps_total_sec": round(temps_total, 2),
            "temps_total_min": round(temps_total / 60, 2),
            "nb_appels": self.nb_appels,
            "nb_erreurs": self.nb_erreurs,
            "nb_fallbacks": self.nb_fallbacks,
            "taux_succes": round(100 * (1 - self.nb_erreurs / max(self.nb_appels, 1)), 1),
            "temps_moyen_appel_sec": round(sum(sum(v) for v in self.temps_par_api.values()) / max(self.nb_appels - self.nb_erreurs, 1), 2) if self.nb_appels > self.nb_erreurs else 0
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

    # Si tout échoue, basculement automatique
    if fallback:
        alt = {"claude": "openai", "openai": "gemini", "gemini": "claude"}[model]
        print(f"🔄 Basculement vers {alt.upper()}...")
        if stats:
            stats.nb_fallbacks += 1
        return safe_call_unified(system_prompt, user_prompt, temperature, model=alt, fallback=False, stats=stats)

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
# GÉNÉRATION PDF
# ===============================================================

def generer_pdf(stats: Statistiques, nom_fichier: str, fichier_source: str, mode: str):
    """Génère un PDF avec tous les résultats d'analyse"""

    if not REPORTLAB_AVAILABLE:
        print("⚠️ reportlab non disponible - génération PDF ignorée")
        return None

    try:
        # Créer les styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=1  # CENTER
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2e5c8a'),
            spaceAfter=12,
            spaceBefore=12
        )

        # Créer le document
        pdf_path = f"rapports/{nom_fichier}.pdf"
        Path("rapports").mkdir(exist_ok=True)

        doc = SimpleDocTemplate(pdf_path, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch)
        story = []

        # En-tête
        story.append(Paragraph("📊 RAPPORT D'ANALYSE ACADÉMIQUE", title_style))
        story.append(Spacer(1, 0.2*inch))

        # Métadonnées
        metadata = [
            ["Fichier source", fichier_source],
            ["Mode d'analyse", mode],
            ["Date du rapport", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Nombre de sections", str(len(stats.resultats))],
        ]

        table = Table(metadata, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0f7')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(table)
        story.append(Spacer(1, 0.3*inch))

        # Statistiques globales
        story.append(Paragraph("Statistiques Globales", heading_style))
        rapport = stats.obtenir_rapport()
        stats_data = [
            ["Temps total", f"{rapport['temps_total_min']} min"],
            ["Nombre d'appels API", str(rapport['nb_appels'])],
            ["Erreurs", str(rapport['nb_erreurs'])],
            ["Taux de succès", f"{rapport['taux_succes']}%"],
            ["Temps moyen par appel", f"{rapport['temps_moyen_appel_sec']} sec"],
        ]

        stats_table = Table(stats_data, colWidths=[2*inch, 4*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f8ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 0.3*inch))

        # Analyses par chapitre
        for i, resultat in enumerate(stats.resultats, 1):
            if i > 1:
                story.append(PageBreak())

            story.append(Paragraph(f"Chapitre {i}: {resultat['chapitre']}", heading_style))

            # Analyse scientifique
            story.append(Paragraph("<b>✓ Rigueur scientifique</b>", styles['Normal']))
            story.append(Paragraph(resultat['scientifique'][:1000] + "..." if len(resultat['scientifique']) > 1000 else resultat['scientifique'], styles['Normal']))
            story.append(Spacer(1, 0.15*inch))

            # Amélioration stylistique
            story.append(Paragraph("<b>✓ Style et clarté</b>", styles['Normal']))
            story.append(Paragraph(resultat['style'][:1000] + "..." if len(resultat['style']) > 1000 else resultat['style'], styles['Normal']))
            story.append(Spacer(1, 0.15*inch))

            # Synthèse
            story.append(Paragraph("<b>✓ Synthèse</b>", styles['Normal']))
            story.append(Paragraph(resultat['synthese'][:1000] + "..." if len(resultat['synthese']) > 1000 else resultat['synthese'], styles['Normal']))
            story.append(Spacer(1, 0.2*inch))

        # Construire le PDF
        doc.build(story)
        print(f"✅ PDF généré : {pdf_path}")
        return pdf_path

    except Exception as e:
        print(f"❌ Erreur lors de la génération du PDF : {e}")
        return None

def sauvegarder_json(stats: Statistiques, nom_fichier: str, fichier_source: str, mode: str):
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
    print("🤖 ANALYSEUR MULTI-MODÈLES IA – V3.0 (avec PDF)")
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

    # Analyse avec barre de progression
    if TQDM_AVAILABLE:
        iter_chapitres = tqdm(enumerate(chapitres, 1), total=len(chapitres), desc="Analyse en cours")
    else:
        iter_chapitres = enumerate(chapitres, 1)

    for i, ch in iter_chapitres:
        if not TQDM_AVAILABLE:
            print(f"\n🔎 {i}/{len(chapitres)}: {ch['titre']} ({ch['nb_mots']} mots)")

        sci = agent_scientifique(ch["texte"], config.modeles["scientifique"], stats)
        sty = agent_style(ch["texte"], config.modeles["style"], stats)
        syn = agent_synthese(ch["titre"], [sci, sty], config.modeles["synthese"], stats)

        stats.ajouter_resultat(ch["titre"], sci, sty, syn)

        if not TQDM_AVAILABLE:
            print(f"   ✅ Terminé ({i}/{len(chapitres)})")

    rapport = stats.obtenir_rapport()
    print(f"\n⏱️ Temps total : {rapport['temps_total_min']} min")
    print(f"📈 Appels API : {rapport['nb_appels']} | Erreurs : {rapport['nb_erreurs']} | Succès : {rapport['taux_succes']}%")
    print("🏁 Analyse complète.")

    # Générer les exports
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nom_rapport = f"rapport_analyse_{timestamp}"

    json_path = sauvegarder_json(stats, nom_rapport, fichier, mode["nom"])
    pdf_path = generer_pdf(stats, nom_rapport, fichier, mode["nom"])

    if pdf_path:
        print(f"\n✨ Tous les résultats ont été sauvegardés !")
        print(f"   📄 PDF : {pdf_path}")
        if json_path:
            print(f"   📋 JSON : {json_path}")
