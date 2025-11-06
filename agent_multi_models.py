# ===============================================================
# agent_multi_models_v2.1.py — Version optimisée avec modes d'analyse
# ===============================================================
# Améliorations V2.1 :
# 1. Mode d'analyse configurable (Rapide/Normal/Détaillé)
# 2. Groupement par chapitre au lieu de section
# 3. Filtrage des sections trop petites
# 4. Estimation du temps avant analyse
# ===============================================================

import os, re, time
from typing import Optional, List, Dict
from datetime import datetime

# ===============================================================
# CONFIGURATION DES APIS
# ===============================================================

# Configuration OpenAI
try:
    from openai import OpenAI, APIError, APITimeoutError
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    OPENAI_AVAILABLE = True
except Exception as e:
    print(f"⚠️ OpenAI non disponible : {e}")
    OPENAI_AVAILABLE = False

# Configuration Anthropic (Claude)
try:
    import anthropic
    claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    CLAUDE_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Claude non disponible : {e}")
    CLAUDE_AVAILABLE = False

# Configuration Google Gemini
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    gemini_model = genai.GenerativeModel('gemini-1.5-pro')
    GEMINI_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Gemini non disponible : {e}")
    GEMINI_AVAILABLE = False

# ===============================================================
# MODES D'ANALYSE
# ===============================================================

class ModeAnalyse:
    """Définit les modes d'analyse disponibles"""
    
    RAPIDE = {
        "nom": "Rapide",
        "description": "Analyse uniquement les chapitres principaux (chapter)",
        "niveaux": ["chapter"],
        "min_mots": 200,
        "duree_estimee": "rapide (5-10 min)"
    }
    
    NORMAL = {
        "nom": "Normal",
        "description": "Analyse les chapitres et sections principales",
        "niveaux": ["chapter", "section"],
        "min_mots": 100,
        "duree_estimee": "moyenne (10-20 min)"
    }
    
    DETAILLE = {
        "nom": "Détaillé",
        "description": "Analyse complète : chapitres, sections et sous-sections",
        "niveaux": ["chapter", "section", "subsection"],
        "min_mots": 50,
        "duree_estimee": "longue (20-40 min)"
    }
    
    @staticmethod
    def choisir_mode():
        """Interface pour choisir le mode d'analyse"""
        print("\n" + "="*60)
        print("⚡ MODE D'ANALYSE")
        print("="*60)
        print("\n[1] 🚀 RAPIDE (5-10 min)")
        print("    → Analyse uniquement les chapitres principaux")
        print("    → Recommandé pour : premier aperçu, test")
        
        print("\n[2] ⚖️  NORMAL (10-20 min) ⭐ RECOMMANDÉ")
        print("    → Analyse chapitres + sections principales")
        print("    → Recommandé pour : la plupart des documents")
        
        print("\n[3] 🔬 DÉTAILLÉ (20-40 min)")
        print("    → Analyse complète avec sous-sections")
        print("    → Recommandé pour : thèses, documents critiques")
        
        choix = input("\nChoisissez un mode [1-3, défaut=2] : ").strip()
        
        if choix == "1":
            return ModeAnalyse.RAPIDE
        elif choix == "3":
            return ModeAnalyse.DETAILLE
        else:
            return ModeAnalyse.NORMAL

# ===============================================================
# CONFIGURATION DES MODÈLES PAR TÂCHE
# ===============================================================

