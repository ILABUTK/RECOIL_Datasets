#!/usr/bin/env python3
"""
Quick performance test for voila.ipynb interactive examples.
Measures how long each data loading operation takes.

Run this inside the Docker container:
    docker exec -it recoil-data-voila python /app/test_performance.py

Or copy into running container and execute:
    docker cp test_performance.py recoil-data-voila:/app/
    docker exec -it recoil-data-voila python /app/test_performance.py
"""

import time
import pickle
import requests
import pandas as pd
import signal
from contextlib import contextmanager

BASE_URL = 'https://recoil.ise.utk.edu/data/Parsed_Data/'
TIMEOUT_SECONDS = 15

class TimeoutException(Exception):
    pass

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException(f"Operation timed out after {seconds} seconds")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

def load_pickle_from_url(url: str):
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return pickle.loads(resp.content)

def time_operation(name, func, timeout=TIMEOUT_SECONDS):
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    start = time.time()
    try:
        with time_limit(timeout):
            result = func()
            elapsed = time.time() - start
            print(f"✓ Success in {elapsed:.2f} seconds")
            if elapsed > 10:
                print(f"⚠️  WARNING: Takes longer than 10 seconds!")
            return elapsed, result, 'success'
    except TimeoutException as e:
        elapsed = time.time() - start
        print(f"⏱️  TIMEOUT after {elapsed:.2f} seconds: {e}")
        return elapsed, None, 'timeout'
    except Exception as e:
        elapsed = time.time() - start
        print(f"✗ Failed in {elapsed:.2f} seconds: {e}")
        return elapsed, None, 'error'

# Test 1: Load nodes CSV
print("\n" + "="*60)
print("EXAMPLE 1: Basic Node/Edge Exploration")
print("="*60)

elapsed_nodes, df_nodes, status_nodes = time_operation(
    "Load nodes CSV (intermodal-217.csv)",
    lambda: pd.read_csv(f"{BASE_URL}intermodal-217.csv")
)

# Test 2: Load edges for each mode
print("\n" + "="*60)
print("EXAMPLE 1 & 2: Load Edges by Mode")
print("="*60)

elapsed_h, edges_h, status_h = time_operation(
    "Load Highway edges (H-adj.pickle)",
    lambda: load_pickle_from_url(f"{BASE_URL}H-adj.pickle")
)

elapsed_r, edges_r, status_r = time_operation(
    "Load Railway edges (R-adj.pickle)",
    lambda: load_pickle_from_url(f"{BASE_URL}R-adj.pickle")
)

elapsed_w, edges_w, status_w = time_operation(
    "Load Waterway edges (W-adj.pickle)",
    lambda: load_pickle_from_url(f"{BASE_URL}W-adj.pickle")
)

# Test 3: Load demand
print("\n" + "="*60)
print("EXAMPLE 3: Demand Lookup")
print("="*60)

elapsed_demand, demand, status_demand = time_operation(
    "Load demand data (demand.pickle)",
    lambda: load_pickle_from_url(f"{BASE_URL}demand.pickle")
)

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)

results = [
    ("Load nodes CSV", elapsed_nodes, status_nodes),
    ("Load Highway edges", elapsed_h, status_h),
    ("Load Railway edges", elapsed_r, status_r),
    ("Load Waterway edges", elapsed_w, status_w),
    ("Load demand data", elapsed_demand, status_demand),
]

print(f"\n{'Operation':<30} {'Time (s)':<12} {'Status'}")
print("-" * 60)
for op, elapsed, status in results:
    if status == 'timeout':
        status_str = "⏱️ TIMEOUT"
    elif status == 'error':
        status_str = "✗ ERROR"
    elif elapsed > 10:
        status_str = "⚠️ SLOW"
    else:
        status_str = "✓ OK"
    print(f"{op:<30} {elapsed:>8.2f}s    {status_str}")

print("\n" + "="*60)
print("RECOMMENDATIONS FOR UI")
print("="*60)

slow_or_timeout = [(op, elapsed, status) for op, elapsed, status in results if elapsed > 10 or status in ['timeout', 'error']]
if slow_or_timeout:
    print("\n⚠️  The following operations need UI improvements:")
    for op, elapsed, status in slow_or_timeout:
        if status == 'timeout':
            print(f"   - {op}: TIMEOUT - Add progress spinner + 'This may take a moment...' warning")
        elif elapsed > 10:
            print(f"   - {op}: {elapsed:.1f}s - Add loading indicator")
else:
    print("\n✓ All operations complete quickly - minimal UI changes needed!")

# Example-specific timings
print("\n" + "="*60)
print("EXAMPLE-SPECIFIC ESTIMATES")
print("="*60)

print(f"\nExample 1 (Load Nodes): ~{elapsed_nodes:.1f}s")
print(f"Example 1 (Load Edges - any mode): ~{max(elapsed_h, elapsed_r, elapsed_w):.1f}s")
print(f"Example 2 (Find Neighbors): ~{max(elapsed_h, elapsed_r, elapsed_w):.1f}s (edges only, nodes pre-loaded)")
print(f"Example 3 (Demand Lookup): ~{elapsed_demand:.1f}s")
if all(s == 'success' for _, _, s in results):
    total_stats = elapsed_nodes + elapsed_h + elapsed_r + elapsed_w + elapsed_demand
    print(f"Example 4 (Dataset Stats): ~{total_stats:.1f}s (loads everything)")
    total_comp = elapsed_h + elapsed_r + elapsed_w
    print(f"Example 5 (Mode Comparison): ~{total_comp:.1f}s (all edges)")
else:
    print(f"Example 4 (Dataset Stats): N/A (some operations timed out)")
    print(f"Example 5 (Mode Comparison): N/A (some operations timed out)")

print("\n")
