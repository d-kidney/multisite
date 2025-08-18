#!/usr/bin/env python3
import os
import re
import json
from pathlib import Path

def search_for_references(directory, patterns, file_extensions):
    """Search for pattern references in files."""
    references = {}
    
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules']]
        
        for file in files:
            # Check if file has relevant extension
            if not any(file.endswith(ext) for ext in file_extensions):
                continue
                
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, directory).replace('\\', '/')
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    for pattern_name, pattern in patterns.items():
                        if re.search(pattern, content, re.IGNORECASE):
                            if rel_path not in references:
                                references[rel_path] = []
                            references[rel_path].append(pattern_name)
            except:
                pass
    
    return references

def analyze_enquiry_system():
    """Analyze all components of the enquiry system."""
    
    build4less_dir = r"C:\Users\User\projects\shopify\multisite\themes\build4less"
    
    # Patterns to search for enquiry system references
    enquiry_patterns = {
        'enquiry-cart': r'enquiry[_-]?cart',
        'enquiry-form': r'enquiry[_-]?form',
        'enquiry-drawer': r'enquiry[_-]?drawer',
        'enquiry-icon': r'enquiry[_-]?icon',
        'enquiry-notification': r'enquiry[_-]?notification',
        'enquiry-config': r'enquiry[_-]?config',
        'enquiry-badge': r'enquiry[_-]?badge',
        'enquiry-checkout': r'enquiry[_-]?checkout',
        'addToEnquiry': r'addToEnquiry',
        'EnquiryCart': r'EnquiryCart',
        'enquirySubmit': r'enquirySubmit'
    }
    
    # Patterns for custom grouped products
    grouped_patterns = {
        'grouped-product': r'grouped[_-]?product',
        'custom-grouped': r'custom[_-]?grouped',
        'product-grouping': r'product[_-]?grouping',
        'group-options': r'group[_-]?options',
        'option-picker': r'option[_-]?picker'
    }
    
    # Patterns for custom product availability
    availability_patterns = {
        'custom-availability': r'custom[_-]?availability',
        'product-availability': r'product[_-]?availability',
        'availability-notice': r'availability[_-]?notice',
        'stock-status': r'stock[_-]?status',
        'unavailable-product': r'unavailable[_-]?product',
        'unavailable-variant': r'unavailable[_-]?variant'
    }
    
    file_extensions = ['.liquid', '.js', '.css', '.json']
    
    print("=" * 80)
    print("ENQUIRY SYSTEM, GROUPED PRODUCTS & AVAILABILITY ANALYSIS")
    print("=" * 80)
    
    # Find all references
    print("\nSearching for enquiry system references...")
    enquiry_refs = search_for_references(build4less_dir, enquiry_patterns, file_extensions)
    
    print("Searching for grouped product references...")
    grouped_refs = search_for_references(build4less_dir, grouped_patterns, file_extensions)
    
    print("Searching for availability references...")
    availability_refs = search_for_references(build4less_dir, availability_patterns, file_extensions)
    
    # Categorize files
    unique_enquiry_files = []
    modified_files = {}
    
    # Identify unique enquiry files
    for file in os.listdir(os.path.join(build4less_dir, 'assets')):
        if 'enquiry' in file.lower():
            unique_enquiry_files.append(f'assets/{file}')
    
    for file in os.listdir(os.path.join(build4less_dir, 'snippets')):
        if 'enquiry' in file.lower():
            unique_enquiry_files.append(f'snippets/{file}')
            
    # Check for grouped product files
    for file in os.listdir(os.path.join(build4less_dir, 'assets')):
        if 'grouped' in file.lower():
            unique_enquiry_files.append(f'assets/{file}')
            
    for file in os.listdir(os.path.join(build4less_dir, 'snippets')):
        if 'grouped' in file.lower():
            unique_enquiry_files.append(f'snippets/{file}')
    
    # Files that need modifications
    key_modified_files = [
        'sections/header.liquid',
        'sections/header-group.json',
        'layout/theme.liquid',
        'sections/main-product.liquid',
        'snippets/main-script.liquid',
        'snippets/buy-buttons.liquid',
        'assets/global.js',
        'assets/product-form.js',
        'config/settings_schema.json'
    ]
    
    print("\n" + "=" * 80)
    print("1. UNIQUE FILES TO MOVE TO /SHARED/")
    print("-" * 80)
    
    print("\nEnquiry System Files:")
    for file in sorted(unique_enquiry_files):
        if 'enquiry' in file.lower():
            print(f"  • {file}")
    
    print("\nGrouped Product Files:")
    for file in sorted(unique_enquiry_files):
        if 'grouped' in file.lower():
            print(f"  • {file}")
    
    print("\nAvailability Files:")
    for file in sorted(unique_enquiry_files):
        if 'unavailable' in file.lower() or 'availability' in file.lower():
            print(f"  • {file}")
    
    print("\n" + "=" * 80)
    print("2. FILES REQUIRING MODIFICATIONS")
    print("-" * 80)
    
    for file in key_modified_files:
        if file in enquiry_refs or file in grouped_refs or file in availability_refs:
            refs = []
            if file in enquiry_refs:
                refs.extend(enquiry_refs[file])
            if file in grouped_refs:
                refs.extend(grouped_refs[file])
            if file in availability_refs:
                refs.extend(availability_refs[file])
            
            print(f"\n{file}:")
            print(f"  References: {', '.join(set(refs))}")
    
    print("\n" + "=" * 80)
    print("3. DETAILED MODIFICATIONS NEEDED")
    print("-" * 80)
    
    # Analyze specific files for modifications
    analyze_header_modifications(build4less_dir)
    analyze_theme_liquid_modifications(build4less_dir)
    analyze_product_modifications(build4less_dir)
    
    return unique_enquiry_files, enquiry_refs, grouped_refs, availability_refs

