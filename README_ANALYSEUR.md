# 🤖 Analyseur Multi-Modèles IA – Guide d'Utilisation

## Vue d'ensemble

L'**Analyseur Multi-Modèles IA v3.2** est un outil académique avancé qui analyse automatiquement des documents LaTeX en utilisant plusieurs modèles d'IA (Claude, OpenAI/GPT-4o, Gemini) pour :

- ✅ **Analyse scientifique** : Rigueur mathématique et méthodologique
- ✅ **Critique stylistique** : Clarté, fluidité et structure rédactionnelle
- ✅ **Synthèse académique** : Résumé critique des points clés
- ✅ **Génération de rapports** : HTML professionnel + JSON structuré

---

## 📋 Versions disponibles

| Version | Fichier | Utilisation |
|---------|---------|-------------|
| **v3.2 Final** | `agent_multi_models_v3.2_final.py` | 🎯 **RECOMMANDÉE** - Complète avec toutes les améliorations |
| **v3.1** | `agent_multi_models_v3.1.py` | Génération HTML/PDF sans dépendances |
| **v3.0** | `agent_multi_models_v3.0.py` | Avec ReportLab (PDF natif) |
| **v2.1.1** | `agent_multi_models_v2.1.1.py` | Version originale (API uniquement) |
| **DÉMO** | `agent_multi_models_demo.py` | Version démo - test sans API |

---

## 🚀 Démarrage rapide

### 1. **Mode DÉMO** (sans clés API)

Parfait pour tester sans avoir besoin de clés d'API :

```bash
python3 agent_multi_models_demo.py
```

**Ce que ça fait :**
- Lit le fichier `Manuscript28octobre2025.tex`
- Extrait les 5 premiers chapitres/sections
- Génère des analyses simulées
- Crée un rapport HTML professionnel
- Sauvegarde un fichier JSON avec les résultats

**Résultat :**
- 📄 `rapports/rapport_demo_TIMESTAMP.html`
- 📊 `rapports/rapport_demo_TIMESTAMP.json`

---

### 2. **Mode RÉEL** (avec clés API)

Pour une analyse réelle avec les modèles d'IA :

#### Étape 1 : Configurer les clés API

```bash
# Linux/macOS
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export GEMINI_API_KEY="..."

# Windows (CMD)
set ANTHROPIC_API_KEY=sk-ant-...
set OPENAI_API_KEY=sk-...
set GEMINI_API_KEY=...
```

#### Étape 2 : Exécuter le script

```bash
# Mode interactif
python3 agent_multi_models_v3.2_final.py

# Mode automatique (rapide)
python3 agent_multi_models_v3.2_final.py --auto
```

#### Étape 3 : Suivre l'analyse

Le script affichera :
```
🔎 1/10: Introduction et mise en contexte (320 mots)
   ✅ Terminé (1/10)
🔎 2/10: Genèse et évolution ...
   ...
⏱️ Temps total : 4.5 min
📈 Appels API : 30 | Erreurs : 0 | Succès : 100%
🏁 Analyse complète.
```

---

## 📊 Modes d'analyse

Choisissez le niveau de détail selon votre besoin :

### Mode **Rapide** ⚡
- **Contenu** : Chapitres uniquement
- **Durée** : 5–10 min
- **Cas d'usage** : Vue d'ensemble rapide

### Mode **Normal** ⭐ (par défaut)
- **Contenu** : Chapitres + sections principales
- **Durée** : 10–20 min
- **Cas d'usage** : Analyse équilibrée

### Mode **Détaillé** 🔬
- **Contenu** : Tout (chapitres, sections, sous-sections)
- **Durée** : 20–40 min
- **Cas d'usage** : Analyse complète et fine

---

## 🔧 Configuration des modèles

Par défaut, la configuration est :

| Tâche | Modèle |
|-------|--------|
| Analyse scientifique | Claude (Sonnet 3.5) |
| Critique stylistique | Gemini 1.5 Pro |
| Analyse du plan | Claude (Sonnet 3.5) |
| Synthèse | Claude (Sonnet 3.5) |

**Pour modifier** : Lors de l'exécution interactive, répondez "non" à la configuration par défaut.

---

## 📁 Fichiers générés

### Après l'analyse, vous obtenez :

```
rapports/
├── rapport_analyse_20251105_173852.html    ← Rapport HTML professionnel
├── rapport_analyse_20251105_173852.json    ← Données structurées
└── (optionnel) rapport_analyse_20251105_173852.pdf   ← PDF converti
```

### Contenu du rapport HTML :

1. **En-tête** : Métadonnées (fichier, date, mode)
2. **Statistiques globales** : Temps total, appels API, taux de succès
3. **Analyses par chapitre** :
   - ✓ Rigueur scientifique
   - ✓ Style et clarté
   - ✓ Synthèse critique

