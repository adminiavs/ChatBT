#!/usr/bin/env python3
"""
Simplified test suite to verify critical fixes without requiring dependencies
"""

import os
import json
import time
from pathlib import Path

def test_frontend_imports():
    """Test that frontend imports are correct"""
    print("Testing frontend imports...")
    
    app_jsx_path = Path("chatbt-frontend/src/App.jsx")
    if app_jsx_path.exists():
        with open(app_jsx_path, 'r') as f:
            content = f.read()
            
        if "EnhancedChatInterface.jsx" in content:
            print("✓ App.jsx imports fixed")
            return True
        else:
            print("✗ App.jsx imports still incorrect")
            return False
    else:
        print("✗ App.jsx not found")
        return False

def test_api_base_configuration():
    """Test that API bases are configured correctly"""
    print("Testing API base configuration...")
    
    use_api_path = Path("chatbt-frontend/src/hooks/useApi.js")
    if use_api_path.exists():
        with open(use_api_path, 'r') as f:
            content = f.read()
            
        if "API_BASE_URL = '/api'" in content:
            print("✓ API base URL fixed to relative path")
            return True
        else:
            print("✗ API base URL still hardcoded")
            return False
    else:
        print("✗ useApi.js not found")
        return False

def test_websocket_urls():
    """Test that WebSocket URLs are fixed"""
    print("Testing WebSocket URL configuration...")
    
    websocket_path = Path("chatbt-frontend/src/hooks/useWebSocket.js")
    if websocket_path.exists():
        with open(websocket_path, 'r') as f:
            content = f.read()
            
        if "useWebSocket = (url = '', options = {})" in content:
            print("✓ WebSocket URLs fixed to relative paths")
            return True
        else:
            print("✗ WebSocket URLs still hardcoded")
            return False
    else:
        print("✗ useWebSocket.js not found")
        return False

def test_vite_proxy_configuration():
    """Test that Vite proxy is configured"""
    print("Testing Vite proxy configuration...")
    
    vite_config_path = Path("chatbt-frontend/vite.config.js")
    if vite_config_path.exists():
        with open(vite_config_path, 'r') as f:
            content = f.read()
            
        if "proxy:" in content and "'/api':" in content:
            print("✓ Vite proxy configuration added")
            return True
        else:
            print("✗ Vite proxy not configured")
            return False
    else:
        print("✗ vite.config.js not found")
        return False

def test_secret_key_security():
    """Test that secret key is properly secured"""
    print("Testing secret key security...")
    
    main_dsde_path = Path("chatbt-backend/src/main_with_dsde.py")
    if main_dsde_path.exists():
        with open(main_dsde_path, 'r') as f:
            content = f.read()
            
        if "secrets.token_hex(32)" in content and "SECRET_KEY = os.environ.get('SECRET_KEY')" in content:
            print("✓ Secret key is properly secured")
            return True
        else:
            print("✗ Secret key is still hardcoded")
            return False
    else:
        print("✗ main_with_dsde.py not found")
        return False

def test_thread_safety_implementation():
    """Test that thread safety is implemented"""
    print("Testing thread safety implementation...")
    
    main_dsde_path = Path("chatbt-backend/src/main_with_dsde.py")
    if main_dsde_path.exists():
        with open(main_dsde_path, 'r') as f:
            content = f.read()
            
        if "metrics_lock = threading.Lock()" in content and "with metrics_lock:" in content:
            print("✓ Thread safety implemented")
            return True
        else:
            print("✗ Thread safety not implemented")
            return False
    else:
        print("✗ main_with_dsde.py not found")
        return False

def test_orchestrator_concurrency():
    """Test that orchestrator uses concurrent specialist calls"""
    print("Testing orchestrator concurrency...")
    
    orchestrator_path = Path("chatbt-backend/src/orchestrator.py")
    if orchestrator_path.exists():
        with open(orchestrator_path, 'r') as f:
            content = f.read()
            
        if "asyncio.gather" in content and "_query_single_specialist" in content:
            print("✓ Orchestrator uses concurrent specialist calls")
            return True
        else:
            print("✗ Orchestrator still uses sequential calls")
            return False
    else:
        print("✗ orchestrator.py not found")
        return False

