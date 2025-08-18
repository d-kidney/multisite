#!/usr/bin/env python3
import os
import json
import shutil
from pathlib import Path

def copy_shared_files():
    """Copy all identical files to the shared folder."""
    
    # Load the analysis results
    with open('shared_files_analysis.json', 'r') as f:
        results = json.load(f)
    
    shared_candidates = results['shared_candidates']
    source_store = 'build4less'  # Use build4less as the source
    
    print("Copying shared files from build4less to /shared/ folder...")
    print("-" * 60)
    
    total_files = 0
    copied_files = 0
    
    # Process each category of files
    for category, files in shared_candidates.items():
        if not files:
            continue
            
        print(f"\nProcessing {category.upper()}: {len(files)} files")
        
        for file_path in files:
            total_files += 1
            source = os.path.join('themes', source_store, file_path)
            destination = os.path.join('shared', file_path)
            
            try:
                # Create destination directory if it doesn't exist
                dest_dir = os.path.dirname(destination)
                if dest_dir and not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                
                # Copy the file
                if os.path.exists(source):
                    shutil.copy2(source, destination)
                    copied_files += 1
                    if copied_files <= 10 or copied_files % 50 == 0:
                        print(f"  [OK] Copied: {file_path}")
                else:
                    print(f"  [WARN] Source not found: {source}")
                    
            except Exception as e:
                print(f"  [ERROR] Error copying {file_path}: {e}")
    
    print("\n" + "=" * 60)
    print(f"COMPLETED: Copied {copied_files} of {total_files} files to /shared/")
    print("=" * 60)
    
    # Create a summary file
    summary = {
        'total_shared_files': copied_files,
        'source_store': source_store,
        'categories': {}
    }
    
    for category, files in shared_candidates.items():
        if files:
            summary['categories'][category] = len(files)
    
    with open('shared/SHARED_FILES_INFO.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\nSummary saved to shared/SHARED_FILES_INFO.json")
    print("\nNext steps:")
    print("1. Commit these changes")
    print("2. Deploy a test store (e.g., tiles4less)")
    print("3. Verify the shared files are correctly applied")

if __name__ == "__main__":
    copy_shared_files()