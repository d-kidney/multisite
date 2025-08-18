#!/usr/bin/env python3
"""
Analyze non-shared files across all 6 Shopify stores to understand store uniqueness.
This script categorizes files that are NOT in the shared folder.
"""

import os
import json
import hashlib
from pathlib import Path
from collections import defaultdict

def get_file_hash(filepath):
    """Get MD5 hash of a file"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def get_file_size(filepath):
    """Get file size"""
    try:
        return os.path.getsize(filepath)
    except:
        return 0

def analyze_non_shared_files():
    """Analyze files that exist in stores but are NOT in the shared folder"""
    
    themes_dir = Path("C:/Users/User/projects/shopify/multisite/themes")
    shared_dir = Path("C:/Users/User/projects/shopify/multisite/shared")
    stores = ["build4less", "tiles4less", "building-supplies-online", "insulation4less", "insulation4us", "roofing4us"]
    
    # Get list of shared files
    shared_files = set()
    if shared_dir.exists():
        for root, dirs, files in os.walk(shared_dir):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), shared_dir)
                shared_files.add(rel_path.replace("\\", "/"))
    
    print(f"Found {len(shared_files)} shared files")
    
    # Analyze non-shared files
    non_shared_analysis = {
        "summary": {},
        "files_in_all_stores_different_content": [],  # Files in all 6 stores but with different content
        "files_in_some_stores_only": [],              # Files in some stores but not others
        "store_unique_files": {store: [] for store in stores},  # Files unique to each store
        "file_size_analysis": {},
        "critical_identity_files": {}
    }
    
    # Collect all files from all stores
    all_files_by_store = {}
    file_presence = defaultdict(list)  # file_path -> [stores where it exists]
    file_hashes = {}  # (store, file_path) -> hash
    
    for store in stores:
        store_path = themes_dir / store
        all_files_by_store[store] = []
        
        if not store_path.exists():
            print(f"Warning: Store {store} not found")
            continue
            
        for root, dirs, files in os.walk(store_path):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, store_path)
                rel_path = rel_path.replace("\\", "/")
                
                # Skip if file is in shared folder
                if rel_path in shared_files:
                    continue
                
                all_files_by_store[store].append(rel_path)
                file_presence[rel_path].append(store)
                file_hashes[(store, rel_path)] = get_file_hash(full_path)
    
    print(f"Analyzing non-shared files...")
    
    # Categorize files
    for file_path, stores_with_file in file_presence.items():
        if len(stores_with_file) == 6:
            # File exists in all stores - check if content is different
            hashes = [file_hashes.get((store, file_path)) for store in stores_with_file]
            unique_hashes = set(h for h in hashes if h is not None)
            
            if len(unique_hashes) > 1:
                # Different content across stores
                store_hash_map = {store: file_hashes.get((store, file_path)) for store in stores_with_file}
                non_shared_analysis["files_in_all_stores_different_content"].append({
                    "file": file_path,
                    "store_hashes": store_hash_map,
                    "unique_versions": len(unique_hashes)
                })
        elif len(stores_with_file) < 6:
            # File exists in some stores but not others
            missing_stores = [store for store in stores if store not in stores_with_file]
            non_shared_analysis["files_in_some_stores_only"].append({
                "file": file_path,
                "exists_in": stores_with_file,
                "missing_from": missing_stores,
                "store_count": len(stores_with_file)
            })
        
        # Check for store-unique files (files that exist only in one store)
        if len(stores_with_file) == 1:
            store = stores_with_file[0]
            file_size = get_file_size(themes_dir / store / file_path)
            non_shared_analysis["store_unique_files"][store].append({
                "file": file_path,
                "size": file_size
            })
    
    # Identify critical identity files (files that likely define store uniqueness)
    critical_patterns = [
        "config/settings_data.json",
        "assets/custom.css", 
        "assets/base.css",
        "layout/theme.liquid",
        "templates/index.json"
    ]
    
    for pattern in critical_patterns:
        stores_with_pattern = []
        pattern_analysis = {}
        
        for store in stores:
            matching_files = [f for f in all_files_by_store.get(store, []) if pattern in f]
            if matching_files:
                stores_with_pattern.append(store)
                file_path = themes_dir / store / matching_files[0]
                pattern_analysis[store] = {
                    "file": matching_files[0],
                    "size": get_file_size(file_path),
                    "hash": get_file_hash(file_path)
                }
        
        if pattern_analysis:
            non_shared_analysis["critical_identity_files"][pattern] = {
                "stores_with_file": stores_with_pattern,
                "analysis": pattern_analysis,
                "all_identical": len(set(info["hash"] for info in pattern_analysis.values() if info["hash"])) <= 1
            }
    
    # Generate summary statistics
    non_shared_analysis["summary"] = {
        "total_non_shared_files": sum(len(files) for files in all_files_by_store.values()),
        "files_in_all_stores_different_content": len(non_shared_analysis["files_in_all_stores_different_content"]),
        "files_in_some_stores_only": len(non_shared_analysis["files_in_some_stores_only"]),
        "store_unique_counts": {store: len(files) for store, files in non_shared_analysis["store_unique_files"].items()},
        "stores_analyzed": stores
    }
    
    return non_shared_analysis

if __name__ == "__main__":
    analysis = analyze_non_shared_files()
    
    # Save analysis
    output_file = "C:/Users/User/projects/shopify/multisite/non_shared_files_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"\nAnalysis saved to {output_file}")
    
    # Print summary
    print("\n=== NON-SHARED FILES ANALYSIS SUMMARY ===")
    print(f"Total non-shared files analyzed: {analysis['summary']['total_non_shared_files']}")
    print(f"Files in ALL stores but with DIFFERENT content: {analysis['summary']['files_in_all_stores_different_content']}")
    print(f"Files in SOME stores only: {analysis['summary']['files_in_some_stores_only']}")
    
    print("\n=== STORE-UNIQUE FILE COUNTS ===")
    for store, count in analysis['summary']['store_unique_counts'].items():
        print(f"{store}: {count} unique files")
    
    print("\n=== TOP FILES IN ALL STORES WITH DIFFERENT CONTENT ===")
    for item in analysis["files_in_all_stores_different_content"][:10]:
        print(f"- {item['file']} ({item['unique_versions']} versions)")
    
    print("\n=== CRITICAL IDENTITY FILES ===")
    for pattern, info in analysis["critical_identity_files"].items():
        identical = "✓ IDENTICAL" if info["all_identical"] else "✗ DIFFERENT"
        print(f"- {pattern}: {len(info['stores_with_file'])} stores, {identical}")