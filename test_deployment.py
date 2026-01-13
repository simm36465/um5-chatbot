#!/usr/bin/env python3
"""
Script de test pour vérifier le déploiement local
À exécuter AVANT de déployer sur le cloud
"""

import requests
import time
import json
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "http://localhost:8000"

def print_header(text):
    print("\n" + "="*70)
    print(Fore.CYAN + Style.BRIGHT + text)
    print("="*70)

def print_success(text):
    print(Fore.GREEN + "✅ " + text)

def print_error(text):
    print(Fore.RED + "❌ " + text)

def print_info(text):
    print(Fore.YELLOW + "ℹ️  " + text)

def test_health():
    """Test 1: Health check"""
    print_header("TEST 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Server status: {data['status']}")
            print_success(f"Model loaded: {data['model_loaded']}")
            print_success(f"Device: {data['device']}")
            return True
        else:
            print_error(f"Status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server!")
        print_info("Make sure the server is running: python app.py")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_stats():
    """Test 2: Stats endpoint"""
    print_header("TEST 2: Model Statistics")
    try:
        response = requests.get(f"{BASE_URL}/api/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success("Model Info:")
            for key, value in data['model_info'].items():
                print(f"   {key}: {value}")
            print_success("Thresholds:")
            for key, value in data['thresholds'].items():
                print(f"   {key}: {value}")
            return True
        else:
            print_error(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_chat(message):
    """Test chat functionality"""
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"message": message},
            timeout=30
        )
        latency = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Response received in {latency:.0f}ms")
            print(f"\n   Q: {Fore.BLUE}{message}")
            print(f"   A: {Fore.GREEN}{data['answer'][:200]}...")
            print(f"\n   Method: {data['method']}")
            print(f"   Confidence: {data['confidence']:.2%}")
            print(f"   Intent: {data.get('intent', 'N/A')}")
            print(f"   Latency: {data['latency_ms']:.0f}ms")
            
            if data.get('sources'):
                print(f"   Sources: {len(data['sources'])} documents")
            
            return True
        else:
            print_error(f"Status code: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def main():
    """Main test suite"""
    
    print(Fore.CYAN + Style.BRIGHT + """
    ╔═══════════════════════════════════════════════════════════╗
    ║         UM5 CHATBOT - SUITE DE TESTS                      ║
    ║         Local Deployment Verification                     ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    results = []
    
    # Test 1: Health
    results.append(("Health Check", test_health()))
    time.sleep(1)
    
    # Test 2: Stats
    results.append(("Statistics", test_stats()))
    time.sleep(1)
    
    # Test 3: High confidence query
    print_header("TEST 3: High Confidence Query (Intent Direct)")
    results.append(("High Confidence", test_chat("Comment m'inscrire à l'UM5?")))
    time.sleep(1)
    
    # Test 4: Medium confidence (RAG)
    print_header("TEST 4: Medium Confidence Query (RAG)")
    results.append(("RAG Pipeline", test_chat("Quels sont les axes de recherche en IA?")))
    time.sleep(1)
    
    # Test 5: Low confidence (Fallback)
    print_header("TEST 5: Low Confidence Query (Fallback)")
    results.append(("Fallback", test_chat("Quelle est la politique sur l'IA éthique?")))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name:<25} PASSED")
        else:
            print_error(f"{test_name:<25} FAILED")
    
    print(f"\n{Fore.CYAN}Results: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("\n🎉 All tests passed! Ready for cloud deployment!")
        print_info("Next step: Follow DEPLOYMENT_GUIDE.md to deploy to cloud")
    else:
        print_error("\n⚠️  Some tests failed. Fix issues before deploying.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
