#!/usr/bin/env python3
import os
import json
import hashlib
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
        return None

def get_file_size(filepath):
    """Get file size in bytes."""
    try:
        return os.path.getsize(filepath)
    except:
        return 0

def load_shared_files():
    """Load list of files already in shared folder."""
    shared_files = set()
    shared_dir = r"C:\Users\User\projects\shopify\multisite\shared"
    
    for root, dirs, files in os.walk(shared_dir):
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules']]
        for file in files:
            if file != 'SHARED_FILES_INFO.json':
                rel_path = os.path.relpath(os.path.join(root, file), shared_dir).replace('\\', '/')
                shared_files.add(rel_path)
    
    return shared_files

def analyze_nonshared_files():
    """Analyze files that are not in the shared folder."""
    base_dir = r"C:\Users\User\projects\shopify\multisite\themes"
    stores = ['build4less', 'tiles4less', 'building-supplies-online', 
              'insulation4less', 'insulation4us', 'roofing4us']
    
    # Load shared files list
    shared_files = load_shared_files()
    print(f"Found {len(shared_files)} files in /shared/ folder\n")
    
    # Collect all files from all stores
    store_files = defaultdict(dict)  # {store: {file_path: hash}}
    file_presence = defaultdict(list)  # {file_path: [stores that have it]}
    file_sizes = defaultdict(dict)  # {file_path: {store: size}}
    
    print("Analyzing stores...")
    print("-" * 60)
    
    for store in stores:
        store_path = os.path.join(base_dir, store)
        if not os.path.exists(store_path):
            continue
            
        print(f"Processing {store}...")
        
        for root, dirs, files in os.walk(store_path):
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules']]
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, store_path).replace('\\', '/')
                
                # Skip if file is in shared folder
                if rel_path in shared_files:
                    continue
                
                file_hash = get_file_hash(file_path)
                file_size = get_file_size(file_path)
                
                if file_hash:
                    store_files[store][rel_path] = file_hash
                    file_presence[rel_path].append(store)
                    file_sizes[rel_path][store] = file_size
    
    # Categorize non-shared files
    categories = {
        'different_content_all_stores': [],  # Files in all stores but different
        'different_content_most_stores': [], # Files in 4-5 stores with different content
        'store_specific': defaultdict(list), # Files unique to specific stores
        'partially_shared': [],              # Files identical in some stores
    }
    
    # Analyze each file
    for file_path, stores_with_file in file_presence.items():
        if len(stores_with_file) == len(stores):
            # File exists in all stores
            hashes = {store_files[store][file_path] for store in stores_with_file}
            if len(hashes) > 1:
                # Different content across stores
                categories['different_content_all_stores'].append({
                    'file': file_path,
                    'sizes': {store: file_sizes[file_path][store] for store in stores_with_file}
                })
        elif len(stores_with_file) >= 4:
            # File exists in most stores
            hashes = {store_files[store][file_path] for store in stores_with_file}
            categories['different_content_most_stores'].append({
                'file': file_path,
                'stores': stores_with_file,
                'unique_versions': len(hashes)
            })
        elif len(stores_with_file) == 1:
            # File unique to one store
            store = stores_with_file[0]
            categories['store_specific'][store].append(file_path)
        else:
            # File in some stores
            hashes = {store_files[store][file_path] for store in stores_with_file}
            if len(hashes) == 1:
                # Same content in all stores that have it
                categories['partially_shared'].append({
                    'file': file_path,
                    'stores': stores_with_file,
                    'could_be_shared': True
                })
    
    return categories, store_files, stores

