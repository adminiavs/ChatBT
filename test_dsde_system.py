"""
Comprehensive DSDE System Test Suite
Tests all DSDE components and integration with ChatBT
"""

import sys
import os
import json
import time
import asyncio
import numpy as np
from typing import Dict, List, Any
import torch

# Add the backend source path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'chatbt-backend', 'src'))

def test_dsde_imports():
    """Test that all DSDE components can be imported"""
    print("Testing DSDE imports...")
    
    try:
        from dsde import DSDecoder, DSDecodeConfig, SignalConfig, AdapterConfig
        print("✓ Core DSDE components imported successfully")
        
        from dsde.signals import KLDVarianceSignal, WVIRCalculator, CombinedSignalProcessor
        print("✓ DSDE signal components imported successfully")
        
        from dsde.adapter import SpeculationLengthAdapter, BatchOptimizer
        print("✓ DSDE adapter components imported successfully")
        
        from dsde.utils import DSDecodeResult, PerformanceMetrics
        print("✓ DSDE utility components imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ DSDE import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_signal_processing():
    """Test DSDE signal processing components"""
    print("\nTesting DSDE signal processing...")
    
    try:
        from dsde.signals import KLDVarianceSignal, WVIRCalculator, CombinedSignalProcessor, SignalConfig
        
        # Test KLD signal
        config = SignalConfig()
        kld_signal = KLDVarianceSignal(config)
        
        # Simulate some logits
        draft_logits = torch.randn(50000)
        target_logits = torch.randn(50000)
        
        kld_value = kld_signal.compute_kld(draft_logits, target_logits)
        print(f"✓ KLD computation: {kld_value:.4f}")
        
        # Test history update
        kld_signal.update_history("test_seq", [kld_value, kld_value * 0.8, kld_value * 1.2])
        stability = kld_signal.get_regional_stability("test_seq")
        print(f"✓ Regional stability: {stability:.4f}")
        
        # Test WVIR calculator
        wvir_calc = WVIRCalculator(config)
        kld_history = [0.5, 0.6, 0.4, 0.7, 0.3, 0.8, 0.2, 0.9]
        wvir_value = wvir_calc.calculate_wvir(kld_history)
        stability_class = wvir_calc.get_stability_classification(wvir_value)
        print(f"✓ WVIR calculation: {wvir_value:.4f} ({stability_class})")
        
        # Test combined signal processor
        signal_processor = CombinedSignalProcessor(config)
        
        # Simulate verification step
        draft_logits_list = [torch.randn(50000) for _ in range(3)]
        target_logits_list = [torch.randn(50000) for _ in range(3)]
        
        results = signal_processor.process_verification_step(
            "test_seq", draft_logits_list, target_logits_list, 2
        )
        
        print(f"✓ Combined signal processing: {len(results)} metrics computed")
        print(f"  - Stability: {results.get('stability', 0):.4f}")
        print(f"  - WVIR: {results.get('wvir', 0):.4f}")
        print(f"  - Acceptance likelihood: {results.get('next_acceptance_likelihood', 0):.4f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Signal processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_speculation_length_adapter():
    """Test speculation length adaptation"""
    print("\nTesting speculation length adapter...")
    
    try:
        from dsde.adapter import SpeculationLengthAdapter, AdapterConfig, BatchOptimizer
        from dsde.signals import SignalConfig
        
        # Initialize adapter
        adapter_config = AdapterConfig(
            min_speculation_length=1,
            max_speculation_length=6,
            default_speculation_length=3
        )
        signal_config = SignalConfig()
        
        adapter = SpeculationLengthAdapter(adapter_config, signal_config)
        
        # Test prediction for different scenarios
        test_scenarios = [
            {"sequence_id": "stable_seq", "context": {"task_type": "code_generation"}},
            {"sequence_id": "unstable_seq", "context": {"task_type": "creative_writing"}},
            {"sequence_id": "moderate_seq", "context": {"task_type": "dialogue"}}
        ]
        
        predictions = []
        for scenario in test_scenarios:
            predicted_sl = adapter.predict_optimal_sl(
                scenario["sequence_id"], 
                scenario["context"]
            )
            predictions.append(predicted_sl)
            print(f"✓ Predicted SL for {scenario['sequence_id']}: {predicted_sl}")
        
        # Test performance updates
        for i, scenario in enumerate(test_scenarios):
            adapter.update_performance(
                scenario["sequence_id"],
                speculation_length=predictions[i],
                accepted_tokens=np.random.randint(1, predictions[i] + 1),
                total_tokens=predictions[i],
                processing_time=0.1
            )
        
        # Test batch optimization
        batch_optimizer = BatchOptimizer(adapter_config)
        optimized_sls, sl_cap = batch_optimizer.optimize_batch_speculation_lengths(predictions)
        
        print(f"✓ Batch optimization: {predictions} -> {optimized_sls} (cap: {sl_cap})")
        
        # Test statistics
        for scenario in test_scenarios:
            stats = adapter.get_sequence_stats(scenario["sequence_id"])
            print(f"✓ Stats for {scenario['sequence_id']}: "
                  f"acceptance_rate={stats['performance']['overall_acceptance_rate']:.3f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Speculation length adapter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dsde_core():
    """Test core DSDE decoder functionality"""
    print("\nTesting DSDE core decoder...")
    
    try:
        from dsde import DSDecoder, DSDecodeConfig, SignalConfig, AdapterConfig
        
        # Configure DSDE
        signal_config = SignalConfig(
            short_window_size=3,
            long_window_size=8,
            kld_threshold=0.1
        )
        
        adapter_config = AdapterConfig(
            min_speculation_length=1,
            max_speculation_length=4,
            default_speculation_length=2
        )
        
        dsde_config = DSDecodeConfig(
            enable_dynamic_sl=True,
            enable_batch_optimization=True,
            enable_performance_monitoring=True,
            signal_config=signal_config,
            adapter_config=adapter_config,
            debug_mode=True
        )
        
        # Initialize decoder
        decoder = DSDecoder(config=dsde_config)
        print("✓ DSDE decoder initialized")
        
        # Test batch decoding
        test_sequences = [
            {
                'id': 'seq_1',
                'prompt': 'Write a Python function to calculate fibonacci numbers',
                'max_tokens': 50
            },
            {
                'id': 'seq_2', 
                'prompt': 'Explain the concept of machine learning',
                'max_tokens': 30
            },
            {
                'id': 'seq_3',
                'prompt': 'Create a simple web scraper',
                'max_tokens': 40
            }
        ]
        
        context_info = {
            'seq_1': {'task_type': 'code_generation', 'temperature': 0.3},
            'seq_2': {'task_type': 'explanation', 'temperature': 0.7},
            'seq_3': {'task_type': 'code_generation', 'temperature': 0.5}
        }
        
        # Run async decoding
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            results = loop.run_until_complete(
                decoder.decode_batch(test_sequences, context_info)
            )
            
            print(f"✓ Batch decoding completed: {len(results)} sequences processed")
            
            for result in results:
                print(f"  - {result.sequence_id}: "
                      f"{result.tokens_generated} tokens, "
                      f"{result.speculation_rounds} rounds, "
                      f"{result.acceptance_rate:.3f} acceptance rate, "
                      f"{result.speedup_estimate:.2f}x speedup")
            
        finally:
            loop.close()
        
        # Test performance summary
        performance_summary = decoder.get_performance_summary()
        print(f"✓ Performance summary: {performance_summary['sequences_per_second']:.2f} seq/s")
        
        return True
        
    except Exception as e:
        print(f"✗ DSDE core test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chatbt_dsde_integration():
    """Test integration between ChatBT and DSDE"""
    print("\nTesting ChatBT-DSDE integration...")
    
    try:
        # Test imports
        from orchestrator import PythonOrchestrator
        from specialists.core_pythonic_specialist import CorePythonicSpecialist
        from dsde import DSDecoder, DSDecodeConfig
        
        # Initialize components
        orchestrator = PythonOrchestrator()
        specialist = CorePythonicSpecialist()
        decoder = DSDecoder(config=DSDecodeConfig(debug_mode=True))
        
        print("✓ All components initialized successfully")
        
        # Test query processing
        test_query = "How can I optimize this Python code for better performance?"
        
        # Process with orchestrator
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            orchestration_result = loop.run_until_complete(
                orchestrator.process_query(test_query)
            )
            
            print(f"✓ Orchestrator processing: {orchestration_result.query_type.value}")
            print(f"  - Confidence: {orchestration_result.confidence:.3f}")
            print(f"  - Specialists: {[r.specialist_name for r in orchestration_result.specialist_responses]}")
            
            # Process with DSDE
            sequence_data = {
                'id': 'integration_test',
                'prompt': test_query,
                'max_tokens': 100
            }
            
            context_info = {
                'integration_test': {
                    'task_type': orchestration_result.query_type.value,
                    'temperature': 0.7
                }
            }
            
            dsde_results = loop.run_until_complete(
                decoder.decode_batch([sequence_data], context_info)
            )
            
            if dsde_results:
                dsde_result = dsde_results[0]
                print(f"✓ DSDE processing: {dsde_result.tokens_generated} tokens generated")
                print(f"  - Acceptance rate: {dsde_result.acceptance_rate:.3f}")
                print(f"  - Speedup estimate: {dsde_result.speedup_estimate:.2f}x")
            
        finally:
            loop.close()
        
        return True
        
    except Exception as e:
        print(f"✗ ChatBT-DSDE integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance_benchmarks():
    """Test DSDE performance benchmarks"""
    print("\nTesting DSDE performance benchmarks...")
    
    try:
        from dsde import DSDecoder, DSDecodeConfig
        from dsde.utils import PerformanceMetrics
        
        # Initialize with performance monitoring
        config = DSDecodeConfig(
            enable_performance_monitoring=True,
            debug_mode=False
        )
        decoder = DSDecoder(config=config)
        
        # Performance test scenarios
        test_scenarios = [
            {'batch_size': 1, 'sequence_length': 50},
            {'batch_size': 4, 'sequence_length': 100},
            {'batch_size': 8, 'sequence_length': 75}
        ]
        
        benchmark_results = []
        
        for scenario in test_scenarios:
            batch_size = scenario['batch_size']
            seq_length = scenario['sequence_length']
            
            # Create test batch
            sequences = [
                {
                    'id': f'perf_seq_{i}',
                    'prompt': f'Test sequence {i} with moderate complexity for performance testing',
                    'max_tokens': seq_length
                }
                for i in range(batch_size)
            ]
            
            # Measure performance
            start_time = time.time()
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                results = loop.run_until_complete(
                    decoder.decode_batch(sequences)
                )
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Calculate metrics
                total_tokens = sum(r.tokens_generated for r in results)
                avg_acceptance_rate = np.mean([r.acceptance_rate for r in results])
                avg_speedup = np.mean([r.speedup_estimate for r in results])
                
                benchmark_result = {
                    'batch_size': batch_size,
                    'sequence_length': seq_length,
                    'processing_time': processing_time,
                    'total_tokens': total_tokens,
                    'tokens_per_second': total_tokens / processing_time,
                    'avg_acceptance_rate': avg_acceptance_rate,
                    'avg_speedup': avg_speedup
                }
                
                benchmark_results.append(benchmark_result)
                
                print(f"✓ Batch {batch_size}, SeqLen {seq_length}: "
                      f"{total_tokens} tokens in {processing_time:.3f}s "
                      f"({benchmark_result['tokens_per_second']:.1f} tok/s, "
                      f"{avg_acceptance_rate:.3f} acc rate, "
                      f"{avg_speedup:.2f}x speedup)")
                
            finally:
                loop.close()
        
        # Performance analysis
        avg_tokens_per_sec = np.mean([r['tokens_per_second'] for r in benchmark_results])
        avg_acceptance_rate = np.mean([r['avg_acceptance_rate'] for r in benchmark_results])
        avg_speedup = np.mean([r['avg_speedup'] for r in benchmark_results])
        
        print(f"\n✓ Performance Summary:")
        print(f"  - Average throughput: {avg_tokens_per_sec:.1f} tokens/second")
        print(f"  - Average acceptance rate: {avg_acceptance_rate:.3f}")
        print(f"  - Average speedup: {avg_speedup:.2f}x")
        
        # Performance thresholds for release readiness
        performance_ready = (
            avg_tokens_per_sec > 50 and  # Minimum throughput
            avg_acceptance_rate > 0.3 and  # Minimum acceptance rate
            avg_speedup > 1.2  # Minimum speedup
        )
        
        if performance_ready:
            print("✓ Performance benchmarks PASSED - System ready for release")
        else:
            print("⚠ Performance benchmarks below thresholds - Optimization needed")
        
        return performance_ready
        
    except Exception as e:
        print(f"✗ Performance benchmark test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_system_stability():
    """Test system stability under various conditions"""
    print("\nTesting system stability...")
    
    try:
        from dsde import DSDecoder, DSDecodeConfig
        
        decoder = DSDecoder(config=DSDecodeConfig(debug_mode=False))
        
        # Stability test scenarios
        stability_tests = [
            {
                'name': 'Empty sequences',
                'sequences': []
            },
            {
                'name': 'Single character prompts',
                'sequences': [{'id': 'short_1', 'prompt': 'a', 'max_tokens': 5}]
            },
            {
                'name': 'Very long prompts',
                'sequences': [{'id': 'long_1', 'prompt': 'a' * 1000, 'max_tokens': 10}]
            },
            {
                'name': 'Mixed batch sizes',
                'sequences': [
                    {'id': 'mixed_1', 'prompt': 'short', 'max_tokens': 5},
                    {'id': 'mixed_2', 'prompt': 'medium length prompt', 'max_tokens': 20},
                    {'id': 'mixed_3', 'prompt': 'very long prompt ' * 50, 'max_tokens': 15}
                ]
            }
        ]
        
        stability_results = []
        
        for test in stability_tests:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    start_time = time.time()
                    results = loop.run_until_complete(
                        decoder.decode_batch(test['sequences'])
                    )
                    end_time = time.time()
                    
                    stability_results.append({
                        'test_name': test['name'],
                        'success': True,
                        'processing_time': end_time - start_time,
                        'results_count': len(results)
                    })
                    
                    print(f"✓ {test['name']}: {len(results)} results in {end_time - start_time:.3f}s")
                    
                finally:
                    loop.close()
                    
            except Exception as e:
                stability_results.append({
                    'test_name': test['name'],
                    'success': False,
                    'error': str(e)
                })
                print(f"✗ {test['name']}: {e}")
        
        # Analyze stability
        success_rate = sum(1 for r in stability_results if r['success']) / len(stability_results)
        
        print(f"\n✓ Stability test summary: {success_rate:.1%} success rate")
        
        stability_ready = success_rate >= 0.8  # 80% success rate threshold
        
        if stability_ready:
            print("✓ Stability tests PASSED - System stable under various conditions")
        else:
            print("⚠ Stability tests indicate issues - Further testing needed")
        
        return stability_ready
        
    except Exception as e:
        print(f"✗ Stability test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_release_readiness_report():
    """Generate comprehensive release readiness report"""
    print("\n" + "="*80)
    print("DSDE SYSTEM RELEASE READINESS REPORT")
    print("="*80)
    
    test_results = {
        'timestamp': time.time(),
        'tests': {}
    }
    
    # Run all tests
    print("\n1. DSDE Import Tests")
    test_results['tests']['imports'] = test_dsde_imports()
    
    print("\n2. Signal Processing Tests")
    test_results['tests']['signal_processing'] = test_signal_processing()
    
    print("\n3. Speculation Length Adapter Tests")
    test_results['tests']['adapter'] = test_speculation_length_adapter()
    
    print("\n4. DSDE Core Functionality Tests")
    test_results['tests']['core_functionality'] = test_dsde_core()
    
    print("\n5. ChatBT-DSDE Integration Tests")
    test_results['tests']['integration'] = test_chatbt_dsde_integration()
    
    print("\n6. Performance Benchmark Tests")
    test_results['tests']['performance'] = test_performance_benchmarks()
    
    print("\n7. System Stability Tests")
    test_results['tests']['stability'] = test_system_stability()
    
    # Calculate overall readiness
    passed_tests = sum(1 for result in test_results['tests'].values() if result)
    total_tests = len(test_results['tests'])
    success_rate = passed_tests / total_tests
    
    # Determine release readiness
    release_ready = success_rate >= 0.9  # 90% threshold for release
    
    test_results['summary'] = {
        'passed_tests': passed_tests,
        'total_tests': total_tests,
        'success_rate': success_rate,
        'release_ready': release_ready,
        'overall_status': 'READY FOR RELEASE' if release_ready else 'NEEDS IMPROVEMENT'
    }
    
    # Save detailed report
    with open('dsde_release_readiness_report.json', 'w') as f:
        json.dump(test_results, f, indent=2, default=str)
    
    # Print summary
    print(f"\n" + "="*80)
    print("RELEASE READINESS SUMMARY")
    print("="*80)
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {success_rate:.1%}")
    print(f"Release Status: {test_results['summary']['overall_status']}")
    
    # Detailed results
    print(f"\nDetailed Results:")
    for test_name, result in test_results['tests'].items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"  {test_name}: {status}")
    
    # Release recommendation
    print(f"\n" + "="*80)
    if release_ready:
        print("🎉 DSDE SYSTEM IS READY FOR RELEASE!")
        print("✓ All critical components tested and functional")
        print("✓ Performance benchmarks meet requirements")
        print("✓ System stability verified under various conditions")
        print("✓ Integration with ChatBT specialists confirmed")
    else:
        print("⚠️  DSDE SYSTEM NEEDS IMPROVEMENT BEFORE RELEASE")
        failed_tests = [name for name, result in test_results['tests'].items() if not result]
        print(f"✗ Failed tests: {', '.join(failed_tests)}")
        print("✗ Address failed tests before proceeding with release")
    
    print(f"\n✓ Detailed report saved to dsde_release_readiness_report.json")
    
    return test_results

def main():
    """Run complete DSDE system test suite"""
    try:
        report = generate_release_readiness_report()
        return report['summary']['release_ready']
    except Exception as e:
        print(f"\n✗ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