def analyze_header_modifications(build4less_dir):
    """Analyze header.liquid for enquiry system modifications."""
    header_file = os.path.join(build4less_dir, 'sections', 'header.liquid')
    
    print("\n### sections/header.liquid")
    print("Modifications needed:")
    
    try:
        with open(header_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Look for enquiry-specific includes
            if 'enquiry-icon-bubble' in content:
                print("  • Add: {% render 'enquiry-icon-bubble' %} - Enquiry cart icon")
            
            if 'enquiry-drawer' in content:
                print("  • Add: Enquiry drawer functionality")
                
            # Find the specific code sections
            if re.search(r'{%-?\s*render\s+[\'"]enquiry-icon-bubble[\'"]', content):
                match = re.search(r'({%-?\s*render\s+[\'"]enquiry-icon-bubble[\'"][^%]*%})', content)
                if match:
                    print(f"  • Code snippet: {match.group(1)[:100]}...")
    except:
        pass

def analyze_theme_liquid_modifications(build4less_dir):
    """Analyze theme.liquid for enquiry system modifications."""
    theme_file = os.path.join(build4less_dir, 'layout', 'theme.liquid')
    
    print("\n### layout/theme.liquid")
    print("Modifications needed:")
    
    try:
        with open(theme_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Look for enquiry script includes
            if 'enquiry.js' in content:
                print("  • Add: <script src='{{ 'enquiry.js' | asset_url }}' defer></script>")
            
            if 'enquiry-config.js' in content:
                print("  • Add: <script src='{{ 'enquiry-config.js' | asset_url }}' defer></script>")
                
            if 'enquiry-form.js' in content:
                print("  • Add: <script src='{{ 'enquiry-form.js' | asset_url }}' defer></script>")
                
            if 'custom-grouped-product.js' in content:
                print("  • Add: <script src='{{ 'custom-grouped-product.js' | asset_url }}' defer></script>")
                
            if 'enquiry-drawer' in content:
                print("  • Add: {% section 'enquiry-drawer' %}")
                
            if 'enquiry-notification' in content:
                print("  • Add: {% render 'enquiry-notification' %}")
    except:
        pass

def analyze_product_modifications(build4less_dir):
    """Analyze product-related modifications."""
    product_file = os.path.join(build4less_dir, 'sections', 'main-product.liquid')
    buy_buttons = os.path.join(build4less_dir, 'snippets', 'buy-buttons.liquid')
    
    print("\n### sections/main-product.liquid")
    print("Modifications needed:")
    
    try:
        with open(product_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            if 'custom-grouped-product' in content:
                print("  • Add: Custom grouped product option picker")
                
            if 'custom-product-availability' in content:
                print("  • Add: Custom product availability display")
                
            if 'enquiry' in content.lower():
                print("  • Add: Enquiry form integration in product template")
    except:
        pass
    
    print("\n### snippets/buy-buttons.liquid")
    print("Modifications needed:")
    
    try:
        with open(buy_buttons, 'r', encoding='utf-8') as f:
            content = f.read()
            
            if 'add-to-enquiry' in content.lower():
                print("  • Add: 'Add to Enquiry' button alongside 'Add to Cart'")
                
            if 'enquiry-form-button' in content:
                print("  • Add: Enquiry form button functionality")
    except:
        pass

def generate_implementation_checklist():
    """Generate a checklist for implementing these features."""
    
    print("\n" + "=" * 80)
    print("4. IMPLEMENTATION CHECKLIST")
    print("-" * 80)
    
    checklist = """
[ ] 1. Copy Unique Files to /shared/:
   [ ] assets/enquiry.js
   [ ] assets/enquiry-form.js
   [ ] assets/enquiry-config.js
   [ ] assets/component-enquiry.css
   [ ] assets/enquiry-checkout-style.css
   [ ] assets/custom-grouped-product.js
   [ ] assets/custom-grouped-product-option-picker.js
   [ ] assets/custom-grouped-product.css
   [ ] assets/unavailable-product.js
   [ ] assets/unavailable-variant-handler.js
   [ ] snippets/enquiry-drawer.liquid
   [ ] snippets/enquiry-icon-bubble.liquid
   [ ] snippets/enquiry-notification.liquid
   [ ] snippets/page-enquiry-form.liquid
   [ ] snippets/custom-grouped-product-option-picker.liquid
   [ ] snippets/custom-grouped-product-pricing.liquid
   [ ] snippets/custom-product-availability.liquid
   [ ] snippets/unavailable-product-notice.liquid
   [ ] snippets/unavailable-variant-notice.liquid

[ ] 2. Modify Existing Files:
   [ ] sections/header.liquid - Add enquiry icon bubble
   [ ] layout/theme.liquid - Include enquiry scripts and sections
   [ ] sections/main-product.liquid - Add grouped products and enquiry
   [ ] snippets/buy-buttons.liquid - Add enquiry button
   [ ] assets/global.js - Integrate enquiry functionality
   [ ] assets/product-form.js - Handle enquiry form submission
   [ ] config/settings_schema.json - Add enquiry settings

[ ] 3. Test Features:
   [ ] Enquiry cart icon appears in header
   [ ] Enquiry drawer opens/closes properly
   [ ] Products can be added to enquiry
   [ ] Grouped products display correctly
   [ ] Custom availability shows properly
   [ ] Enquiry form submission works
    """
    
    print(checklist)

def main():
    # Run analysis
    unique_files, enquiry_refs, grouped_refs, availability_refs = analyze_enquiry_system()
    
    # Generate implementation checklist
    generate_implementation_checklist()
    
    # Save results
    results = {
        'unique_files_to_move': unique_files,
        'files_with_enquiry_refs': list(enquiry_refs.keys()),
        'files_with_grouped_refs': list(grouped_refs.keys()),
        'files_with_availability_refs': list(availability_refs.keys()),
        'total_files_affected': len(set(list(enquiry_refs.keys()) + list(grouped_refs.keys()) + list(availability_refs.keys())))
    }
    
    with open('enquiry_system_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nDetailed results saved to enquiry_system_analysis.json")

if __name__ == "__main__":
    main()