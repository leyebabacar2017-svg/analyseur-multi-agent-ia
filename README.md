# 🤖 Correcteur IA Académique EXPERT v4.0

Analyseur multidimensionnel de textes académiques avec évaluation expert de niveau GPT-5.

## ✨ Fonctionnalités

### 📊 Analyse Multidimensionnelle (5 Dimensions)

1. **Analyse Conceptuelle et Scientifique**
   - Vérification de cohérence mathématique
   - Identification des failles théoriques
   - Évaluation de la pertinence des équations

2. **Analyse Logique et Méthodologique**
   - Évaluation de la progression des idées
   - Vérification de la cohérence argumentative
   - Détection des manques de justification

3. **Analyse Stylistique et Linguistique**
   - Clarté du discours
   - Fluidité rédactionnelle
   - Propositions de reformulation

4. **Appréciation Critique Globale**
   - Identification des forces et faiblesses
   - Suggestions d'amélioration concrètes
   - Hiérarchisation des priorités

5. **Évaluation Synthétique**
   - Clarté: ✅ bon / ⚠️ moyen / ❌ faible
   - Profondeur scientifique
   - Cohérence argumentative

### 🔌 APIs Intégrées

- **OpenAI** (gpt-4o) - Analyses rapides et expertises
- **Claude** (claude-opus-4-1) - Analyses scientifiques approfondies
- **Gemini** (gemini-2.0-flash) - Analyses stylistiques créatives

Fallback intelligent automatique en cas d'indisponibilité.

### 📁 Formats de Sortie

- **HTML** : Rapport professionnel, facilement imprimable en PDF
- **JSON** : Données structurées pour intégration ultérieure

## 🚀 Installation

### Prérequis

- Python 3.8+
- Clés API pour au moins une des plateformes (OpenAI, Claude, Gemini)

### Configuration des APIs

```bash
export OPENAI_API_KEY="sk-proj-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="AIza-..."
```

Ou créez un fichier `config_apis.sh` (ajouté à .gitignore):
```bash
#!/bin/bash
export OPENAI_API_KEY="votre_clé"
export ANTHROPIC_API_KEY="votre_clé"
export GEMINI_API_KEY="votre_clé"
```

Puis:
```bash
source config_apis.sh
```

## 📖 Utilisation

### Mode Expert (Recommandé)

```bash
python3 correcteur_expert_v4.py
# Sélectionnez votre fichier LaTeX à analyser
```

### Mode Simple

```bash
python3 correcteur_final.py
```

### Script Automatisé

```bash
bash run_expert.sh
```

### Analyser un fichier spécifique

```bash
python3 correcteur_expert_v4.py << 'EOF'
chemin/vers/fichier.tex
EOF
```

## 📊 Résultats

Les rapports sont générés dans le dossier `rapports/`:

```
rapports/
├── rapport_expert_20251106_195526.html
├── rapport_expert_20251106_195526.json
├── rapport_final_20251106_194041.html
└── rapport_final_20251106_194041.json
```

### Temps d'Exécution

- Par chapitre: ~30-50 secondes
- 5 chapitres: ~2.5 minutes
- Qualité: ⭐⭐⭐⭐⭐ Expert

## 🛠️ Architecture

### Scripts Principaux

| Script | Description | Usage |
|--------|-------------|-------|
| `correcteur_expert_v4.py` | Analyseur expert (5 dimensions) | Analyse complète |
| `correcteur_final.py` | Analyseur simple (3 analyses) | Analyse rapide |
| `diagnose_apis.py` | Test des APIs | Diagnostic |

### Support des Formats

- **Entrée**: Fichiers LaTeX (.tex)
- **Extraction**: Chapitres, sections, sous-sections
- **Sortie**: HTML + JSON

## 📋 Exemples d'Analyse

### Section "Introduction"

```
1️⃣ ANALYSE CONCEPTUELLE
   ✅ Cohérence des définitions
   ⚠️ Manque de détails théoriques
   ❌ Équation non justifiée

2️⃣ ANALYSE LOGIQUE
   ✅ Progression claire
   ⚠️ Transitions insuffisantes

3️⃣ ANALYSE STYLISTIQUE
   ✅ Clarté bonne
   ⚠️ Formulation à améliorer
   → Suggestion: "Ceci démontre que..."

4️⃣ APPRÉCIATION CRITIQUE
   Forces: Structure logique
   Faiblesses: Profondeur insuffisante
   Pistes: Ajouter exemples concrets

5️⃣ SYNTHÈSE
   Clarté: ✅ Bon
   Profondeur scientifique: ⚠️ Moyen
   Cohérence: ⚠️ Moyen
```

## 🔍 Diagnostic

Tester les APIs configurées:

```bash
python3 diagnose_apis.py
```

Sortie attendue:
```
✅ OPENAI - Fonctionnel
✅ CLAUDE - Fonctionnel
✅ GEMINI - Fonctionnel
```

## 🔐 Sécurité

⚠️ **Important**:
- Les clés API sont ajoutées à `.gitignore`
- Ne committez JAMAIS vos clés
- Utilisez des variables d'environnement
- Si compromission: régénérez les clés

## 📚 Documentation

- `EXPERT_V4_CHANGELOG.md` - Nouveautés v4.0
- `GUIDE_CORRECTION_APIS.md` - Guide complet APIs
- `STATUS_APIS.txt` - État des configurações
- `SYNTHESE_COMPLETE.txt` - Résumé complet

## 🤝 Contribution

Ce projet est privé. Reportez les issues via:
- Email
- Issues GitHub (repo privé)
- Discussions internes

## 📜 Licence

Propriétaire. Tous droits réservés.

## 👨‍💼 Auteur

Correcteur IA Académique EXPERT
Version 4.0 - Novembre 2025

---

**Status**: ✅ Opérationnel à 100%

Lancez: `python3 correcteur_expert_v4.py`