class ConfigModeles:
    """Configuration des modèles à utiliser pour chaque type d'analyse"""
    
    def __init__(self):
        self.modeles = {
            "scientifique": "claude",
            "style": "gemini",
            "plan": "claude",
            "synthese": "claude"
        }
    
    def afficher_config(self):
        """Affiche la configuration actuelle"""
        print("\n📋 Configuration des modèles par tâche :")
        print(f"  • Analyse scientifique : {self.modeles['scientifique'].upper()}")
        print(f"  • Amélioration style   : {self.modeles['style'].upper()}")
        print(f"  • Restructuration plan : {self.modeles['plan'].upper()}")
        print(f"  • Synthèse finale      : {self.modeles['synthese'].upper()}")
    
    def configurer_interactive(self):
        """Configuration interactive des modèles"""
        print("\n" + "="*60)
        print("⚙️  CONFIGURATION DES MODÈLES PAR TÂCHE")
        print("="*60)
        print("\nRecommandations :")
        print("  • CLAUDE   → Meilleur en analyse académique approfondie")
        print("  • GEMINI   → Rapide et gratuit, bon pour le style")
        print("  • OPENAI   → Polyvalent, bon équilibre partout")
        print("\n💡 Conseil : Claude pour scientifique/synthèse, Gemini pour style")
        
        choix = input("\nUtiliser la configuration recommandée ? [O/n] : ").strip().lower()
        
        if choix in ['n', 'non', 'no']:
            print("\n🔧 Configuration manuelle :")
            taches = {
                "scientifique": "Analyse scientifique (équations, cohérence)",
                "style": "Amélioration stylistique (grammaire, clarté)",
                "plan": "Restructuration du plan (redondances)",
                "synthese": "Synthèse finale (rapport global)"
            }
            
            for tache, description in taches.items():
                print(f"\n📌 {description}")
                print("  [1] Claude  [2] Gemini  [3] OpenAI")
                choix_model = input(f"  Modèle pour '{tache}' [1-3, défaut={self.modeles[tache]}] : ").strip()
                
                if choix_model == '1':
                    self.modeles[tache] = 'claude'
                elif choix_model == '2':
                    self.modeles[tache] = 'gemini'
                elif choix_model == '3':
                    self.modeles[tache] = 'openai'
        
        print("\n✅ Configuration finalisée !")
        self.afficher_config()

# ===============================================================
# GESTION DES DOSSIERS DE SORTIE
# ===============================================================

class GestionnaireDossiers:
    """Gère l'organisation des fichiers de sortie"""
    
    def __init__(self, nom_fichier_source: str, mode: Dict):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nom_base = os.path.splitext(os.path.basename(nom_fichier_source))[0]
        mode_nom = mode["nom"].lower()
        self.dossier_principal = f"analyse_{nom_base}_{mode_nom}_{timestamp}"
        
        self.dossier_syntheses = os.path.join(self.dossier_principal, "syntheses_chapitres")
        self.dossier_rapports = os.path.join(self.dossier_principal, "rapports")
        self.dossier_logs = os.path.join(self.dossier_principal, "logs")
        
        self.creer_structure()
    
    def creer_structure(self):
        """Crée la structure de dossiers"""
        os.makedirs(self.dossier_principal, exist_ok=True)
        os.makedirs(self.dossier_syntheses, exist_ok=True)
        os.makedirs(self.dossier_rapports, exist_ok=True)
        os.makedirs(self.dossier_logs, exist_ok=True)
        
        print(f"\n📁 Dossier d'analyse créé : {self.dossier_principal}/")
    
    def chemin_synthese(self, numero: int, config: ConfigModeles) -> str:
        modeles_str = f"{config.modeles['scientifique']}-{config.modeles['style']}"
        return os.path.join(self.dossier_syntheses, f"chapitre_{numero:02d}_{modeles_str}.txt")
    
    def chemin_rapport(self, config: ConfigModeles) -> str:
        modele_principal = config.modeles['synthese']
        return os.path.join(self.dossier_rapports, f"rapport_analyse_{modele_principal}.tex")
    
    def chemin_log(self) -> str:
        return os.path.join(self.dossier_logs, "analyse.log")
    
    def chemin_config(self) -> str:
        return os.path.join(self.dossier_principal, "configuration.txt")
    
    def sauvegarder_config(self, config: ConfigModeles, fichier_source: str, mode: Dict, nb_sections: int):
        """Sauvegarde la configuration utilisée"""
        with open(self.chemin_config(), "w", encoding="utf-8") as f:
            f.write("="*60 + "\n")
            f.write("CONFIGURATION DE L'ANALYSE\n")
            f.write("="*60 + "\n\n")
            f.write(f"Date/Heure : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Fichier source : {fichier_source}\n")
            f.write(f"Mode d'analyse : {mode['nom']} ({mode['duree_estimee']})\n")
            f.write(f"Sections analysées : {nb_sections}\n\n")
            f.write("Modèles utilisés par tâche :\n")
            for tache, modele in config.modeles.items():
                f.write(f"  • {tache.capitalize():20s} : {modele.upper()}\n")
            f.write("\nNiveaux de structure analysés :\n")
            for niveau in mode['niveaux']:
                f.write(f"  • {niveau}\n")
            f.write(f"\nMot minimum par section : {mode['min_mots']}\n")
            f.write("\n" + "="*60 + "\n")

