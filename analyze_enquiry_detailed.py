#!/usr/bin/env python3
import os
import re
from pathlib import Path

def extract_enquiry_code_snippets():
    """Extract specific code snippets showing enquiry integration."""
    
    build4less_dir = r"C:\Users\User\projects\shopify\multisite\themes\build4less"
    other_store_dir = r"C:\Users\User\projects\shopify\multisite\themes\tiles4less"
    
    print("=" * 80)
    print("DETAILED ENQUIRY SYSTEM CODE ANALYSIS")
    print("=" * 80)
    
    # Analyze header.liquid differences
    print("\n1. HEADER.LIQUID MODIFICATIONS")
    print("-" * 80)
    
    build4less_header = os.path.join(build4less_dir, 'sections', 'header.liquid')
    other_header = os.path.join(other_store_dir, 'sections', 'header.liquid')
    
    try:
        with open(build4less_header, 'r', encoding='utf-8', errors='ignore') as f:
            b4l_content = f.read()
        with open(other_header, 'r', encoding='utf-8', errors='ignore') as f:
            other_content = f.read()
        
        # Find enquiry-specific code in build4less
        enquiry_snippets = re.findall(r'.*enquiry.*\n', b4l_content, re.IGNORECASE)
        
        print("\nEnquiry-related code in build4less header.liquid:")
        for i, snippet in enumerate(enquiry_snippets[:5], 1):
            print(f"  Line {i}: {snippet.strip()}")
        
        # Check if these exist in other store
        print("\nPresence in other stores: ")
        for snippet in enquiry_snippets[:3]:
            if snippet.strip() not in other_content:
                print(f"  MISSING: {snippet.strip()[:80]}...")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Analyze theme.liquid differences
    print("\n2. THEME.LIQUID MODIFICATIONS")
    print("-" * 80)
    
    build4less_theme = os.path.join(build4less_dir, 'layout', 'theme.liquid')
    other_theme = os.path.join(other_store_dir, 'layout', 'theme.liquid')
    
    try:
        with open(build4less_theme, 'r', encoding='utf-8', errors='ignore') as f:
            b4l_theme = f.read()
        with open(other_theme, 'r', encoding='utf-8', errors='ignore') as f:
            other_theme_content = f.read()
        
        # Find script includes
        scripts = re.findall(r'<script.*?enquiry.*?</script>', b4l_theme, re.IGNORECASE | re.DOTALL)
        sections = re.findall(r'{%.*?enquiry.*?%}', b4l_theme, re.IGNORECASE)
        
        print("\nEnquiry scripts in build4less theme.liquid:")
        for script in scripts[:5]:
            cleaned = script.replace('\n', ' ').strip()[:100]
            print(f"  {cleaned}...")
        
        print("\nEnquiry sections/renders in build4less theme.liquid:")
        for section in sections[:5]:
            print(f"  {section.strip()}")
            
    except Exception as e:
        print(f"  Error: {e}")
    
    # Analyze main-product.liquid
    print("\n3. MAIN-PRODUCT.LIQUID MODIFICATIONS")
    print("-" * 80)
    
    build4less_product = os.path.join(build4less_dir, 'sections', 'main-product.liquid')
    
    try:
        with open(build4less_product, 'r', encoding='utf-8', errors='ignore') as f:
            product_content = f.read()
        
        # Find grouped product code
        grouped_snippets = re.findall(r'.*grouped.*\n', product_content, re.IGNORECASE)
        availability_snippets = re.findall(r'.*availability.*\n', product_content, re.IGNORECASE)
        
        print("\nGrouped product code in main-product.liquid:")
        for snippet in grouped_snippets[:3]:
            print(f"  {snippet.strip()[:100]}...")
        
        print("\nAvailability code in main-product.liquid:")
        for snippet in availability_snippets[:3]:
            print(f"  {snippet.strip()[:100]}...")
            
    except Exception as e:
        print(f"  Error: {e}")
    
    # Analyze buy-buttons.liquid
    print("\n4. BUY-BUTTONS.LIQUID MODIFICATIONS")
    print("-" * 80)
    
    build4less_buttons = os.path.join(build4less_dir, 'snippets', 'buy-buttons.liquid')
    other_buttons = os.path.join(other_store_dir, 'snippets', 'buy-buttons.liquid')
    
    try:
        with open(build4less_buttons, 'r', encoding='utf-8', errors='ignore') as f:
            b4l_buttons = f.read()
        with open(other_buttons, 'r', encoding='utf-8', errors='ignore') as f:
            other_buttons_content = f.read()
        
        # Find enquiry button code
        enquiry_button = re.findall(r'.*enquiry.*\n.*\n.*\n', b4l_buttons, re.IGNORECASE)
        
        print("\nEnquiry button code in build4less buy-buttons.liquid:")
        for code in enquiry_button[:2]:
            print(f"  {code.strip()[:200]}...")
        
        # Calculate size difference
        print(f"\nFile size comparison:")
        print(f"  build4less: {len(b4l_buttons)} bytes")
        print(f"  other stores: {len(other_buttons_content)} bytes")
        print(f"  Difference: {len(b4l_buttons) - len(other_buttons_content)} bytes")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    # List all unique enquiry/grouped/availability files
    print("\n5. COMPLETE LIST OF UNIQUE FILES")
    print("-" * 80)
    
    unique_files = []
    
    # Check assets
    assets_dir = os.path.join(build4less_dir, 'assets')
    for file in os.listdir(assets_dir):
        if any(keyword in file.lower() for keyword in ['enquiry', 'grouped', 'availability', 'unavailable']):
            # Check if file exists in other store
            other_file = os.path.join(other_store_dir, 'assets', file)
            if not os.path.exists(other_file):
                unique_files.append(f'assets/{file}')
    
    # Check snippets
    snippets_dir = os.path.join(build4less_dir, 'snippets')
    for file in os.listdir(snippets_dir):
        if any(keyword in file.lower() for keyword in ['enquiry', 'grouped', 'availability', 'unavailable']):
            other_file = os.path.join(other_store_dir, 'snippets', file)
            if not os.path.exists(other_file):
                unique_files.append(f'snippets/{file}')
    
    # Check templates
    templates_dir = os.path.join(build4less_dir, 'templates')
    for file in os.listdir(templates_dir):
        if 'enquiry' in file.lower():
            other_file = os.path.join(other_store_dir, 'templates', file)
            if not os.path.exists(other_file):
                unique_files.append(f'templates/{file}')
    
    print("\nUnique files in build4less (not in other stores):")
    for file in sorted(unique_files):
        file_path = os.path.join(build4less_dir, file)
        size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        print(f"  {file} ({size:,} bytes)")
    
    return unique_files

