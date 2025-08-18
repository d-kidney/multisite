#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

def copy_enquiry_files():
    """Copy all enquiry system files from build4less to shared folder."""
    
    source_dir = r"C:\Users\User\projects\shopify\multisite\themes\build4less"
    shared_dir = r"C:\Users\User\projects\shopify\multisite\shared"
    
    # Define all files to copy
    files_to_copy = {
        # Enquiry System Core
        'assets/enquiry.js': 'Main enquiry cart functionality',
        'assets/enquiry-form.js': 'Form handling and submission',
        'assets/enquiry-config.js': 'Configuration settings',
        'assets/component-enquiry.css': 'Enquiry styles',
        'assets/enquiry-checkout-style.css': 'Checkout styling',
        
        # Enquiry UI Components
        'snippets/enquiry-drawer.liquid': 'Sliding drawer interface',
        'snippets/enquiry-icon-bubble.liquid': 'Header cart icon',
        'snippets/enquiry-notification.liquid': 'Success notifications',
        'snippets/page-enquiry-form.liquid': 'Full enquiry form page',
        'templates/page.enquiry-form.liquid': 'Page template',
        
        # Grouped Products & Availability
        'assets/custom-grouped-product-option-picker.js': 'Option selection',
        'assets/custom-grouped-product.css': 'Grouped product styles',
        'snippets/custom-grouped-product-option-picker.liquid': 'UI component',
        'snippets/custom-grouped-product-pricing.liquid': 'Pricing display',
        'snippets/custom-product-availability.liquid': 'Availability status',
        'assets/unavailable-product.js': 'Unavailable product handler',
        'assets/unavailable-variant-handler.js': 'Unavailable variant handler',
        'snippets/unavailable-product-notice.liquid': 'Unavailable notice',
        'snippets/unavailable-variant-notice.liquid': 'Variant notice',
        
        # Additional files found in build4less
        'assets/search-zindex-fix.js': 'Search z-index fix',
        'snippets/b2b-header-mega-menu.liquid': 'B2B header menu',
        'snippets/shoplift.liquid': 'Shoplift integration'
    }
    
    print("=" * 80)
    print("COPYING ENQUIRY SYSTEM FILES TO /SHARED/")
    print("=" * 80)
    
    copied_count = 0
    skipped_count = 0
    total_size = 0
    
    for file_path, description in files_to_copy.items():
        source = os.path.join(source_dir, file_path)
        destination = os.path.join(shared_dir, file_path)
        
        if os.path.exists(source):
            # Create destination directory if needed
            dest_dir = os.path.dirname(destination)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            
            # Copy the file
            shutil.copy2(source, destination)
            file_size = os.path.getsize(source)
            total_size += file_size
            copied_count += 1
            
            print(f"[OK] Copied: {file_path}")
            print(f"     Description: {description}")
            print(f"     Size: {file_size:,} bytes")
        else:
            print(f"[SKIP] Not found: {file_path}")
            skipped_count += 1
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Files copied: {copied_count}")
    print(f"Files skipped: {skipped_count}")
    print(f"Total size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    
    return copied_count, skipped_count, total_size

def main():
    copied, skipped, size = copy_enquiry_files()
    
    if copied > 0:
        print("\nNext steps:")
        print("1. Commit these changes")
        print("2. Deploy to all stores")
        print("3. Test enquiry system functionality")

if __name__ == "__main__":
    main()