# ===============================================================
# WRAPPER UNIFIÉ POUR LES 3 APIS
# ===============================================================

def safe_call_unified(system_prompt: str, user_prompt: str, temperature: float = 0.3, model: str = "claude") -> Optional[str]:
    """Appel unifié pour Claude, Gemini ou OpenAI avec retry"""
    
    for attempt in range(3):
        try:
            if model == "claude" and CLAUDE_AVAILABLE:
                response = claude_client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4000,
                    temperature=temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                return response.content[0].text
            
            elif model == "gemini" and GEMINI_AVAILABLE:
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                response = gemini_model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=4000
                    )
                )
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
                return response.choices[0].message.content
            
            else:
                print(f"❌ Modèle '{model}' non disponible ou non configuré.")
                return None
                
        except Exception as e:
            print(f"⚠️ Tentative {attempt+1}/3 échouée ({type(e).__name__}): {str(e)[:100]}")
            time.sleep(5)
    
    print("❌ Abandon après 3 tentatives.")
    return None

# ===============================================================
# AGENTS SPÉCIALISÉS
# ===============================================================

def agent_scientifique(section_text: str, model: str = "claude") -> str:
    """Agent 1️⃣ — Analyse scientifique et mathématique"""
    system = "Tu es un expert en mathématiques appliquées et modélisation numérique."
    prompt = f"""
Analyse scientifique d'un mémoire en mathématiques appliquées :
- Vérifie la cohérence théorique et la rigueur mathématique.
- Identifie les erreurs symboliques, incohérences, omissions.
- Suggère des améliorations précises et reformulations.

Texte :
{section_text[:4000]}
"""
    result = safe_call_unified(system, prompt, temperature=0.2, model=model)
    return result or "Analyse scientifique non disponible."

def agent_style(section_text: str, model: str = "gemini") -> str:
    """Agent 2️⃣ — Style académique et rédactionnel"""
    system = "Tu es un relecteur académique spécialisé dans la rédaction scientifique."
    prompt = f"""
Améliore le style académique du texte suivant :
- Corrige grammaire, syntaxe, ponctuation et style scientifique.
- Supprime les redondances et lourdeurs.
- Clarifie les phrases trop longues.

Texte :
{section_text[:4000]}
"""
    result = safe_call_unified(system, prompt, temperature=0.4, model=model)
    return result or "Amélioration stylistique non disponible."

def agent_plan(plan_text: str, model: str = "claude") -> str:
    """Agent 3️⃣ — Structure et organisation du document"""
    system = "Tu es un rapporteur de thèse spécialisé dans la structuration académique."
    prompt = f"""
Analyse la structure du mémoire :
- Détecte les redondances entre sections.
- Propose un plan restructuré complet (chapitres, sections, sous-sections).
- Indique les fusions, suppressions et intégrations à prévoir.
- Suggère un nombre de pages par section.

Plan détecté :
{plan_text[:4000]}
"""
    result = safe_call_unified(system, prompt, temperature=0.3, model=model)
    return result or "Analyse du plan non disponible."

