# 🔐 Configuration de Gemini API (Optionnel)

## ⚠️ Vous N'Avez PAS Besoin de Faire Cela

Votre système fonctionne déjà correctement avec **Claude + OpenAI**. Cette guide est **optionnel** si vous voulez améliorer la qualité du style.

---

## 📊 Comparaison des Modèles

| Aspect | Claude 3.5 | GPT-4o | Gemini 2.0 |
|--------|-----------|--------|-----------|
| **Analyse scientifique** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Style et rédaction** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Synthèse** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Coût** | Moyen | Élevé | Faible |
| **Vitesse** | Rapide | Rapide | Très rapide |

**Recommandation :** Vous avez déjà les meilleurs modèles disponibles.

---

## 🎯 Si Vous Voulez Ajouter Gemini

### Étape 1 : Créer une Clé API Google

1. Allez sur [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Cliquez sur **"Create API Key"**
3. Sélectionnez **"Create API key in new project"**
4. Copiez la clé générée

### Étape 2 : Configurer la Variable d'Environnement

#### Sur Windows (PowerShell)
```powershell
[System.Environment]::SetEnvironmentVariable("GEMINI_API_KEY","votre_clé_ici","User")
```

Puis relancez votre terminal.

#### Sur Linux/Mac
```bash
# Ajoutez à ~/.bashrc ou ~/.zshrc
export GEMINI_API_KEY="votre_clé_ici"

# Appliquez les changements
source ~/.bashrc  # ou source ~/.zshrc
```

#### Vérifier que c'est configuré
```bash
python3 -c "import os; print('✅' if os.getenv('GEMINI_API_KEY') else '❌')"
```

### Étape 3 : Tester
```bash
python3 agent_multi_models_v3.2_final.py --auto
```

Vous devriez voir :
```
✅ Gemini initialisé (gemini-2.0-flash)
```

---

## ⚡ Modèles Gemini Disponibles (en ordre de priorité)

Le script essaie dans cet ordre :

1. **gemini-2.0-flash** ⚡ (Nouveau, ultra-rapide, recommandé)
2. **gemini-1.5-flash** (Équilibre vitesse/qualité)
3. **gemini-1.5-pro** (Haute qualité, plus lent)

---

## 💡 Cas d'Usage pour Gemini

Utilisez Gemini si vous cherchez :
- ✅ Meilleure qualité de style (rédaction académique)
- ✅ Rapidité maximale
- ✅ Coûts minimaux
- ✅ Analyse de contenu créatif

**NON recommandé pour :**
- Analyse mathématique rigoureuse → Claude
- Tâches analytiques complexes → Claude

---

## 🆚 Configuration Finale Recommandée

```python
# Avec Gemini (optimal)
"scientifique": "claude",    # Analyse rigoureuse
"style": "gemini",           # Rédaction créative
"synthese": "claude",        # Synthèse logique

# Sans Gemini (ce que vous avez, c'est bien aussi)
"scientifique": "claude",    # Analyse rigoureuse
"style": "openai",           # Rédaction professionnelle
"synthese": "claude",        # Synthèse logique
```

---

## ⚠️ Conseils de Sécurité

- **Ne committez jamais votre clé API** dans Git
- **Ne la partagez avec personne**
- Si compromise : régénérez-la sur [Google AI Studio](https://aistudio.google.com/app/apikey)
- Utilisez des variables d'environnement, **jamais** des literals en dur

---

## 🆘 Si Ça Ne Marche Pas

### Erreur : "API key not valid"
```
→ Vérifiez que vous avez copié la clé correctement
→ Vérifiez la variable d'environnement: echo $GEMINI_API_KEY
```

### Erreur : "Model not found"
```
→ C'est OK ! Le script bascule automatiquement sur OpenAI
→ Votre système fonctionne parfaitement sans Gemini
```

### Erreur : "Rate limit exceeded"
```
→ Attendez 60 secondes
→ Ou passez à OpenAI (déjà configuré)
```

---

## 📚 Ressources

- [Google AI Studio](https://aistudio.google.com/app/apikey) - Créer une clé API
- [Documentation Gemini](https://ai.google.dev/docs) - Guide complet
- [Pricing Gemini](https://ai.google.dev/pricing) - Coûts

---

## ✨ TL;DR

- Vous n'avez **PAS BESOIN** de Gemini pour que ça marche
- Si vous le voulez : récupérez une clé gratuite sur [Google AI Studio](https://aistudio.google.com/app/apikey)
- Ajoutez `export GEMINI_API_KEY="votre_clé"` à votre shell
- C'est tout ! Le script fera le reste automatiquement