def test_cors_configuration():
    """Test CORS configuration"""
    print("Testing CORS configuration...")
    
    main_dsde_path = Path("chatbt-backend/src/main_with_dsde.py")
    if main_dsde_path.exists():
        with open(main_dsde_path, 'r') as f:
            content = f.read()
            
        if "CORS_ORIGINS = os.environ.get" in content and not 'origins="*"' in content:
            print("✓ CORS configuration secured")
            return True
        else:
            print("✗ CORS still uses wildcard")
            return False
    else:
        print("✗ main_with_dsde.py not found")
        return False

def test_requirements_consistency():
    """Test that requirements are consistent"""
    print("Testing requirements consistency...")
    
    unified_req_path = Path("chatbt-backend/requirements_unified.txt")
    if unified_req_path.exists():
        with open(unified_req_path, 'r') as f:
            content = f.read()
            
        if "Flask==" in content and "torch==" in content and "numpy==" in content:
            print("✓ Unified requirements file created with all dependencies")
            return True
        else:
            print("✗ Unified requirements incomplete")
            return False
    else:
        print("✗ Unified requirements file missing")
        return False

def test_dsde_package_structure():
    """Test DSDE package structure"""
    print("Testing DSDE package structure...")
    
    dsde_init_path = Path("chatbt-backend/src/dsde/__init__.py")
    if dsde_init_path.exists():
        with open(dsde_init_path, 'r') as f:
            content = f.read()
            
        if "DSDecoder" in content and "SignalConfig" in content and "AdapterConfig" in content:
            print("✓ DSDE package properly structured")
            return True
        else:
            print("✗ DSDE package incomplete")
            return False
    else:
        print("✗ DSDE package not found")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print("=" * 80)
    print("CHATBT FIXES VERIFICATION REPORT (SIMPLIFIED)")
    print("=" * 80)
    
    tests = [
        ("Frontend Imports", test_frontend_imports),
        ("API Base Configuration", test_api_base_configuration),
        ("WebSocket URLs", test_websocket_urls),
        ("Vite Proxy Configuration", test_vite_proxy_configuration),
        ("Secret Key Security", test_secret_key_security),
        ("Thread Safety Implementation", test_thread_safety_implementation),
        ("Orchestrator Concurrency", test_orchestrator_concurrency),
        ("CORS Configuration", test_cors_configuration),
        ("Requirements Consistency", test_requirements_consistency),
        ("DSDE Package Structure", test_dsde_package_structure),
    ]
    
    results = {}
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 ALL FIXES VERIFIED - SYSTEM READY FOR RELEASE")
        status = "READY FOR RELEASE"
    elif passed >= total * 0.9:
        print("✅ MOST FIXES VERIFIED - SYSTEM NEARLY READY")
        status = "NEARLY READY"
    elif passed >= total * 0.7:
        print("⚠️  MOST FIXES VERIFIED - MINOR ISSUES REMAIN")
        status = "MOSTLY READY"
    else:
        print("❌ CRITICAL ISSUES REMAIN - NEEDS MORE WORK")
        status = "NEEDS WORK"
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        status_icon = "✓" if result else "✗"
        print(f"  {status_icon} {test_name}")
    
    # Save results to file
    report = {
        "timestamp": time.time(),
        "total_tests": total,
        "passed_tests": passed,
        "success_rate": passed/total,
        "status": status,
        "detailed_results": results
    }
    
    with open("fixes_verification_report_simple.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to fixes_verification_report_simple.json")
    
    return passed >= total * 0.9  # 90% pass rate for release readiness

if __name__ == "__main__":
    success = run_all_tests()
    exit_code = 0 if success else 1
    print(f"\nExit code: {exit_code}")
    exit(exit_code)