def agent_synthese(chapitre: str, analyses: list, model: str = "claude") -> str:
    """Agent 4️⃣ — Synthèse globale par chapitre"""
    system = "Tu es un examinateur scientifique rédigeant un rapport de synthèse."
    joined = "\n\n".join(analyses)
    prompt = f"""
Rédige une synthèse critique complète du chapitre intitulé « {chapitre} » :
- Résume les points forts et faiblesses scientifiques et rédactionnels.
- Intègre les remarques de fond, de forme et de structure.
- Propose des reformulations et des suggestions concrètes.
- Présente le tout en paragraphes structurés et fluides (2 à 3 pages équivalentes).

Analyses des agents précédents :
{joined[:8000]}
"""
    result = safe_call_unified(system, prompt, temperature=0.4, model=model)
    return result or "Synthèse non disponible."

# ===============================================================
# UTILITAIRES LATEX - VERSION AMÉLIORÉE
# ===============================================================

def lire_latex(fichier: str) -> str:
    """Lit un fichier LaTeX"""
    with open(fichier, "r", encoding="utf-8") as f:
        return f.read()

def compter_mots(texte: str) -> int:
    """Compte le nombre de mots dans un texte"""
    # Enlève les commandes LaTeX pour un compte plus précis
    texte_nettoye = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', texte)
    texte_nettoye = re.sub(r'\\[a-zA-Z]+', '', texte_nettoye)
    mots = texte_nettoye.split()
    return len(mots)

def extraire_chapitres_optimise(contenu: str, mode: Dict) -> List[Dict]:
    """
    Extrait les chapitres/sections selon le mode choisi
    Groupe les sous-sections avec leur section parente
    """
    # Extraction de toutes les structures
    pattern = re.compile(r'\\(chapter|section|subsection)\{([^}]*)\}')
    positions = [(m.start(), m.group(1), m.group(2)) for m in pattern.finditer(contenu)]
    
    niveaux_autorises = mode['niveaux']
    min_mots = mode['min_mots']
    
    chapitres = []
    
    i = 0
    while i < len(positions):
        pos, niveau, titre = positions[i]
        
        # Si ce niveau n'est pas autorisé, on skip
        if niveau not in niveaux_autorises:
            i += 1
            continue
        
        # Trouver la fin de cette section
        start = pos
        end = len(contenu)
        
        # Chercher la prochaine section de même niveau ou supérieur
        for j in range(i + 1, len(positions)):
            next_pos, next_niveau, _ = positions[j]
            
            # Hiérarchie : chapter > section > subsection
            niveau_hierarchie = {"chapter": 1, "section": 2, "subsection": 3}
            
            if niveau_hierarchie[next_niveau] <= niveau_hierarchie[niveau]:
                end = next_pos
                break
        
        texte = contenu[start:end]
        nb_mots = compter_mots(texte)
        
        # Filtrer les sections trop petites
        if nb_mots >= min_mots:
            chapitres.append({
                "type": niveau,
                "titre": titre.strip(),
                "texte": texte,
                "nb_mots": nb_mots
            })
        
        i += 1
    
    return chapitres

def estimer_duree(nb_sections: int, config: ConfigModeles) -> str:
    """Estime la durée de l'analyse"""
    # Estimation: ~1-2 min par section en moyenne
    duree_min = nb_sections * 1
    duree_max = nb_sections * 2
    return f"{duree_min}-{duree_max} minutes"

