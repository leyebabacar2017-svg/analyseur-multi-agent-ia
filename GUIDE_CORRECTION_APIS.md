# 🔧 Guide de Correction des APIs

## État Actuel (Nov 6, 2025)

```
✅ OpenAI       → FONCTIONNE
❌ Claude       → ERREUR 404 (Clé invalide)
❌ Gemini       → NON CONFIGURÉ
```

---

## 🔴 Problème 1: Claude API - Erreur 404

### Diagnostic
- **Clé détectée**: Oui (108 caractères)
- **Format**: Valide (`sk-ant-*`)
- **Erreur**: HTTP 404 Not Found
- **Cause probable**: Clé API invalide ou accès restreint au modèle

### Solutions

#### Option A - Créer une nouvelle clé Claude
1. Allez sur [Claude Console](https://console.anthropic.com)
2. Connectez-vous avec votre compte
3. Allez dans "API Keys"
4. Cliquez sur "Create Key"
5. Copiez la nouvelle clé

#### Option B - Vérifier votre clé existante
1. Vérifiez que la clé commence par `sk-ant-`
2. Vérifiez qu'elle ne contient pas de caractères invisibles
3. Vérifiez que votre compte a accès au modèle `claude-3-5-sonnet`

#### Option C - Configurer la nouvelle clé
```bash
export ANTHROPIC_API_KEY="votre_nouvelle_cle_ici"
python3 diagnose_apis.py  # Tester
python3 correcteur_final.py  # Utiliser
```

---

## 🔴 Problème 2: Gemini API - Non Configuré

### Diagnostic
- **Clé détectée**: Non (0 caractères)
- **Status**: À configurer

### Solutions

#### Étape 1: Créer une clé API Google
1. Allez sur [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Cliquez sur "Create API Key"
3. Sélectionnez ou créez un projet
4. Copiez la clé générée (commence par `AIza`)

#### Étape 2: Configurer la clé
```bash
export GEMINI_API_KEY="AIza_votre_cle_ici"
python3 diagnose_apis.py  # Tester
```

#### Étape 3: Vérifier
La sortie devrait afficher:
```
✅ GEMINI
```

---

## ✅ OpenAI - Déjà Fonctionnel

**Status**: ✅ **FONCTIONNE PARFAITEMENT**

Vous pouvez commencer à utiliser le correcteur immédiatement!

```bash
python3 correcteur_final.py
```

---

## 📋 Configuration Complète Recommandée

```bash
# Export toutes les clés
export OPENAI_API_KEY="sk-proj-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="AIza-..."

# Vérifier
python3 diagnose_apis.py

# Utiliser le correcteur
python3 correcteur_final.py
```

---

## 🚀 Démarrage Rapide

### Si vous n'avez que OpenAI (cas actuel)
```bash
python3 correcteur_final.py
# Fonctionnera parfaitement avec OpenAI
```

### Si vous avez OpenAI + Gemini
```bash
export GEMINI_API_KEY="AIza-..."
python3 diagnose_apis.py
python3 correcteur_final.py
```

### Si vous avez tous les APIs
```bash
export OPENAI_API_KEY="sk-proj-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="AIza-..."
python3 diagnose_apis.py
python3 correcteur_final.py
```

---

## 📞 Support

### Vérifier les clés
```bash
python3 diagnose_apis.py
```

### Recréer les exports
```bash
source /tmp/setup_api_keys.sh
```

### Utiliser le correcteur
```bash
python3 correcteur_final.py
```

---

## 🔒 Sécurité

⚠️ **Ne committez JAMAIS vos clés API dans Git!**

1. Ajoutez à `.gitignore`:
```
*.sh
.env
.env.local
```

2. Utilisez des variables d'environnement:
```bash
export ANTHROPIC_API_KEY="..."  # Mieux
ANTHROPIC_API_KEY="..." python3 script.py  # Encore mieux
```

3. Si compromise: Régénérez la clé sur:
   - [Claude Console](https://console.anthropic.com) pour Claude
   - [OpenAI Dashboard](https://platform.openai.com/api-keys) pour OpenAI
   - [Google AI Studio](https://aistudio.google.com/app/apikey) pour Gemini

---

## ✨ Prochaines Étapes

1. **IMMÉDIAT**: Testez avec OpenAI (déjà fonctionnel)
   ```bash
   python3 correcteur_final.py
   ```

2. **OPTIONNEL**: Récupérez une clé Gemini gratuite
   - [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Copiez-collez la clé
   - `export GEMINI_API_KEY="AIza-..."`

3. **OPTIONNEL**: Corrigez la clé Claude
   - Créez une nouvelle clé
   - [Claude Console](https://console.anthropic.com)
   - `export ANTHROPIC_API_KEY="sk-ant-..."`

---

**Vous êtes prêt à commencer!** 🎉