def print_analysis_results(categories, store_files, stores):
    """Print formatted analysis results."""
    
    print("\n" + "=" * 60)
    print("NON-SHARED FILES ANALYSIS")
    print("=" * 60)
    
    # Files in all stores but different
    print(f"\n1. FILES IN ALL STORES WITH DIFFERENT CONTENT ({len(categories['different_content_all_stores'])} files)")
    print("-" * 60)
    for item in sorted(categories['different_content_all_stores'], key=lambda x: x['file']):
        print(f"\n  {item['file']}")
        sizes = item['sizes']
        min_size = min(sizes.values())
        max_size = max(sizes.values())
        if max_size - min_size > 1000:  # Significant size difference
            print(f"    Size range: {min_size:,} - {max_size:,} bytes (varies significantly)")
            for store, size in sorted(sizes.items()):
                print(f"      {store}: {size:,} bytes")
        else:
            print(f"    Size: ~{min_size:,} bytes (similar across stores)")
    
    # Store-specific files
    print(f"\n2. STORE-SPECIFIC FILES (unique to individual stores)")
    print("-" * 60)
    for store in stores:
        specific_files = categories['store_specific'].get(store, [])
        if specific_files:
            print(f"\n  {store.upper()} ({len(specific_files)} unique files):")
            
            # Group by type
            by_type = defaultdict(list)
            for file in specific_files:
                if file.startswith('assets/'):
                    if file.endswith('.js'):
                        by_type['JavaScript'].append(file)
                    elif file.endswith('.css'):
                        by_type['CSS'].append(file)
                    else:
                        by_type['Other Assets'].append(file)
                elif file.startswith('sections/'):
                    by_type['Sections'].append(file)
                elif file.startswith('snippets/'):
                    by_type['Snippets'].append(file)
                elif file.startswith('templates/'):
                    by_type['Templates'].append(file)
                else:
                    by_type['Other'].append(file)
            
            for file_type, files in sorted(by_type.items()):
                print(f"    {file_type}: {', '.join([f.split('/')[-1] for f in sorted(files)[:5]])}")
                if len(files) > 5:
                    print(f"      ... and {len(files) - 5} more")
    
    # Partially shared files
    if categories['partially_shared']:
        print(f"\n3. PARTIALLY SHARED FILES (could potentially move to /shared/)")
        print("-" * 60)
        for item in categories['partially_shared'][:10]:
            print(f"  {item['file']}")
            print(f"    Present in: {', '.join(item['stores'])}")
    
    # Summary statistics
    print(f"\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    total_nonshared = sum(len(store_files[store]) for store in stores)
    print(f"Total non-shared files across all stores: {total_nonshared}")
    print(f"Files different in all stores: {len(categories['different_content_all_stores'])}")
    print(f"Files different in most stores: {len(categories['different_content_most_stores'])}")
    print(f"Partially shared (opportunity): {len(categories['partially_shared'])}")
    
    # Store uniqueness
    print(f"\nStore Uniqueness Index:")
    for store in stores:
        unique_count = len(categories['store_specific'].get(store, []))
        total_count = len(store_files.get(store, {}))
        if total_count > 0:
            uniqueness = (unique_count / total_count) * 100
            print(f"  {store}: {unique_count} unique files ({uniqueness:.1f}% of non-shared)")

def identify_key_differences():
    """Identify the key files that define each store's identity."""
    print(f"\n" + "=" * 60)
    print("KEY STORE IDENTITY FILES")
    print("=" * 60)
    
    identity_files = {
        'Branding & Settings': [
            'config/settings_data.json',
            'assets/custom.css',
            'locales/en.default.json'
        ],
        'Store Features': [
            'assets/enquiry.js',
            'assets/enquiry-form.js',
            'assets/custom-grouped-product.js',
            'snippets/enquiry-drawer.liquid'
        ],
        'Visual Identity': [
            'assets/base.css',
            'sections/header.liquid',
            'sections/footer.liquid'
        ]
    }
    
    for category, files in identity_files.items():
        print(f"\n{category}:")
        for file in files:
            print(f"  - {file}")
    
    print(f"\nThese files are critical for maintaining each store's unique:")
    print("  • Brand identity (logos, colors, fonts)")
    print("  • Store-specific features (enquiry system, product grouping)")
    print("  • Custom functionality and user experience")
    print("  • Localized content and messaging")

def main():
    # Run analysis
    categories, store_files, stores = analyze_nonshared_files()
    
    # Print results
    print_analysis_results(categories, store_files, stores)
    
    # Identify key differences
    identify_key_differences()
    
    # Save detailed results
    results = {
        'summary': {
            'total_nonshared_files': sum(len(store_files[store]) for store in stores),
            'different_all_stores': len(categories['different_content_all_stores']),
            'different_most_stores': len(categories['different_content_most_stores']),
            'partially_shared': len(categories['partially_shared'])
        },
        'different_content_all_stores': categories['different_content_all_stores'][:20],
        'store_specific_counts': {
            store: len(categories['store_specific'].get(store, []))
            for store in stores
        },
        'partially_shared_opportunities': categories['partially_shared'][:20]
    }
    
    with open('nonshared_files_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to nonshared_files_analysis.json")

if __name__ == "__main__":
    main()