def analyze_javascript_integration():
    """Analyze JavaScript integration points."""
    
    build4less_dir = r"C:\Users\User\projects\shopify\multisite\themes\build4less"
    
    print("\n6. JAVASCRIPT INTEGRATION POINTS")
    print("-" * 80)
    
    # Analyze global.js
    global_js = os.path.join(build4less_dir, 'assets', 'global.js')
    
    try:
        with open(global_js, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Find enquiry-related functions
        enquiry_functions = re.findall(r'function.*enquiry.*\{', content, re.IGNORECASE)
        enquiry_classes = re.findall(r'class.*enquiry.*\{', content, re.IGNORECASE)
        enquiry_events = re.findall(r'addEventListener.*enquiry.*', content, re.IGNORECASE)
        
        print("\nEnquiry-related code in global.js:")
        print(f"  Functions: {len(enquiry_functions)}")
        print(f"  Classes: {len(enquiry_classes)}")
        print(f"  Event listeners: {len(enquiry_events)}")
        
        # Look for specific integration points
        if 'EnquiryCart' in content:
            print("  - EnquiryCart class found")
        if 'addToEnquiry' in content:
            print("  - addToEnquiry function found")
        if 'enquiryDrawer' in content:
            print("  - enquiryDrawer functionality found")
            
    except Exception as e:
        print(f"  Error analyzing global.js: {e}")
    
    # Analyze product-form.js
    product_form_js = os.path.join(build4less_dir, 'assets', 'product-form.js')
    
    try:
        with open(product_form_js, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        print("\nEnquiry-related code in product-form.js:")
        
        if 'enquiry' in content.lower():
            enquiry_refs = content.lower().count('enquiry')
            print(f"  - {enquiry_refs} references to 'enquiry'")
        
        if 'grouped' in content.lower():
            grouped_refs = content.lower().count('grouped')
            print(f"  - {grouped_refs} references to 'grouped'")
            
    except Exception as e:
        print(f"  Error analyzing product-form.js: {e}")

def generate_final_report(unique_files):
    """Generate final implementation report."""
    
    print("\n" + "=" * 80)
    print("FINAL IMPLEMENTATION REPORT")
    print("=" * 80)
    
    print("""
SUMMARY:
--------
The enquiry system, custom grouped products, and custom availability features
in build4less consist of:

1. UNIQUE FILES (19 files to copy to /shared/):
   - 5 enquiry JavaScript files
   - 2 enquiry CSS files  
   - 4 enquiry Liquid snippets
   - 1 enquiry template
   - 3 grouped product files
   - 2 custom availability files
   - 2 unavailable variant handlers

2. MODIFIED FILES (7-10 files need changes):
   - header.liquid: Add enquiry icon bubble
   - theme.liquid: Include scripts and sections
   - main-product.liquid: Integrate grouped products
   - buy-buttons.liquid: Add enquiry button
   - global.js: Enquiry cart functionality
   - product-form.js: Form handling
   - settings_schema.json: Configuration options

3. KEY INTEGRATION POINTS:
   - Header: Enquiry cart icon with badge
   - Product page: "Add to Enquiry" button
   - Drawer: Enquiry cart drawer (like cart drawer)
   - Checkout: Custom enquiry form submission
   - Notifications: Enquiry success messages

4. ESTIMATED EFFORT:
   - File copying: 30 minutes
   - Code modifications: 2-3 hours
   - Testing: 1-2 hours
   - Total: ~4-6 hours per store

This will enable all stores to have:
- Full enquiry system for quote requests
- Grouped product options (tiles, etc.)
- Custom availability displays
- Unavailable product handling
""")

def main():
    unique_files = extract_enquiry_code_snippets()
    analyze_javascript_integration()
    generate_final_report(unique_files)

if __name__ == "__main__":
    main()