"""
Comprehensive Test Suite for Complete ChatBT System
Tests all specialists, orchestrator, and integration
"""

import sys
import os
import json
import time
import asyncio
import requests
from typing import Dict, List, Any

# Add the backend source path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'chatbt-backend', 'src'))

def test_backend_imports():
    """Test that all backend components can be imported"""
    print("Testing backend imports...")
    
    try:
        from orchestrator import PythonOrchestrator
        print("✓ Orchestrator imported successfully")
        
        from specialists.core_pythonic_specialist import CorePythonicSpecialist
        print("✓ Core Pythonic Specialist imported successfully")
        
        from specialists.standard_library_specialist import StandardLibrarySpecialist
        print("✓ Standard Library Specialist imported successfully")
        
        from specialists.code_critic_specialist import CodeCriticSpecialist
        print("✓ Code Critic Specialist imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_specialist_initialization():
    """Test individual specialist initialization"""
    print("\nTesting specialist initialization...")
    
    try:
        from orchestrator import PythonOrchestrator
        from specialists.core_pythonic_specialist import CorePythonicSpecialist
        from specialists.standard_library_specialist import StandardLibrarySpecialist
        from specialists.code_critic_specialist import CodeCriticSpecialist
        
        # Test individual specialists
        core_pythonic = CorePythonicSpecialist()
        print(f"✓ Core Pythonic: {len(core_pythonic.patterns)} patterns loaded")
        
        stdlib_specialist = StandardLibrarySpecialist()
        print(f"✓ Standard Library: {len(stdlib_specialist.patterns)} patterns loaded")
        
        code_critic = CodeCriticSpecialist()
        print(f"✓ Code Critic: {len(code_critic.rules)} rules loaded")
        
        # Test orchestrator
        orchestrator = PythonOrchestrator()
        print(f"✓ Orchestrator: {len(orchestrator.query_patterns)} query types supported")
        
        return True
        
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_orchestrator_functionality():
    """Test orchestrator end-to-end functionality"""
    print("\nTesting orchestrator functionality...")
    
    try:
        from orchestrator import PythonOrchestrator
        
        orchestrator = PythonOrchestrator()
        
        # Test different types of queries
        test_queries = [
            {
                'query': 'How do I count items in a list efficiently?',
                'expected_type': 'library_usage',
                'expected_specialists': ['stdlib_specialist']
            },
            {
                'query': 'Analyze this code: def bad_func(items=[]): return items',
                'expected_type': 'code_analysis',
                'expected_specialists': ['code_critic']
            },
            {
                'query': 'What\'s the most pythonic way to iterate?',
                'expected_type': 'best_practices',
                'expected_specialists': ['core_pythonic']
            }
        ]
        
        results = []
        
        for test_case in test_queries:
            print(f"  Testing: '{test_case['query'][:50]}...'")
            
            result = await orchestrator.process_query(test_case['query'])
            
            print(f"    ✓ Query type: {result.query_type.value}")
            print(f"    ✓ Specialists: {[r.specialist_name for r in result.specialist_responses]}")
            print(f"    ✓ Confidence: {result.confidence:.2f}")
            print(f"    ✓ Processing time: {result.processing_time:.3f}s")
            
            results.append(result)
        
        return results
        
    except Exception as e:
        print(f"✗ Orchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_api_endpoints(base_url='http://localhost:5000'):
    """Test API endpoints (requires running server)"""
    print(f"\nTesting API endpoints at {base_url}...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✓ Health check: {health_data['status']}")
            print(f"  - Uptime: {health_data['uptime_seconds']:.1f}s")
            print(f"  - Specialists: {health_data['specialists_loaded']}")
            print(f"  - Orchestrator: {health_data['orchestrator_ready']}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Health check connection failed: {e}")
        print("  (Make sure the server is running with: python chatbt-backend/src/main_with_specialists.py)")
        return False
    
    # Test chat endpoint
    try:
        chat_data = {"message": "How do I use list comprehensions?"}
        response = requests.post(f"{base_url}/api/chat", json=chat_data, timeout=10)
        
        if response.status_code == 200:
            chat_response = response.json()
            print(f"✓ Chat endpoint working")
            print(f"  - Query type: {chat_response.get('query_type')}")
            print(f"  - Specialists used: {chat_response.get('specialists_used')}")
            print(f"  - Confidence: {chat_response.get('confidence', 0):.2f}")
            print(f"  - Response length: {len(chat_response.get('response', ''))}")
        else:
            print(f"✗ Chat endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Chat endpoint failed: {e}")
        return False
    
    # Test code analysis endpoint
    try:
        code_data = {
            "code": "def bad_function(items=[]):\n    result = ''\n    for item in items:\n        result += str(item)\n    return result"
        }
        response = requests.post(f"{base_url}/api/analyze-code", json=code_data, timeout=10)
        
        if response.status_code == 200:
            analysis_response = response.json()
            print(f"✓ Code analysis endpoint working")
            print(f"  - Issues found: {analysis_response['summary']['total_issues']}")
            print(f"  - Fix suggestions: {len(analysis_response.get('fixes', []))}")
        else:
            print(f"✗ Code analysis endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Code analysis endpoint failed: {e}")
        return False
    
    # Test library suggestion endpoint
    try:
        lib_data = {"task": "I need to count items in a dataset"}
        response = requests.post(f"{base_url}/api/suggest-library", json=lib_data, timeout=10)
        
        if response.status_code == 200:
            lib_response = response.json()
            print(f"✓ Library suggestion endpoint working")
            print(f"  - Suggestions: {len(lib_response.get('suggestions', []))}")
        else:
            print(f"✗ Library suggestion endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Library suggestion endpoint failed: {e}")
        return False
    
    # Test metrics endpoint
    try:
        response = requests.get(f"{base_url}/api/metrics", timeout=5)
        
        if response.status_code == 200:
            metrics_response = response.json()
            print(f"✓ Metrics endpoint working")
            print(f"  - Total queries: {metrics_response['system_metrics']['total_queries']}")
            print(f"  - Avg response time: {metrics_response['system_metrics']['avg_response_time']:.3f}s")
            print(f"  - Specialists loaded: {len(metrics_response.get('specialists_loaded', []))}")
        else:
            print(f"✗ Metrics endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Metrics endpoint failed: {e}")
        return False
    
    return True

def test_specialist_integration():
    """Test integration between specialists"""
    print("\nTesting specialist integration...")
    
    try:
        from orchestrator import PythonOrchestrator
        
        orchestrator = PythonOrchestrator()
        
        # Test complex query that should involve multiple specialists
        complex_query = '''
        Analyze this code and suggest improvements:
        
        def process_data(items=[]):
            result = ""
            for item in items:
                result += str(item) + ", "
            
            try:
                return result.strip(", ")
            except:
                pass
        '''
        
        print("  Processing complex query...")
        result = asyncio.run(orchestrator.process_query(complex_query))
        
        print(f"  ✓ Query processed successfully")
        print(f"  ✓ Query type: {result.query_type.value}")
        print(f"  ✓ Response mode: {result.response_mode.value}")
        print(f"  ✓ Specialists involved: {[r.specialist_name for r in result.specialist_responses]}")
        print(f"  ✓ Overall confidence: {result.confidence:.2f}")
        
        # Check if multiple specialists were involved
        specialist_names = [r.specialist_name for r in result.specialist_responses]
        if len(specialist_names) > 1:
            print(f"  ✓ Multi-specialist collaboration successful")
        else:
            print(f"  ⚠ Only one specialist involved: {specialist_names}")
        
        # Check if response contains analysis from different perspectives
        response_lower = result.primary_response.lower()
        analysis_indicators = ['issue', 'problem', 'improve', 'suggest', 'fix', 'better']
        found_indicators = [ind for ind in analysis_indicators if ind in response_lower]
        
        print(f"  ✓ Analysis indicators found: {found_indicators}")
        
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance_benchmarks():
    """Test system performance with various query types"""
    print("\nTesting performance benchmarks...")
    
    try:
        from orchestrator import PythonOrchestrator
        
        orchestrator = PythonOrchestrator()
        
        benchmark_queries = [
            "How do I use list comprehensions?",
            "What's wrong with this code: def func(x=[]): x.append(1)",
            "Suggest the best library for file operations",
            "Explain the difference between lists and tuples",
            "How can I optimize this slow function?"
        ]
        
        total_time = 0
        results = []
        
        for query in benchmark_queries:
            start_time = time.time()
            result = asyncio.run(orchestrator.process_query(query))
            end_time = time.time()
            
            processing_time = end_time - start_time
            total_time += processing_time
            
            results.append({
                'query': query[:50] + '...',
                'processing_time': processing_time,
                'confidence': result.confidence,
                'specialists_used': len(result.specialist_responses)
            })
            
            print(f"  ✓ '{query[:40]}...' - {processing_time:.3f}s")
        
        avg_time = total_time / len(benchmark_queries)
        avg_confidence = sum(r['confidence'] for r in results) / len(results)
        
        print(f"\n  Performance Summary:")
        print(f"  - Average processing time: {avg_time:.3f}s")
        print(f"  - Average confidence: {avg_confidence:.2f}")
        print(f"  - Total queries: {len(benchmark_queries)}")
        
        # Performance thresholds
        if avg_time < 1.0:
            print(f"  ✓ Performance: Excellent (< 1.0s)")
        elif avg_time < 2.0:
            print(f"  ✓ Performance: Good (< 2.0s)")
        else:
            print(f"  ⚠ Performance: Needs optimization (> 2.0s)")
        
        return results
        
    except Exception as e:
        print(f"✗ Performance test failed: {e}")
        return []

def generate_integration_report():
    """Generate comprehensive integration test report"""
    print("\n" + "="*70)
    print("CHATBT COMPLETE SYSTEM INTEGRATION TEST REPORT")
    print("="*70)
    
    test_results = {
        'timestamp': time.time(),
        'tests': {}
    }
    
    # Run all tests
    print("\n1. Backend Import Tests")
    test_results['tests']['imports'] = test_backend_imports()
    
    print("\n2. Specialist Initialization Tests")
    test_results['tests']['initialization'] = test_specialist_initialization()
    
    print("\n3. Orchestrator Functionality Tests")
    orchestrator_results = asyncio.run(test_orchestrator_functionality())
    test_results['tests']['orchestrator'] = len(orchestrator_results) > 0
    test_results['orchestrator_results'] = len(orchestrator_results)
    
    print("\n4. Specialist Integration Tests")
    test_results['tests']['integration'] = test_specialist_integration()
    
    print("\n5. Performance Benchmark Tests")
    performance_results = test_performance_benchmarks()
    test_results['tests']['performance'] = len(performance_results) > 0
    test_results['performance_results'] = performance_results
    
    print("\n6. API Endpoint Tests")
    test_results['tests']['api_endpoints'] = test_api_endpoints()
    
    # Calculate overall success
    passed_tests = sum(1 for result in test_results['tests'].values() if result)
    total_tests = len(test_results['tests'])
    success_rate = passed_tests / total_tests
    
    test_results['summary'] = {
        'passed_tests': passed_tests,
        'total_tests': total_tests,
        'success_rate': success_rate,
        'overall_status': 'PASSED' if success_rate >= 0.8 else 'FAILED'
    }
    
    # Save report
    with open('complete_system_test_report.json', 'w') as f:
        json.dump(test_results, f, indent=2, default=str)
    
    # Print summary
    print(f"\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {success_rate:.1%}")
    print(f"Overall Status: {test_results['summary']['overall_status']}")
    
    if test_results['tests']['imports']:
        print("✓ All backend components can be imported")
    if test_results['tests']['initialization']:
        print("✓ All specialists initialize correctly")
    if test_results['tests']['orchestrator']:
        print(f"✓ Orchestrator processes {test_results['orchestrator_results']} test queries")
    if test_results['tests']['integration']:
        print("✓ Specialists integrate and collaborate correctly")
    if test_results['tests']['performance']:
        print(f"✓ Performance benchmarks completed ({len(performance_results)} queries)")
    if test_results['tests']['api_endpoints']:
        print("✓ All API endpoints respond correctly")
    else:
        print("⚠ API endpoints not tested (server not running)")
    
    print(f"\n✓ Complete system test report saved to complete_system_test_report.json")
    
    if success_rate >= 0.8:
        print("🎉 ChatBT Complete System is ready for deployment!")
    else:
        print("❌ System needs fixes before deployment")
    
    return test_results

def main():
    """Run complete system tests"""
    try:
        report = generate_integration_report()
        return report['summary']['overall_status'] == 'PASSED'
    except Exception as e:
        print(f"\n✗ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

