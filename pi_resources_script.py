#!/usr/bin/env python3
"""
Resource usage test for email polling on Raspberry Pi Zero W2
Measures CPU, memory, and network overhead of IMAP polling
"""
import psutil
import time
import threading
from app import Config, imap_fetch_unseen
import gc

def measure_resources():
    """Measure current system resource usage."""
    process = psutil.Process()
    return {
        'cpu_percent': process.cpu_percent(),
        'memory_mb': process.memory_info().rss / 1024 / 1024,
        'memory_percent': process.memory_percent(),
        'threads': process.num_threads()
    }

def test_polling_overhead():
    """Test resource overhead of IMAP polling operations."""
    print("🔍 RASPBERRY PI ZERO W2 - RESOURCE USAGE TEST")
    print("=" * 60)
    
    config = Config()
    
    # Baseline measurement
    print("📊 Baseline measurements...")
    gc.collect()  # Force garbage collection
    time.sleep(1)
    baseline = measure_resources()
    
    print(f"Baseline - CPU: {baseline['cpu_percent']:.1f}%, "
          f"Memory: {baseline['memory_mb']:.1f}MB ({baseline['memory_percent']:.1f}%), "
          f"Threads: {baseline['threads']}")
    
    # Test single polling operation
    print("\n🔄 Testing single IMAP poll...")
    start_time = time.time()
    start_resources = measure_resources()
    
    try:
        messages = imap_fetch_unseen(config)
        poll_duration = time.time() - start_time
        end_resources = measure_resources()
        
        print(f"✅ Poll completed in {poll_duration:.2f}s")
        print(f"📧 Found {len(messages)} messages")
        print(f"🧠 Memory after poll: {end_resources['memory_mb']:.1f}MB "
              f"(+{end_resources['memory_mb'] - start_resources['memory_mb']:.1f}MB)")
        print(f"⚡ CPU during poll: {end_resources['cpu_percent']:.1f}%")
        
    except Exception as e:
        print(f"❌ Poll failed: {e}")
        return
    
    # Simulate polling intervals
    intervals = [20, 30, 60, 120]  # seconds
    
    for interval in intervals:
        print(f"\n⏰ Simulating {interval}s polling interval...")
        
        # Calculate resource usage per hour
        polls_per_hour = 3600 / interval
        estimated_cpu_time = poll_duration * polls_per_hour
        
        print(f"   📈 Polls per hour: {polls_per_hour:.1f}")
        print(f"   🔥 CPU time per hour: {estimated_cpu_time:.1f}s ({estimated_cpu_time/36:.1f}%)")
        print(f"   🌐 Network connections per hour: {polls_per_hour:.1f}")
        
        # Pi Zero W2 specific assessment
        if interval == 20:
            print(f"   🚨 Pi Zero W2 Assessment: {'HEAVY' if estimated_cpu_time > 60 else 'MODERATE' if estimated_cpu_time > 30 else 'LIGHT'}")
        elif interval == 60:
            print(f"   ✅ Pi Zero W2 Assessment: {'HEAVY' if estimated_cpu_time > 30 else 'MODERATE' if estimated_cpu_time > 15 else 'LIGHT'}")

def test_memory_leak():
    """Test for memory leaks during repeated polling."""
    print(f"\n🔍 Memory leak test (10 polling cycles)...")
    config = Config()
    
    initial_memory = measure_resources()['memory_mb']
    
    for i in range(10):
        try:
            messages = imap_fetch_unseen(config)
            current_memory = measure_resources()['memory_mb']
            memory_growth = current_memory - initial_memory
            
            if i % 3 == 0:  # Report every 3rd cycle
                print(f"   Cycle {i+1}: {current_memory:.1f}MB (+{memory_growth:.1f}MB)")
            
            time.sleep(1)  # Brief pause between polls
            
        except Exception as e:
            print(f"   Cycle {i+1} failed: {e}")
            break
    
    final_memory = measure_resources()['memory_mb']
    total_growth = final_memory - initial_memory
    
    print(f"📊 Memory growth over 10 cycles: {total_growth:.1f}MB")
    print(f"🔍 Memory leak assessment: {'DETECTED' if total_growth > 5 else 'MINIMAL' if total_growth > 1 else 'NONE'}")

def get_raspberry_pi_recommendations():
    """Provide Pi Zero W2 specific recommendations."""
    print("\n🥧 RASPBERRY PI ZERO W2 RECOMMENDATIONS")
    print("=" * 50)
    
    # Pi Zero W2 specs
    print("Hardware specs:")
    print("   📱 RAM: 512MB")
    print("   🔧 CPU: 1GHz ARM Cortex-A53 (single core)")
    print("   🌐 WiFi: 802.11n")
    
    print("\nOptimal polling intervals:")
    print("   ⚡ Real-time needs: 30-60 seconds (acceptable overhead)")
    print("   🔋 Battery friendly: 2-5 minutes (minimal overhead)")
    print("   💤 Low-priority: 10+ minutes (negligible overhead)")
    
    print("\nMemory optimization tips:")
    print("   🗑️  Enable log rotation")
    print("   🚫 Disable debug logging in production")
    print("   🔄 Periodic garbage collection")
    print("   📊 Monitor with htop or similar")

if __name__ == "__main__":
    try:
        test_polling_overhead()
        test_memory_leak()
        get_raspberry_pi_recommendations()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        
    print(f"\n🏁 Resource test completed!")
