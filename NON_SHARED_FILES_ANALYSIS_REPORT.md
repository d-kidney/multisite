# Non-Shared Files Analysis: What Makes Each Shopify Store Unique

## Executive Summary

After analyzing 680 non-shared files across 6 Shopify stores (298 files were already moved to shared), here's what makes each store unique:

### Key Findings:
- **70 files** exist in ALL stores but with DIFFERENT content (store customizations)
- **69 files** exist in SOME stores only (store-specific features)
- **build4less** is the most feature-rich with 19 unique files
- **building-supplies-online** is the most streamlined with only 1 unique file

---

## 1. Files in ALL Stores but with DIFFERENT Content (70 files)

These files represent the core customizations that differentiate each store while maintaining the same functionality:

### Critical Identity Files (All Different Across Stores):

| File | Purpose | Variations |
|------|---------|------------|
| **`config/settings_data.json`** | Store configuration, branding, theme settings | 6 unique versions (14-17KB each) |
| **`assets/custom.css`** | Store-specific styling and customizations | 6 unique versions (14-34KB) |
| **`assets/base.css`** | Core theme styles with store modifications | 6 unique versions (~98KB each) |
| **`layout/theme.liquid`** | Main template structure | 6 unique versions |
| **`templates/index.json`** | Homepage layout configuration | 6 unique versions |

### Store Branding Differences:

| Store | Logo | Logo Width | Favicon | Custom CSS Size |
|-------|------|------------|---------|-----------------|
| **build4less** | b4l-w-tagline-v3-2.png | 220px | fav_inverted.png | 34KB (largest) |
| **tiles4less** | T4L_New_Logo.png | 180px | T4L_Circle_Logo.png | 31KB |
| **building-supplies-online** | bso-logo-small-154x158.png | 70px | bso-logo-medium-308x315.png | 15KB (smallest) |
| **insulation4less** | I4L_Logo_md.png | 220px | fav_I4L_inverted.png | 32KB |
| **insulation4us** | logo_final.png | 220px | I4US-fav.jpg | 29KB |
| **roofing4us** | Roofing4US_LOGO.png | 220px | I4US-fav.jpg | 29KB |

### Other Significant Different Files:
- **`assets/cart.js`** - 6 different versions (cart functionality variations)
- **`assets/cart-notification.js`** - 4 different versions
- **`assets/component-cart.css`** - 4 different versions
- **`assets/component-mega-menu.css`** - 3 different versions

---

## 2. Files in SOME Stores Only (69 files)

These represent store-specific features and functionality:

### build4less Unique Features (19 unique files):

#### Enquiry System (build4less ONLY):
- `assets/component-enquiry.css` - Enquiry form styling
- `assets/enquiry.js` - Main enquiry functionality (47KB)
- `assets/enquiry-form.js` - Form handling (58KB)
- `assets/enquiry-config.js` - Configuration (3KB)
- `assets/enquiry-checkout-style.css` - Checkout styling (7KB)

#### B2B Context Templates (build4less ONLY):
- `sections/footer-group.context.b2b.json`
- `sections/header-group.context.b2b.json`
- `templates/index.context.b2b.json`

#### Additional build4less Unique Files:
- `assets/search-zindex-fix.js` (0 bytes - empty file)
- Various B2B-specific snippets and sections

### Grouped Product Features (5 stores - MISSING from building-supplies-online):
- `assets/custom-grouped-product.css` - Grouped product styling
- `assets/custom-grouped-product-option-picker.js` - Product option logic (53KB)

### Additional Icons (5 stores - MISSING from building-supplies-online):
- `assets/icon-battery.svg`
- `assets/icon-connection.svg`
- `assets/icon-fast-delivery-truck.svg`
- `assets/icon-leaves.svg`
- `assets/icon-muscle.svg`
- `assets/icon-piggy-bank.svg`
- `assets/icon-shield.svg`
- `assets/icon-tick-circle.svg`
- `assets/icon-tools.svg`
- `assets/icon-warranty.svg`

### Unavailable Product Handling:
- **build4less & tiles4less**: Full unavailable product system
  - `assets/unavailable-product.js`
  - `assets/unavailable-variant-handler.js`
- **Other stores**: Only basic `icon-unavailable.svg`

---

## 3. Store Identity Analysis

### build4less - The Feature-Rich Flagship
- **Most advanced**: 19 unique files, largest custom.css (34KB)
- **Unique features**: Full enquiry system, B2B context, advanced grouped products
- **Target**: B2B customers with complex requirements
- **Branding**: Comprehensive "Build4Less" brand with tagline logo

### tiles4less - The Specialized Store  
- **Moderate customization**: No unique files but different styling
- **Features**: Grouped products, standard icons, unavailable product handling
- **Target**: Tile-specific customers
- **Branding**: Tiles4Less with circular logo, 180px width

### building-supplies-online - The Streamlined Store
- **Most minimal**: Only 1 unique file, smallest custom.css (15KB)
- **Missing features**: No grouped products, no extra icons, no enquiry system
- **Target**: General building supplies, simple shopping experience
- **Branding**: Compact BSO logo (70px), clean design

### insulation4less - The UK Focus
- **Standard features**: Grouped products, full icon set
- **Geographic targeting**: GB and Ireland context templates
- **Branding**: Insulation4Less with inverted favicon

### insulation4us - The US Market
- **Similar to insulation4less** but US-focused
- **Branding**: Different logo, shares favicon with roofing4us

### roofing4us - The Specialized US Store
- **Similar structure to insulation4us**
- **Branding**: Roofing4US logo, shares favicon with insulation4us

---

## 4. Patterns and Consolidation Opportunities

### Nearly Identical Files (Could be Parameterized):

1. **Geographic Variations**: 
   - Many files differ only by market (GB, Ireland, US contexts)
   - Could use dynamic market detection

2. **Icon Sets**:
   - building-supplies-online missing 10+ icons that others have
   - Could standardize icon library

3. **Feature Toggles**:
   - Enquiry system could be feature-flagged rather than build4less-only
   - Grouped products could be enabled/disabled per store

### Store Clustering:
- **Advanced Group**: build4less (most features)
- **Standard Group**: tiles4less, insulation4less, insulation4us, roofing4us
- **Minimal Group**: building-supplies-online (streamlined)

---

## 5. Most Important Store-Specific Files

### Critical for Store Identity:
1. **`config/settings_data.json`** - Must remain unique (logos, branding, configuration)
2. **`assets/custom.css`** - Store-specific styling and branding
3. **Store logos and favicons** - Obviously must remain unique

### Critical for Functionality:
1. **build4less enquiry system** - Major differentiator for B2B customers
2. **Grouped product functionality** - Important for 5/6 stores
3. **Geographic context templates** - Important for international stores

### Could be Consolidated:
1. **Base theme files** (`base.css`, `theme.liquid`) - Mostly identical with minor variations
2. **Icon libraries** - Could standardize across all stores
3. **Cart functionality** - Currently 6 different versions

---

## 6. Recommendations

### Immediate Opportunities:
1. **Standardize icon library** across all stores
2. **Consolidate cart functionality** with feature flags
3. **Parameterize geographic templates** instead of separate context files

### Architecture Improvements:
1. **Feature flag system** for enquiry, grouped products, etc.
2. **Theme inheritance** with store-specific overrides
3. **Centralized configuration** for common theme settings

### Maintain as Unique:
1. Store branding (logos, favicons, brand colors)
2. Store-specific business logic (build4less enquiry system)
3. Market-specific content and legal requirements