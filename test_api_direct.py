#!/usr/bin/env python3
"""
Test direct des APIs sans dépendances externes
Utilise urllib (stdlib)
"""

import os
import json
import urllib.request
import urllib.error
import time

def test_claude():
    """Test Claude API"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY non configurée")
        return False

    print("\n🔍 Test Claude API...")

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    data = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 100,
        "messages": [
            {"role": "user", "content": "Dis 'Hello' en une seule ligne."}
        ]
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            if "content" in result and result["content"]:
                text = result["content"][0]["text"]
                print(f"✅ Claude API fonctionne!")
                print(f"   Réponse: {text}")
                return True
    except urllib.error.HTTPError as e:
        print(f"❌ Erreur HTTP {e.code}: {e.reason}")
        print(f"   Body: {e.read().decode('utf-8')[:200]}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

    return False

def test_openai():
    """Test OpenAI API"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY non configurée")
        return False

    print("\n🔍 Test OpenAI API...")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }

    data = {
        "model": "gpt-4o",
        "max_tokens": 100,
        "messages": [
            {"role": "user", "content": "Dis 'Hello' en une seule ligne."}
        ]
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            if "choices" in result and result["choices"]:
                text = result["choices"][0]["message"]["content"]
                print(f"✅ OpenAI API fonctionne!")
                print(f"   Réponse: {text}")
                return True
    except urllib.error.HTTPError as e:
        print(f"❌ Erreur HTTP {e.code}: {e.reason}")
        body = e.read().decode('utf-8')[:200]
        print(f"   Body: {body}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

    return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 TEST DES APIS (urllib, sans dépendances)")
    print("=" * 60)

    claude_ok = test_claude()
    time.sleep(1)
    openai_ok = test_openai()

    print("\n" + "=" * 60)
    if claude_ok or openai_ok:
        print("✅ Au moins une API fonctionne!")
    else:
        print("❌ Aucune API ne fonctionne")
    print("=" * 60)
