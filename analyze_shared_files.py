#!/usr/bin/env python3
import os
import hashlib
import json
from pathlib import Path
from collections import defaultdict

def get_file_hash(filepath):
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Error hashing {filepath}: {e}")
        return None

def analyze_themes(base_dir):
    """Analyze all theme files and identify identical ones."""
    stores = [
        'build4less',
        'tiles4less',
        'building-supplies-online',
        'insulation4less',
        'insulation4us',
        'roofing4us'
    ]
    
    # Dictionary to store file hashes: {relative_path: {store: hash}}
    file_hashes = defaultdict(dict)
    
    # Dictionary to store hash groups: {hash: {relative_path: [stores]}}
    hash_groups = defaultdict(lambda: defaultdict(list))
    
    print("Analyzing themes...")
    print("-" * 60)
    
    for store in stores:
        store_path = os.path.join(base_dir, store)
        if not os.path.exists(store_path):
            print(f"Warning: Store path not found: {store_path}")
            continue
            
        print(f"Processing {store}...")
        
        for root, dirs, files in os.walk(store_path):
            # Skip .git and node_modules
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules']]
            
            for file in files:
                file_path = os.path.join(root, file)
                # Get relative path from store root
                relative_path = os.path.relpath(file_path, store_path).replace('\\', '/')
                
                # Calculate hash
                file_hash = get_file_hash(file_path)
                if file_hash:
                    file_hashes[relative_path][store] = file_hash
                    hash_groups[file_hash][relative_path].append(store)
    
    return file_hashes, hash_groups, stores

def categorize_files(file_hashes, stores):
    """Categorize files by how many stores they're identical across."""
    categories = {
        'all_stores': [],      # Files identical across all 6 stores
        'five_stores': [],     # Files identical across 5 stores
        'four_stores': [],     # Files identical across 4 stores
        'three_stores': [],    # Files identical across 3 stores
        'unique': []           # Files unique to specific stores
    }
    
    for relative_path, store_hashes in file_hashes.items():
        # Get unique hashes for this file
        unique_hashes = set(store_hashes.values())
        
        if len(unique_hashes) == 1 and len(store_hashes) == len(stores):
            # Same hash in all stores
            categories['all_stores'].append(relative_path)
        elif len(store_hashes) == len(stores):
            # File exists in all stores but with different content
            if len(unique_hashes) == 2:
                # Find which stores have which version
                hash_counts = defaultdict(list)
                for store, hash_val in store_hashes.items():
                    hash_counts[hash_val].append(store)
                
                for hash_val, store_list in hash_counts.items():
                    if len(store_list) == 5:
                        categories['five_stores'].append({
                            'file': relative_path,
                            'identical_in': store_list,
                            'different_in': [s for s in stores if s not in store_list]
                        })
                    elif len(store_list) == 4:
                        categories['four_stores'].append({
                            'file': relative_path,
                            'identical_in': store_list,
                            'different_in': [s for s in stores if s not in store_list]
                        })
                    elif len(store_list) == 3:
                        categories['three_stores'].append({
                            'file': relative_path,
                            'identical_in': store_list
                        })
    
    return categories

def organize_by_type(files):
    """Organize files by their type (assets, sections, snippets, etc.)."""
    organized = defaultdict(list)
    
    for file_path in files:
        if file_path.startswith('assets/'):
            organized['assets'].append(file_path)
        elif file_path.startswith('sections/'):
            organized['sections'].append(file_path)
        elif file_path.startswith('snippets/'):
            organized['snippets'].append(file_path)
        elif file_path.startswith('templates/'):
            organized['templates'].append(file_path)
        elif file_path.startswith('config/'):
            organized['config'].append(file_path)
        elif file_path.startswith('layout/'):
            organized['layout'].append(file_path)
        elif file_path.startswith('locales/'):
            organized['locales'].append(file_path)
        elif file_path.startswith('blocks/'):
            organized['blocks'].append(file_path)
        else:
            organized['other'].append(file_path)
    
    return organized

def main():
    base_dir = r"C:\Users\User\projects\shopify\multisite\themes"
    
    # Analyze themes
    file_hashes, hash_groups, stores = analyze_themes(base_dir)
    
    # Categorize files
    categories = categorize_files(file_hashes, stores)
    
    # Organize files identical across all stores by type
    all_stores_by_type = organize_by_type(categories['all_stores'])
    
    # Print results
    print("\n" + "=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)
    
    print(f"\nTotal unique files analyzed: {len(file_hashes)}")
    print(f"Files identical across ALL 6 stores: {len(categories['all_stores'])}")
    print(f"Files identical across 5 stores: {len(categories['five_stores'])}")
    print(f"Files identical across 4 stores: {len(categories['four_stores'])}")
    
    print("\n" + "-" * 60)
    print("FILES IDENTICAL ACROSS ALL 6 STORES (Prime /shared/ candidates)")
    print("-" * 60)
    
    for file_type, files in sorted(all_stores_by_type.items()):
        if files:
            print(f"\n{file_type.upper()} ({len(files)} files):")
            for file_path in sorted(files)[:10]:  # Show first 10 of each type
                print(f"  - {file_path}")
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more")
    
    # Calculate potential space savings
    total_shared_files = len(categories['all_stores'])
    potential_savings = total_shared_files * (len(stores) - 1)
    print(f"\nPOTENTIAL IMPACT:")
    print(f"Moving {total_shared_files} shared files would eliminate {potential_savings} duplicate files")
    
    # Save detailed results to JSON
    results = {
        'summary': {
            'total_files': len(file_hashes),
            'identical_all_stores': len(categories['all_stores']),
            'identical_5_stores': len(categories['five_stores']),
            'identical_4_stores': len(categories['four_stores'])
        },
        'shared_candidates': all_stores_by_type,
        'partial_matches': {
            'five_stores': categories['five_stores'][:20],  # First 20 examples
            'four_stores': categories['four_stores'][:20]   # First 20 examples
        }
    }
    
    with open('shared_files_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nDetailed results saved to shared_files_analysis.json")
    
    # Print files that are nearly universal (5 stores)
    if categories['five_stores']:
        print("\n" + "-" * 60)
        print("FILES IDENTICAL IN 5 STORES (Consider for /shared/ with override)")
        print("-" * 60)
        for item in categories['five_stores'][:10]:
            print(f"  - {item['file']}")
            print(f"    Different in: {', '.join(item['different_in'])}")

if __name__ == "__main__":
    main()