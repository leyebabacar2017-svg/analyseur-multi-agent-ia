#!/usr/bin/env python3
"""
Diagnostic complet de toutes les APIs
"""

import os
import json
import urllib.request

print("=" * 70)
print("🔍 DIAGNOSTIC COMPLET DES APIs")
print("=" * 70)

OPENAI_KEY = os.getenv("OPENAI_API_KEY", "").strip()
CLAUDE_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "").strip()

print("\n📋 CLÉS CONFIGURÉES:")
print(f"  OpenAI:  {len(OPENAI_KEY)} chars - {'✅' if OPENAI_KEY else '❌'}")
print(f"  Claude:  {len(CLAUDE_KEY)} chars - {'✅' if CLAUDE_KEY else '❌'}")
print(f"  Gemini:  {len(GEMINI_KEY)} chars - {'✅' if GEMINI_KEY else '❌'}")

results = {}

# Test OpenAI
print("\n🧪 TEST 1: OpenAI API")
try:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
    data = {"model": "gpt-4o", "max_tokens": 20, "messages": [{"role": "user", "content": "ok"}]}
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
    with urllib.request.urlopen(req, timeout=10) as response:
        result = json.loads(response.read().decode('utf-8'))
        print("   ✅ FONCTIONNE!")
        print(f"      Réponse: {result['choices'][0]['message']['content']}")
        results['openai'] = True
except urllib.error.HTTPError as e:
    print(f"   ❌ ERREUR HTTP {e.code}")
    results['openai'] = False
except Exception as e:
    print(f"   ❌ ERREUR: {str(e)[:80]}")
    results['openai'] = False

# Test Claude
print("\n🧪 TEST 2: Claude API")
try:
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": CLAUDE_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    data = {"model": "claude-opus-4-1", "max_tokens": 20, "messages": [{"role": "user", "content": "ok"}]}
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
    with urllib.request.urlopen(req, timeout=10) as response:
        result = json.loads(response.read().decode('utf-8'))
        print("   ✅ FONCTIONNE!")
        print(f"      Réponse: {result['content'][0]['text']}")
        results['claude'] = True
except urllib.error.HTTPError as e:
    print(f"   ❌ ERREUR HTTP {e.code}")
    print(f"      Cause: Clé invalide ou accès restreint")
    results['claude'] = False
except Exception as e:
    print(f"   ❌ ERREUR: {str(e)[:80]}")
    results['claude'] = False

# Test Gemini
print("\n🧪 TEST 3: Gemini API")
if GEMINI_KEY and "AIza" in GEMINI_KEY:
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": "ok"}]}], "generationConfig": {"maxOutputTokens": 20}}
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            print("   ✅ FONCTIONNE!")
            print(f"      Réponse: {result['candidates'][0]['content']['parts'][0]['text']}")
            results['gemini'] = True
    except urllib.error.HTTPError as e:
        print(f"   ❌ ERREUR HTTP {e.code}")
        results['gemini'] = False
    except Exception as e:
        print(f"   ❌ ERREUR: {str(e)[:80]}")
        results['gemini'] = False
else:
    print("   ⚠️ Clé Gemini manquante ou invalide")
    results['gemini'] = False

# Résumé final
print("\n" + "=" * 70)
print("📊 RÉSUMÉ FINAL")
print("=" * 70)

count_ok = sum(1 for v in results.values() if v)
total = len(results)

print(f"\n✅ APIs fonctionnels: {count_ok}/{total}")
for api, ok in results.items():
    status = "✅" if ok else "❌"
    print(f"   {status} {api.upper()}")

if count_ok == 0:
    print("\n❌ AUCUNE API NE FONCTIONNE!")
    print("   Vérifiez vos clés API")
elif count_ok == total:
    print(f"\n✅ TOUS LES APIS FONCTIONNENT!")
    print(f"   Vous pouvez utiliser: python3 correcteur_final.py")
else:
    print(f"\n⚠️ {count_ok}/{total} APIs fonctionnels")
    print(f"   Le correcteur utilisera les APIs disponibles")
    print(f"   Vous pouvez utiliser: python3 correcteur_final.py")

print("\n" + "=" * 70)