def ecrire_rapport_latex(chapitres: list, syntheses: list, plan_restructure: str, 
                         dossiers: GestionnaireDossiers, config: ConfigModeles, mode: Dict):
    """Génère le rapport final en LaTeX"""
    chemin_rapport = dossiers.chemin_rapport(config)
    
    with open(chemin_rapport, "w", encoding="utf-8") as f:
        f.write(r"""\documentclass[12pt,a4paper]{report}
\usepackage[utf8]{inputenc}
\usepackage[french]{babel}
\usepackage{geometry}
\usepackage{xcolor}
\geometry{margin=2.5cm}
\begin{document}
\title{Rapport d'analyse multi-agent}
\author{Généré par IA multi-modèles}
\date{\today}
\maketitle

\section*{Configuration utilisée}
""")
        f.write(f"Mode d'analyse : {mode['nom']}\n\n")
        f.write("Modèles IA par tâche :\n\\begin{itemize}\n")
        for tache, modele in config.modeles.items():
            f.write(f"\\item {tache.capitalize()} : {modele.upper()}\n")
        f.write("\\end{itemize}\n\n")
        
        f.write(r"\tableofcontents" + "\n\\newpage\n")
        f.write(r"\chapter*{Rapport global d'analyse du mémoire}" + "\n")
        
        for ch, syn in zip(chapitres, syntheses):
            f.write(f"\\section*{{{ch['titre']} ({ch['nb_mots']} mots)}}\n")
            texte_escape = syn.replace("_", "\\_").replace("%", "\\%").replace("&", "\\&").replace("#", "\\#")
            f.write(texte_escape + "\n\n")
        
        f.write(r"\chapter*{Proposition de plan restructuré}" + "\n")
        plan_escape = plan_restructure.replace("_", "\\_").replace("%", "\\%").replace("&", "\\&").replace("#", "\\#")
        f.write(plan_escape + "\n\n")
        f.write(r"\end{document}")
    
    print(f"✅ Rapport LaTeX : {chemin_rapport}")

# ===============================================================
# LOGGER
# ===============================================================

