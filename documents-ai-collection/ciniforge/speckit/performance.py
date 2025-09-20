"""Performance testing utilities for SpecKit"""

import time
import psutil
import functools
import threading
from typing import Callable, Dict, Any, List, Optional
from dataclasses import dataclass
from contextlib import contextmanager

@dataclass
class PerformanceMetrics:
    """Container for performance metrics"""
    execution_time: float
    memory_usage: float
    cpu_usage: float
    peak_memory: float
    function_name: str
    timestamp: float
    
class PerformanceMonitor:
    """Monitor performance metrics during test execution"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.monitoring = False
        self.monitor_thread = None
        self.process = psutil.Process()
    
    def start_monitoring(self, interval: float = 0.1):
        """Start continuous performance monitoring"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
    
    def _monitor_loop(self, interval: float):
        """Continuous monitoring loop"""
        while self.monitoring:
            try:
                memory_info = self.process.memory_info()
                cpu_percent = self.process.cpu_percent()
                
                metric = PerformanceMetrics(
                    execution_time=0,  # Not applicable for continuous monitoring
                    memory_usage=memory_info.rss / 1024 / 1024,  # MB
                    cpu_usage=cpu_percent,
                    peak_memory=memory_info.peak_wss / 1024 / 1024 if hasattr(memory_info, 'peak_wss') else 0,
                    function_name="continuous_monitoring",
                    timestamp=time.time()
                )
                
                self.metrics.append(metric)
                time.sleep(interval)
                
            except Exception:
                # Continue monitoring even if there's an error
                time.sleep(interval)
    
    def get_average_metrics(self) -> Dict[str, float]:
        """Get average performance metrics"""
        if not self.metrics:
            return {}
            
        total_metrics = len(self.metrics)
        avg_memory = sum(m.memory_usage for m in self.metrics) / total_metrics
        avg_cpu = sum(m.cpu_usage for m in self.metrics) / total_metrics
        peak_memory = max(m.peak_memory for m in self.metrics)
        
        return {
            'average_memory_mb': round(avg_memory, 2),
            'average_cpu_percent': round(avg_cpu, 2),
            'peak_memory_mb': round(peak_memory, 2),
            'sample_count': total_metrics
        }
    
    def clear_metrics(self):
        """Clear collected metrics"""
        self.metrics.clear()

