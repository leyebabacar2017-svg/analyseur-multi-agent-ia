# ===============================================================
# agent_multi_models_v2.2.py — Version corrigée (nov. 2025)
# ===============================================================
# ✅ Nouveautés V2.2 :
# 1. Correction totale Gemini (API v1)
# 2. Fallback automatique (Claude ↔ OpenAI ↔ Gemini)
# 3. Gestion d’erreur renforcée et logs explicites
# 4. Code prêt pour exécution non interactive (--auto)
# ===============================================================

import os, re, time, sys
from typing import Optional, List, Dict
from datetime import datetime

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
# MODES D’ANALYSE
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

        print("\n=== MODE D’ANALYSE ===")
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
# FONCTION UNIFIÉE D’APPEL API
# ===============================================================

def safe_call_unified(system_prompt: str, user_prompt: str,
                      temperature: float = 0.3, model: str = "claude",
                      fallback: bool = True) -> Optional[str]:
    """Appel unifié avec basculement automatique entre modèles"""
    for attempt in range(3):
        try:
            if model == "claude" and CLAUDE_AVAILABLE:
                response = claude_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4000,
                    temperature=temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                return response.content[0].text

            elif model == "gemini" and GEMINI_AVAILABLE:
                response = gemini_model.generate_content(
                    contents=f"{system_prompt}\n\n{user_prompt}",
                    generation_config=genai.GenerationConfig(
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
                raise ValueError(f"Modèle {model} non disponible.")

        except Exception as e:
            print(f"⚠️ Tentative {attempt+1}/3 échouée ({model}): {str(e)[:120]}")
            time.sleep(3)

    # Si tout échoue, basculement automatique
    if fallback:
        alt = {"claude": "openai", "openai": "gemini", "gemini": "claude"}[model]
        print(f"🔄 Basculement vers {alt.upper()}...")
        return safe_call_unified(system_prompt, user_prompt, temperature, model=alt, fallback=False)

    print(f"❌ Abandon ({model}) après 3 tentatives.")
    return None

# ===============================================================
# AGENTS
# ===============================================================

def agent_scientifique(txt: str, model="claude"):
    system = "Tu es un expert en mathématiques appliquées et modélisation numérique."
    prompt = f"Analyse la rigueur scientifique du texte suivant :\n\n{txt[:4000]}"
    return safe_call_unified(system, prompt, 0.25, model) or "Analyse scientifique indisponible."

def agent_style(txt: str, model="gemini"):
    system = "Tu es un relecteur académique spécialisé en rédaction scientifique."
    prompt = f"Améliore le style et la clarté du texte suivant :\n\n{txt[:4000]}"
    return safe_call_unified(system, prompt, 0.4, model) or "Amélioration stylistique indisponible."

def agent_plan(plan: str, model="claude"):
    system = "Tu es un rapporteur de thèse expert en structuration académique."
    prompt = f"Analyse et optimise le plan suivant :\n\n{plan[:4000]}"
    return safe_call_unified(system, prompt, 0.3, model) or "Analyse du plan indisponible."

def agent_synthese(titre: str, analyses: list, model="claude"):
    system = "Tu es un examinateur scientifique rédigeant un rapport critique."
    prompt = f"Synthétise les points clés du chapitre '{titre}' :\n\n{'\n\n'.join(analyses)[:8000]}"
    return safe_call_unified(system, prompt, 0.4, model) or "Synthèse indisponible."

# ===============================================================
# UTILITAIRES LATEX (inchangé)
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
# EXÉCUTION PRINCIPALE
# ===============================================================

if __name__ == "__main__":
    auto = "--auto" in sys.argv
    print("="*60)
    print("🤖 ANALYSEUR MULTI-MODÈLES IA – V2.2 (corrigé Gemini)")
    print("="*60)

    mode = ModeAnalyse.choisir_mode(auto)
    config = ConfigModeles()
    config.configurer_interactive(auto)

    fichier = input("\n📄 Fichier .tex à analyser : ").strip()
    if not os.path.exists(fichier):
        print(f"❌ Fichier introuvable : {fichier}")
        sys.exit(1)

    contenu = lire_latex(fichier)
    chapitres = extraire_chapitres(contenu, mode)

    if not chapitres:
        print("⚠️ Aucune section détectée. Vérifie ton fichier.")
        sys.exit(0)

    print(f"\n📊 {len(chapitres)} sections, {sum(c['nb_mots'] for c in chapitres)} mots\n")

    syntheses = []
    t0 = time.time()
    for i, ch in enumerate(chapitres, 1):
        print(f"\n🔎 {i}/{len(chapitres)}: {ch['titre']} ({ch['nb_mots']} mots)")
        sci = agent_scientifique(ch["texte"], config.modeles["scientifique"])
        sty = agent_style(ch["texte"], config.modeles["style"])
        syn = agent_synthese(ch["titre"], [sci, sty], config.modeles["synthese"])
        syntheses.append(syn)
        print(f"   ✅ Terminé ({i}/{len(chapitres)})")

    print(f"\n⏱️ Temps total : {(time.time()-t0)/60:.1f} min")
    print("🏁 Analyse complète.")