class Logger:
    """Enregistre les étapes de l'analyse"""
    
    def __init__(self, chemin: str):
        self.chemin = chemin
        self.debut = time.time()
        with open(self.chemin, "w", encoding="utf-8") as f:
            f.write("="*60 + "\n")
            f.write("LOG D'ANALYSE MULTI-AGENT\n")
            f.write("="*60 + "\n\n")
            f.write(f"Début : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    def log(self, message: str):
        """Ajoute une entrée au log"""
        with open(self.chemin, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    
    def fin(self):
        """Marque la fin de l'analyse"""
        duree = time.time() - self.debut
        with open(self.chemin, "a", encoding="utf-8") as f:
            f.write(f"\nFin : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Durée totale : {duree:.1f} secondes ({duree/60:.1f} minutes)\n")

# ===============================================================
# ORCHESTRATION PRINCIPALE
# ===============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 ANALYSEUR MULTI-AGENT IA - VERSION 2.1 OPTIMISÉE")
    print("=" * 60)
    print("\n✨ Nouveautés V2.1 :")
    print("  • Modes d'analyse (Rapide/Normal/Détaillé)")
    print("  • Groupement par chapitre")
    print("  • Filtrage sections courtes")
    print("  • Estimation du temps")
    
    # Choix du mode d'analyse
    mode = ModeAnalyse.choisir_mode()
    print(f"\n✅ Mode sélectionné : {mode['nom']}")
    print(f"   Durée estimée : {mode['duree_estimee']}")
    
    # Configuration des modèles
    config = ConfigModeles()
    config.configurer_interactive()
    
    # Lecture du fichier
    print("\n" + "="*60)
    fichier = input("📄 Nom du fichier .tex à analyser : ").strip()
    if not os.path.exists(fichier):
        print(f"❌ Fichier '{fichier}' introuvable.")
        exit(1)
    
    # Extraction optimisée
    contenu = lire_latex(fichier)
    chapitres = extraire_chapitres_optimise(contenu, mode)
    
    # Affichage du résumé
    print(f"\n📊 Résumé de l'analyse :")
    print(f"   • Mode : {mode['nom']}")
    print(f"   • Sections à analyser : {len(chapitres)}")
    total_mots = sum(ch['nb_mots'] for ch in chapitres)
    print(f"   • Mots totaux : {total_mots:,}")
    print(f"   • Durée estimée : {estimer_duree(len(chapitres), config)}")
    
    # Confirmation
    continuer = input("\nContinuer avec cette analyse ? [O/n] : ").strip().lower()
    if continuer in ['n', 'non', 'no']:
        print("❌ Analyse annulée.")
        exit(0)
    
    # Création de la structure de dossiers
    dossiers = GestionnaireDossiers(fichier, mode)
    dossiers.sauvegarder_config(config, fichier, mode, len(chapitres))
    
    # Initialisation du logger
    logger = Logger(dossiers.chemin_log())
    logger.log(f"Analyse du fichier : {fichier}")
    logger.log(f"Mode : {mode['nom']}, {len(chapitres)} sections")
    
    # Analyse du plan global
    print("\n🧭 Génération du plan restructuré global...")
    plan_text = "\n".join([f"{c['type']}: {c['titre']} ({c['nb_mots']} mots)" for c in chapitres])
    logger.log(f"Analyse du plan avec {config.modeles['plan'].upper()}")
    plan_restructure = agent_plan(plan_text, model=config.modeles['plan'])
    
    # Analyse chapitre par chapitre
    syntheses = []
    temps_debut_analyse = time.time()
    
    for i, ch in enumerate(chapitres, 1):
        temps_debut_section = time.time()
        print(f"\n🔎 Analyse {i}/{len(chapitres)} : {ch['titre'][:60]}... ({ch['nb_mots']} mots)")
        logger.log(f"Début analyse chapitre {i}: {ch['titre']}")
        
        print(f"   → Agent scientifique ({config.modeles['scientifique'].upper()})...")
        sci = agent_scientifique(ch["texte"], model=config.modeles['scientifique'])
        
        print(f"   → Agent stylistique ({config.modeles['style'].upper()})...")
        sty = agent_style(ch["texte"], model=config.modeles['style'])
        
        print(f"   → Synthèse finale ({config.modeles['synthese'].upper()})...")
        syn = agent_synthese(ch["titre"], [sci, sty], model=config.modeles['synthese'])
        syntheses.append(syn)
        
        # Sauvegarde individuelle
        chemin_synthese = dossiers.chemin_synthese(i, config)
        with open(chemin_synthese, "w", encoding="utf-8") as f:
            f.write(f"{'='*60}\n")
            f.write(f"CHAPITRE {i} : {ch['titre']}\n")
            f.write(f"Type : {ch['type']} | Mots : {ch['nb_mots']}\n")
            f.write(f"{'='*60}\n\n")
            f.write(f"--- ANALYSE SCIENTIFIQUE ({config.modeles['scientifique'].upper()}) ---\n{sci}\n\n")
            f.write(f"--- ANALYSE STYLISTIQUE ({config.modeles['style'].upper()}) ---\n{sty}\n\n")
            f.write(f"--- SYNTHÈSE FINALE ({config.modeles['synthese'].upper()}) ---\n{syn}\n")
        
        temps_fin_section = time.time()
        duree_section = temps_fin_section - temps_debut_section
        temps_restant = (len(chapitres) - i) * duree_section
        
        print(f"   ✅ Sauvegardé ({duree_section:.1f}s) | Temps restant estimé: {temps_restant/60:.1f} min")
        logger.log(f"Chapitre {i} terminé en {duree_section:.1f}s")
    
    # Génération du rapport final
    print("\n📝 Génération du rapport final...")
    ecrire_rapport_latex(chapitres, syntheses, plan_restructure, dossiers, config, mode)
    logger.log("Rapport LaTeX généré")
    
    # Statistiques finales
    temps_total = time.time() - temps_debut_analyse
    logger.fin()
    
    print("\n" + "=" * 60)
    print("🏁 ANALYSE TERMINÉE AVEC SUCCÈS !")
    print("=" * 60)
    print(f"\n⏱️  Statistiques :")
    print(f"   • Sections analysées : {len(chapitres)}")
    print(f"   • Temps total : {temps_total/60:.1f} minutes")
    print(f"   • Temps moyen/section : {temps_total/len(chapitres):.1f} secondes")
    print(f"\n📁 Tous les fichiers sont dans : {dossiers.dossier_principal}/")
    print(f"\n💡 Conseil : Consultez 'configuration.txt' pour voir les détails")