def benchmark(func: Callable = None, *, iterations: int = 1, warmup: int = 0):
    """Decorator to benchmark function performance
    
    Args:
        func: Function to benchmark
        iterations: Number of times to run the function
        warmup: Number of warmup runs (not counted in results)
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            process = psutil.Process()
            
            # Warmup runs
            for _ in range(warmup):
                f(*args, **kwargs)
            
            # Benchmark runs
            execution_times = []
            memory_before = process.memory_info().rss
            
            for _ in range(iterations):
                start_time = time.perf_counter()
                result = f(*args, **kwargs)
                end_time = time.perf_counter()
                execution_times.append(end_time - start_time)
            
            memory_after = process.memory_info().rss
            memory_used = (memory_after - memory_before) / 1024 / 1024  # MB
            
            # Calculate statistics
            avg_time = sum(execution_times) / len(execution_times)
            min_time = min(execution_times)
            max_time = max(execution_times)
            
            benchmark_result = {
                'function': f.__name__,
                'iterations': iterations,
                'average_time': round(avg_time, 6),
                'min_time': round(min_time, 6),
                'max_time': round(max_time, 6),
                'memory_used_mb': round(memory_used, 2),
                'times': execution_times
            }
            
            # Store result as function attribute
            wrapper.benchmark_result = benchmark_result
            
            return result
            
        return wrapper
    
    if func is None:
        return decorator
    else:
        return decorator(func)

@contextmanager
def performance_context(name: str = "operation"):
    """Context manager for measuring performance of code blocks"""
    process = psutil.Process()
    
    # Initial measurements
    start_time = time.perf_counter()
    start_memory = process.memory_info().rss
    start_cpu_time = process.cpu_times()
    
    try:
        yield
    finally:
        # Final measurements
        end_time = time.perf_counter()
        end_memory = process.memory_info().rss
        end_cpu_time = process.cpu_times()
        
        # Calculate metrics
        execution_time = end_time - start_time
        memory_delta = (end_memory - start_memory) / 1024 / 1024  # MB
        cpu_time_delta = (end_cpu_time.user - start_cpu_time.user) + (end_cpu_time.system - start_cpu_time.system)
        
        print(f"\n=== Performance Report: {name} ===")
        print(f"Execution Time: {execution_time:.6f} seconds")
        print(f"Memory Delta: {memory_delta:+.2f} MB")
        print(f"CPU Time: {cpu_time_delta:.6f} seconds")
        print(f"Memory Efficiency: {memory_delta/execution_time:.2f} MB/sec" if execution_time > 0 else "N/A")
        print("=" * (25 + len(name)))

class LoadTester:
    """Simple load testing utility"""
    
    def __init__(self, target_function: Callable):
        self.target_function = target_function
        self.results = []
    
    def run_load_test(self, 
                     concurrent_users: int = 10, 
                     requests_per_user: int = 10,
                     ramp_up_time: float = 1.0) -> Dict[str, Any]:
        """Run a load test with multiple concurrent users
        
        Args:
            concurrent_users: Number of concurrent threads
            requests_per_user: Number of requests each user makes
            ramp_up_time: Time to ramp up all users (seconds)
        """
        self.results.clear()
        threads = []
        start_time = time.time()
        
        def user_simulation(user_id: int):
            """Simulate a single user's requests"""
            user_results = []
            
            for request_id in range(requests_per_user):
                request_start = time.perf_counter()
                try:
                    result = self.target_function()
                    success = True
                    error = None
                except Exception as e:
                    result = None
                    success = False
                    error = str(e)
                
                request_end = time.perf_counter()
                
                user_results.append({
                    'user_id': user_id,
                    'request_id': request_id,
                    'response_time': request_end - request_start,
                    'success': success,
                    'error': error,
                    'timestamp': request_start
                })
            
            self.results.extend(user_results)
        
        # Start threads with ramp-up
        for i in range(concurrent_users):
            thread = threading.Thread(target=user_simulation, args=(i,))
            threads.append(thread)
            thread.start()
            
            # Ramp-up delay
            if i < concurrent_users - 1:
                time.sleep(ramp_up_time / concurrent_users)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # Calculate statistics
        successful_requests = [r for r in self.results if r['success']]
        failed_requests = [r for r in self.results if not r['success']]
        
        if successful_requests:
            response_times = [r['response_time'] for r in successful_requests]
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = min_response_time = max_response_time = 0
        
        total_time = end_time - start_time
        throughput = len(successful_requests) / total_time if total_time > 0 else 0
        
        return {
            'total_requests': len(self.results),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': len(successful_requests) / len(self.results) * 100 if self.results else 0,
            'average_response_time': round(avg_response_time, 6),
            'min_response_time': round(min_response_time, 6),
            'max_response_time': round(max_response_time, 6),
            'throughput_rps': round(throughput, 2),
            'total_test_time': round(total_time, 2),
            'concurrent_users': concurrent_users,
            'requests_per_user': requests_per_user
        }

def memory_profiler(func: Callable) -> Callable:
    """Decorator to profile memory usage of a function"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        process = psutil.Process()
        
        # Before execution
        memory_before = process.memory_info()
        
        result = func(*args, **kwargs)
        
        # After execution
        memory_after = process.memory_info()
        
        memory_delta = {
            'rss_delta_mb': (memory_after.rss - memory_before.rss) / 1024 / 1024,
            'vms_delta_mb': (memory_after.vms - memory_before.vms) / 1024 / 1024,
            'function': func.__name__
        }
        
        # Store as function attribute
        wrapper.memory_profile = memory_delta
        
        return result
    
    return wrapper