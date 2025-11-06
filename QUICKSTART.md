# ⚡ Démarrage rapide – 5 minutes

## 🚀 Option 1 : Test immédiat (DÉMO)

**Pas besoin de configuration !**

```bash
python3 agent_multi_models_demo.py
```

**Résultat en < 1 seconde :**
```
✅ Rapport HTML généré
✅ Données JSON sauvegardées
📄 Fichiers dans : rapports/
```

**Ouvrir le rapport :**
```bash
# Linux/Mac
open rapports/rapport_demo_*.html

# Windows
start rapports\rapport_demo_*.html

# Ou dans votre navigateur
# Glissez-déposez le fichier .html
```

---

## 🔧 Option 2 : Utilisation réelle (avec API)

### Étape 1 : Configurer les clés (< 2 min)

Obtenez vos clés API :
- **Claude** : https://console.anthropic.com
- **OpenAI** : https://platform.openai.com/api-keys
- **Gemini** : https://ai.google.dev

Puis :

```bash
# Linux/macOS
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export GEMINI_API_KEY="AIzaSy..."

# Windows (CMD)
set ANTHROPIC_API_KEY=sk-ant-...
set OPENAI_API_KEY=sk-...
set GEMINI_API_KEY=AIzaSy...

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="sk-ant-..."
$env:OPENAI_API_KEY="sk-..."
$env:GEMINI_API_KEY="AIzaSy..."
```

### Étape 2 : Lancer l'analyse (< 3 min)

```bash
# Mode automatique (rapide, pas de questions)
python3 agent_multi_models_v3.2_final.py --auto

# Ou mode interactif
python3 agent_multi_models_v3.2_final.py
```

### Étape 3 : Récupérer les résultats

```bash
# Voir les fichiers générés
ls -lh rapports/

# Ouvrir le rapport HTML
open rapports/rapport_analyse_*.html
```

---

## 📊 Résultats attendus

### Après exécution en mode DÉMO

```
✅ Rapport HTML (14 KB)
✅ Données JSON (6 KB)
⏱️ Temps : < 1 seconde
📝 Sections analysées : 5
```

### Après exécution réelle (mode Normal, 10 chapitres)

```
✅ Rapport HTML (30-50 KB)
✅ Données JSON (15-30 KB)
⏱️ Temps : 10-20 minutes
📝 Sections analysées : 10
💰 Coût API : ~$2-5
```

---

## 🎯 Prochaines étapes

### Pour approfondir
1. Lisez `README_ANALYSEUR.md` (guide complet)
2. Consultez `AMELIORATIONS.md` (détails techniques)
3. Explorez les scripts dans `agent_multi_models_v*.py`

### Pour exporter en PDF
```bash
# Option 1 : Navigateur
# Fichier → Imprimer → Enregistrer en PDF

# Option 2 : Python (si weasyprint/reportlab installé)
python3 converter_html_to_pdf.py rapports/rapport.html
```

### Pour personnaliser
- **Modifier le fichier à analyser** : Changez le chemin dans le script
- **Changer les modèles IA** : Répondez différemment aux questions
- **Ajuster les modes** : Choisissez Rapide/Normal/Détaillé

---

## 🆘 Problèmes ?

### "Fichier introuvable"
```bash
# Vérifiez que Manuscript28octobre2025.tex existe
ls Manuscript28octobre2025.tex

# Sinon, modifiez le chemin dans le script
```

### "Clé API invalide"
```bash
# Testez d'abord en mode DÉMO
python3 agent_multi_models_demo.py

# Vérifiez vos clés
echo $ANTHROPIC_API_KEY
```

### "Aucune section détectée"
```bash
# Le fichier LaTeX doit avoir \chapter{} ou \section{}
# Vérifiez le contenu du fichier
head -50 Manuscript28octobre2025.tex
```

---

## 📚 Fichiers utiles

| Fichier | Usage |
|---------|-------|
| `agent_multi_models_demo.py` | Test rapide sans API |
| `agent_multi_models_v3.2_final.py` | Version complète (recommandée) |
| `README_ANALYSEUR.md` | Guide d'utilisation |
| `AMELIORATIONS.md` | Détails des améliorations |
| `rapports/rapport_*.html` | Rapport généré (HTML) |
| `rapports/rapport_*.json` | Données brutes (JSON) |

---

## ⏱️ Temps estimé

| Tâche | Temps |
|-------|-------|
| Lire ce document | 2 min |
| Tester le DÉMO | 1 min |
| Configurer les clés | 5 min |
| Exécuter l'analyse | 10-20 min |
| Exporter en PDF | 2 min |
| **Total** | **~20-30 min** |

---

## ✅ Checklist

- [ ] Télécharger les scripts
- [ ] Tester avec `agent_multi_models_demo.py`
- [ ] Lire `README_ANALYSEUR.md`
- [ ] Configurer les clés API (optionnel)
- [ ] Exécuter l'analyse complète
- [ ] Ouvrir le rapport HTML
- [ ] Exporter en PDF (optionnel)

---

## 🎉 C'est tout !

Vous êtes prêt à analyser vos manuscrits !

**Commencez par :**
```bash
python3 agent_multi_models_demo.py
```

Pour plus d'informations, consultez `README_ANALYSEUR.md`.

---

**Questions fréquentes ?** → Voir `README_ANALYSEUR.md` section "Dépannage"
**Besoin d'aide ?** → Consultez les commentaires du code
**Envie de contribuer ?** → Modifiez les prompts dans les fonctions `agent_*`

Bonne utilisation ! 🚀