---

## 💾 Exporter en PDF

### Option 1 : Navigateur (Recommandé ✅)

```
1. Ouvre le fichier HTML dans un navigateur (Chrome, Firefox, etc.)
2. Fichier → Imprimer → Enregistrer en PDF
3. Paramètres : Format = A4, Marges = Normal
```

### Option 2 : Ligne de commande

Si `wkhtmltopdf` ou `weasyprint` sont installés :

```bash
python3 converter_html_to_pdf.py rapports/rapport.html rapports/rapport.pdf
```

### Option 3 : Installer les outils

```bash
# Ubuntu/Debian
sudo apt-get install wkhtmltopdf

# Ou avec pip
pip install weasyprint
```

---

## 📊 Résultats JSON

Le fichier JSON contient :

```json
{
  "metadata": {
    "fichier_source": "Manuscript28octobre2025.tex",
    "mode_analyse": "Normal",
    "date": "2025-11-05T17:38:52.123456"
  },
  "statistiques": {
    "temps_total_min": 4.5,
    "nb_appels": 30,
    "nb_erreurs": 0,
    "taux_succes": 100.0
  },
  "resultats": [
    {
      "chapitre": "Introduction et mise en contexte",
      "scientifique": "L'analyse scientifique montre...",
      "style": "Le style du chapitre...",
      "synthese": "En synthèse..."
    },
    ...
  ]
}
```

---

## 🔄 Système de Fallback automatique

Si un modèle n'est pas disponible ou échoue :

```
Claude → OpenAI → Gemini → Claude (cycle automatique)
```

Le script affichera :
```
⚠️ Tentative 1/3 échouée (claude): [erreur]
🔄 Basculement vers OPENAI...
```

---

## ⚙️ Améliorations principales (v3.2)

✅ **Génération HTML** : Rapport professionnel avec CSS intégré
✅ **Statistiques détaillées** : Temps, tokens, taux de succès
✅ **Gestion d'erreurs robuste** : Retry + Fallback automatique
✅ **Mode DÉMO** : Test sans API
✅ **JSON structuré** : Exporte complètement les résultats
✅ **Support multi-encodages** : UTF-8, Latin-1, CP1252
✅ **Mode automatique** : `--auto` pour exécution sans interaction

---

## 🐛 Dépannage

### Problème : "Fichier introuvable"
```
❌ Fichier introuvable : Manuscript28octobre2025.tex
```

**Solution :**
- Vérifiez que le fichier `.tex` est dans le répertoire courant
- Ou donnez le chemin complet : `/chemin/vers/fichier.tex`

### Problème : "Modèle non disponible"
```
⚠️ Claude non disponible : 401 Invalid API key
```

**Solution :**
- Vérifiez votre clé API
- Testez avec le mode DÉMO d'abord : `python3 agent_multi_models_demo.py`

### Problème : "Aucune section détectée"
```
⚠️ Aucune section détectée. Vérifie ton fichier.
```

**Solution :**
- Le fichier LaTeX doit contenir `\chapter{}`, `\section{}` ou `\subsection{}`
- Testez le fichier : `python3 -c "import re; print(len(re.findall(r'\\\\(chapter|section)', open('fichier.tex').read())))"`

---

## 📚 Exemple complet

```bash
# 1. Tester avec DÉMO
python3 agent_multi_models_demo.py

# 2. Configurer les clés API
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export GEMINI_API_KEY="..."

# 3. Exécuter en mode automatique
python3 agent_multi_models_v3.2_final.py --auto

# 4. Vérifier les résultats
ls -lh rapports/
cat rapports/rapport_analyse_*.json | python3 -m json.tool

# 5. Exporter en PDF
python3 converter_html_to_pdf.py rapports/rapport_analyse_*.html
```

---

## 📞 Support & Feedback

- **Erreurs** : Vérifiez les logs dans le répertoire `logs/`
- **Améliorations** : Modifiez les prompts dans les fonctions `agent_*`
- **Performance** : Utilisez le mode "Rapide" pour documents grands

---

## 📄 Licence & Utilisation

Ce script est conçu pour :
- ✅ L'analyse académique de manuscrits
- ✅ La relecture scientifique automatisée
- ✅ La génération de rapports critiques

**Nota bene** : Respectez les conditions d'utilisation des API (Anthropic, OpenAI, Google).

---

## 🎯 Prochaines étapes

1. **Essayez le DÉMO** : `python3 agent_multi_models_demo.py`
2. **Configurez vos clés API**
3. **Lancez l'analyse complète** : `python3 agent_multi_models_v3.2_final.py --auto`
4. **Exportez en PDF** via navigateur ou ligne de commande

**Bonne analyse ! 🚀**
