#!/usr/bin/env python3
"""
Chat Speed Test

This script tests the optimized chat API to measure response times
and verify the speed improvements.
"""

import requests
import time
import json
from statistics import mean, median

def test_chat_speed():
    """Test chat API speed with various questions"""
    base_url = "http://127.0.0.1:8000"
    
    print("⚡ BH Assurance Chat Speed Test")
    print("=" * 50)
    
    # Test questions of varying complexity
    test_questions = [
        "Bonjour",
        "Quelle est l'activité de la société Societe_000001?",
        "Quels sont les profils cibles pour le produit TEMPORAIRE DECES?",
        "Que couvre la garantie DECES?",
        "Comment choisir une assurance pour une entreprise?",
        "Quels sont les différents types d'assurance vie?",
        "Pouvez-vous expliquer la garantie INVALIDITE PERMANENTE TOTALE?",
        "Où se trouve la société Societe_000002?",
        "Merci pour votre aide",
        "Au revoir"
    ]
    
    response_times = []
    successful_requests = 0
    
    print(f"🧪 Testing {len(test_questions)} questions...")
    print("-" * 50)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}: {question}")
        
        try:
            # Measure request time
            start_time = time.time()
            
            response = requests.post(
                f"{base_url}/api/chat/",
                json={"message": question},
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            total_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                chat_response = data.get('response', 'No response')
                api_response_time = data.get('response_time', 'N/A')
                
                print(f"✅ Status: {response.status_code}")
                print(f"⏱️ Total Time: {total_time:.2f}s")
                print(f"🤖 API Time: {api_response_time}s")
                print(f"💬 Response: {chat_response[:80]}...")
                
                response_times.append(total_time)
                successful_requests += 1
                
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        
        # Small delay between requests
        time.sleep(1)
    
    # Calculate statistics
    print("\n" + "=" * 50)
    print("📊 SPEED TEST RESULTS")
    print("=" * 50)
    
    if response_times:
        avg_time = mean(response_times)
        median_time = median(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        print(f"📈 Total Requests: {len(test_questions)}")
        print(f"✅ Successful: {successful_requests}")
        print(f"❌ Failed: {len(test_questions) - successful_requests}")
        print(f"📊 Success Rate: {successful_requests/len(test_questions)*100:.1f}%")
        
        print(f"\n⏱️ Response Time Statistics:")
        print(f"   Average: {avg_time:.2f}s")
        print(f"   Median: {median_time:.2f}s")
        print(f"   Fastest: {min_time:.2f}s")
        print(f"   Slowest: {max_time:.2f}s")
        
        # Performance assessment
        print(f"\n🎯 Performance Assessment:")
        if avg_time < 3:
            print("🟢 EXCELLENT: Very fast response times!")
        elif avg_time < 5:
            print("🟡 GOOD: Acceptable response times")
        elif avg_time < 10:
            print("🟠 FAIR: Moderate response times")
        else:
            print("🔴 SLOW: Response times need improvement")
        
        # Speed recommendations
        print(f"\n💡 Speed Optimization Status:")
        if avg_time < 2:
            print("✅ Optimal performance achieved")
        elif avg_time < 5:
            print("✅ Good performance - minor optimizations possible")
        else:
            print("⚠️ Consider additional optimizations:")
            print("   • Reduce max_tokens further")
            print("   • Enable model caching")
            print("   • Use GPU acceleration")
            print("   • Implement response streaming")
    
    else:
        print("❌ No successful requests to analyze")
    
    return response_times

def test_cache_performance():
    """Test response caching performance"""
    base_url = "http://127.0.0.1:8000"
    
    print("\n" + "=" * 50)
    print("🗄️ CACHE PERFORMANCE TEST")
    print("=" * 50)
    
    # Test same question multiple times
    test_question = "Quelle est l'activité de la société Societe_000001?"
    
    print(f"Testing question: {test_question}")
    print("Testing cache performance with repeated requests...")
    
    times = []
    
    for i in range(3):
        print(f"\n🔄 Request {i+1}:")
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{base_url}/api/chat/",
                json={"message": test_question},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            total_time = time.time() - start_time
            times.append(total_time)
            
            if response.status_code == 200:
                data = response.json()
                api_time = data.get('response_time', 'N/A')
                print(f"   ⏱️ Time: {total_time:.2f}s (API: {api_time}s)")
                
                if i == 0:
                    print("   📝 First request (no cache)")
                else:
                    print("   🗄️ Subsequent request (potential cache hit)")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
        
        time.sleep(0.5)
    
    # Analyze cache performance
    if len(times) >= 2:
        first_time = times[0]
        subsequent_times = times[1:]
        avg_subsequent = mean(subsequent_times)
        
        print(f"\n📊 Cache Analysis:")
        print(f"   First request: {first_time:.2f}s")
        print(f"   Avg subsequent: {avg_subsequent:.2f}s")
        
        if avg_subsequent < first_time * 0.8:
            print("   ✅ Cache appears to be working!")
            speedup = (first_time - avg_subsequent) / first_time * 100
            print(f"   ⚡ Speedup: {speedup:.1f}%")
        else:
            print("   ⚠️ Cache may not be working optimally")

def main():
    """Main test function"""
    print("🚀 Starting Chat Speed Tests...")
    
    # Test overall speed
    response_times = test_chat_speed()
    
    # Test cache performance
    test_cache_performance()
    
    print(f"\n🎉 Speed testing completed!")
    
    if response_times:
        avg_time = mean(response_times)
        print(f"\n🎯 Summary: Average response time is {avg_time:.2f} seconds")
        
        if avg_time < 3:
            print("✅ Your chat API is performing excellently!")
        elif avg_time < 5:
            print("✅ Your chat API has good performance!")
        else:
            print("⚠️ Consider implementing additional optimizations")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
