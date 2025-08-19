# Shopify Multisite Theme Differences Analysis Report

## Executive Summary

This report analyzes the differences between six Shopify store themes in a multisite architecture, identifying unique features and opportunities for increased code sharing. Currently, 298 files (~44%) are shared across themes, with significant variations in JavaScript functionality, Liquid templates, and business logic implementations.

### Key Findings
- **Build4Less** has the most advanced B2B features with 19 unique files
- **Insulation4Us/Roofing4Us** have unique auto-shipping protection systems
- **Tiles4Less** includes tile-specific calculators for flooring products
- **Building Supplies Online** has the simplest implementation with basic e-commerce features
- Potential to increase shared code from 44% to ~65% through strategic refactoring

## Table of Contents
1. [Theme Overview](#theme-overview)
2. [JavaScript Differences Analysis](#javascript-differences-analysis)
3. [Liquid Template Differences](#liquid-template-differences)
4. [Unique Features by Theme](#unique-features-by-theme)
5. [Code Sharing Opportunities](#code-sharing-opportunities)
6. [Implementation Recommendations](#implementation-recommendations)
7. [Technical Debt Assessment](#technical-debt-assessment)

## Theme Overview

### Current Architecture
```
/themes/
├── build4less/          (B2B focused, most features)
├── tiles4less/          (B2B + tile calculations)
├── building-supplies-online/ (B2C, simplified)
├── insulation4less/     (Standard + partial shipping protection)
├── insulation4us/       (Full shipping protection)
└── roofing4us/          (Full shipping protection)

/shared/                 (298 shared files)
```

### File Size Comparison

| File | Build4Less | Tiles4Less | BSO | Insulation4Less | Insulation4Us | Roofing4Us |
|------|------------|------------|-----|-----------------|---------------|------------|
| cart.js | 16,931 | 16,929 | **10,622** | 16,812 | **24,405** | **24,440** |
| global.js | 60,743 | 61,164 | 53,571 | 60,809 | 58,134 | 58,134 |
| product-info.js | 18,101 | 18,342 | 16,700 | 18,101 | 18,101 | 18,101 |
| custom.css | 33,941 | 30,624 | **14,553** | 31,902 | 28,955 | 29,045 |

## JavaScript Differences Analysis

### 1. Cart.js Implementation Variations

#### Building Supplies Online (Simplified Version)
```javascript
// BSO - Basic cart without validation (10,622 bytes)
class CartItems extends HTMLElement {
  constructor() {
    super();
    // Simple quantity updates
    this.addEventListener('change', debounce((event) => {
      this.onChange(event);
    }, ON_CHANGE_DEBOUNCE_TIMER));
  }
  
  onChange(evt) {
    // Basic cart update without radio validation
    this.updateQuantity(
      line, 
      quantity, 
      document.activeElement.getAttribute('name'),
      evt.target.dataset.index
    );
  }
}
```

#### Build4Less/Tiles4Less (Standard B2B Version)
```javascript
// Build4Less - Includes delivery validation (16,931 bytes)
class CartItems extends HTMLElement {
  constructor() {
    super();
    // Advanced validation for B2B requirements
    this.cartAcceptAlertRadioButtons = document.querySelectorAll('input[name="attributes[accept_alt]"]');
    this.cartOffloadConfirmationRadioButtons = document.querySelectorAll('input[name="attributes[offload_confirmation]"]');
    
    // Prevent scroll on number inputs
    document.querySelectorAll('input[type=number]').forEach(function(input) {
      input.addEventListener('wheel', function(e) {
        e.preventDefault();
      });
    });
  }
  
  onChange(evt) {
    // Validate B2B requirements before updating
    const radioValidation = this.validateRadioButtons();
    if (!radioValidation.isValid) {
      this.showRadioAlert(radioValidation.missingSelection);
      evt.preventDefault();
      return;
    }
    
    this.updateQuantity(/* ... */);
  }
  
  validateRadioButtons() {
    // Complex validation for accept alternatives and offload confirmation
    const acceptAltChecked = [...this.cartAcceptAlertRadioButtons].some(radio => radio.checked);
    const offloadChecked = [...this.cartOffloadConfirmationRadioButtons].some(radio => radio.checked);
    
    return {
      isValid: acceptAltChecked && offloadChecked,
      missingSelection: !acceptAltChecked ? 'accept_alt' : 'offload_confirmation'
    };
  }
}
```

#### Insulation4Us/Roofing4Us (Auto Shipping Protection)
```javascript
// Insulation4Us - Complete shipping protection system (24,405 bytes)
class CartItems extends HTMLElement {
  constructor() {
    super();
    
    // Shipping protection configuration
    this.shippingProtectionVariants = [
      39919251030071, 39919251062839, 39919251095607, // ... 100+ variants
    ];
    
    this.shippingProtectionPrices = [
      0.15, 0.18, 0.21, 0.24, 0.27, // ... matching price array
    ];
    
    // Auto-add shipping protection on checkout
    this.initShippingProtection();
  }
  
  initShippingProtection() {
    // Check if ShopPay redirect via cookie
    const shopPayRedirect = this.getCookie('shopPayRedirect');
    
    if (shopPayRedirect === 'true') {
      this.addShippingProtection();
      this.setCookie('shopPayRedirect', 'false', 1);
    }
  }
  
  addShippingProtection() {
    // Calculate 3% of cart total
    const cartTotal = parseFloat(document.querySelector('[data-cart-total]').dataset.cartTotal);
    const protectionAmount = cartTotal * 0.03;
    
    // Find matching variant based on price
    const variantIndex = this.findClosestPriceIndex(protectionAmount);
    const variantId = this.shippingProtectionVariants[variantIndex];
    
    // Add via AJAX
    jQuery.ajax({
      type: 'POST',
      url: '/cart/add.js',
      data: {
        id: variantId,
        quantity: 1,
        properties: {
          '_auto_added': 'true',
          '_protection_percentage': '3%'
        }
      },
      dataType: 'json',
      success: function() {
        window.location.href = '/checkout';
      }
    });
  }
  
  findClosestPriceIndex(targetPrice) {
    // Binary search for closest price match
    return this.shippingProtectionPrices.reduce((prev, curr, index) => {
      return Math.abs(curr - targetPrice) < Math.abs(this.shippingProtectionPrices[prev] - targetPrice) 
        ? index : prev;
    }, 0);
  }
}
```

### 2. Product-Info.js Variations

#### Tiles4Less (Tile Calculator Integration)
```javascript
// Tiles4Less - Includes tile quantity computation
class ProductInfo extends HTMLElement {
  constructor() {
    super();
    this.initializeTileCalculator();
  }
  
  onVariantChange() {
    this.updateOptions();
    this.updateMasterId();
    this.updateMedia();
    
    // Tile-specific calculation
    if (this.dataset.productType === 'Tiles' || this.dataset.productType === 'Flooring') {
      setTimeout(() => {
        this.computeTileQuantity(
          '.cart__qty.quantity-box .quantity-block .common_field_label div',
          '.cart__qty.quantity-box .sqm-qty-block .sqm-user-input-block .common_field_label div'
        );
      }, 0);
    }
  }
  
  computeTileQuantity(qtySelector, sqmSelector) {
    const qtyElement = document.querySelector(qtySelector);
    const sqmElement = document.querySelector(sqmSelector);
    
    if (qtyElement && sqmElement) {
      const tilesPerSqm = parseFloat(this.currentVariant.metafields?.tiles_per_sqm || 1);
      const quantity = parseInt(qtyElement.textContent);
      const sqmCoverage = (quantity / tilesPerSqm).toFixed(2);
      
      sqmElement.textContent = `${sqmCoverage} m²`;
    }
  }
}
```

#### Building Supplies Online (Simplified Product Handling)
```javascript
// BSO - Basic product form without complex re-initialization
class ProductInfo extends HTMLElement {
  onVariantChange() {
    this.updateOptions();
    this.updateMasterId();
    this.updateMedia();
    
    // Simple availability update
    this.updatePickupAvailability();
    
    // No complex form re-initialization
    if (!this.currentVariant) {
      this.setUnavailable();
    } else {
      this.updateURL();
      this.updateVariantInput();
      this.renderProductInfo();
    }
  }
  
  updatePickupAvailability() {
    // Synchronous update without error handling
    const pickupElement = document.querySelector('[data-pickup-availability]');
    if (pickupElement) {
      pickupElement.fetchAvailability(this.currentVariant.id);
    }
  }
}
```

## Liquid Template Differences

### 1. Main Product Section Variations

#### Build4Less (sections/main-product.liquid)
```liquid
<!-- Build4Less - Advanced B2B features -->
<section class="product" data-product-id="{{ product.id }}">
  <!-- Reviews.io integration -->
  <script src="//widget.reviews.io/modern-widgets/nuggets.js"></script>
  
  <!-- H1 with anchor for SEO -->
  <h1 id="h1-anchor" class="product__title">
    {{ product.title | escape }}
  </h1>
  
  <!-- Advanced availability checking -->
  {%- if product.metafields.custom.availability_status == 'not_for_sale' -%}
    {%- render 'unavailable-product-notice', product: product -%}
  {%- elsif product.metafields.custom.call_to_enquire == true -%}
    {%- render 'enquiry-form', product: product, type: 'b2b' -%}
  {%- else -%}
    <!-- Standard product form -->
  {%- endif -%}
  
  <!-- B2B specific features -->
  {%- if b2b_customer -%}
    {%- render 'product-key-selling-points', product: product -%}
    {%- render 'delivery-calculation', product: product -%}
  {%- endif -%}
</section>
```

#### Building Supplies Online (sections/main-product.liquid)
```liquid
<!-- BSO - Simplified with hardcoded contact info -->
<section class="product">
  <h1 class="product__title">{{ product.title | escape }}</h1>
  
  {%- if product.metafields.custom.call_for_price == true -%}
    <div class="call-for-price">
      <p>Please call for pricing</p>
      <a href="tel:020-3936-2839">020-3936-2839</a>
      <a href="mailto:sales@i4lgroup.co.uk">sales@i4lgroup.co.uk</a>
    </div>
  {%- else -%}
    <!-- Standard product form -->
  {%- endif -%}
  
  <!-- Supply chain messaging -->
  <div class="supply-notice">
    <p>Due to current supply chain conditions, availability may vary.</p>
  </div>
</section>
```

#### Tiles4Less (sections/main-product.liquid)
```liquid
<!-- Tiles4Less - Enhanced variant tracking -->
<section class="product" 
         data-all-variants-unavailable="{{ product.available }}"
         data-current-variant-status="{{ current_variant.inventory_policy }}">
  
  <h1 class="product__title">{{ product.title | escape }}</h1>
  
  <!-- Tile calculator integration -->
  {%- if product.type == 'Tiles' or product.type == 'Flooring' -%}
    <div class="tile-calculator-wrapper">
      {%- render 'tile-quantity-calculator', product: product -%}
    </div>
  {%- endif -%}
  
  <!-- Different status checking -->
  {%- if product.metafields.custom.status == 'we dont sell' -%}
    {%- render 'product-not-available' -%}
  {%- else -%}
    {%- render 'product-form', product: product -%}
  {%- endif -%}
</section>
```

### 2. Buy Buttons Implementation

#### Build4Less (snippets/buy-buttons.liquid)
```liquid
<!-- Build4Less - Complex enquiry system -->
{%- liquid
  assign call_to_enquire = product.metafields.custom.call_to_enquire
  assign variant_status = current_variant.metafields.custom.status
  
  # Multiple enquiry triggers
  if call_to_enquire == true 
    assign show_enquiry = true
    assign enquiry_type = 'standard'
  elsif variant_status == 'poa'
    assign show_enquiry = true
    assign enquiry_type = 'price_on_application'
  elsif variant_status == 'custom_product'
    assign show_enquiry = true
    assign enquiry_type = 'custom'
  elsif variant_status == 'cte'
    assign show_enquiry = true
    assign enquiry_type = 'call_to_enquire'
  elsif variant_status == 'no_restock_date'
    assign show_enquiry = true
    assign enquiry_type = 'out_of_stock'
  endif
  
  # Grouped product handling
  if product.metafields.custom.grouped_product_parent
    assign parent_product = all_products[product.metafields.custom.grouped_product_parent]
    if parent_product.available == false
      assign show_alternative = true
    endif
  endif
-%}

{%- if show_enquiry -%}
  <button type="button" 
          class="product-form__submit button button--full-width button--secondary"
          data-enquiry-trigger
          data-enquiry-type="{{ enquiry_type }}">
    {%- case enquiry_type -%}
      {%- when 'price_on_application' -%}
        Price on Application
      {%- when 'custom' -%}
        Configure Custom Product
      {%- when 'out_of_stock' -%}
        Enquire About Availability
      {%- else -%}
        Enquire Now
    {%- endcase -%}
  </button>
{%- elsif show_alternative -%}
  {%- render 'alternative-product-suggestion', product: parent_product -%}
{%- else -%}
  <!-- Standard add to cart -->
  <button type="submit" name="add" class="product-form__submit button button--full-width">
    Add to Cart
  </button>
{%- endif -%}
```

### 3. Unique Snippet Files

#### Build4Less Exclusive Snippets

**b2b-header-mega-menu.liquid**
```liquid
<!-- B2B Mega Menu with collection filtering -->
<nav class="b2b-mega-menu">
  {%- for link in section.settings.menu.links -%}
    {%- if link.links != blank -%}
      <div class="mega-menu__column">
        <h3>{{ link.title }}</h3>
        <ul>
          {%- for child_link in link.links -%}
            {%- # Filter collections based on B2B customer tags -%}
            {%- if customer.b2b? -%}
              {%- assign show_collection = false -%}
              {%- for tag in customer.tags -%}
                {%- if child_link.url contains tag -%}
                  {%- assign show_collection = true -%}
                  {%- break -%}
                {%- endif -%}
              {%- endfor -%}
              
              {%- if show_collection -%}
                <li><a href="{{ child_link.url }}">{{ child_link.title }}</a></li>
              {%- endif -%}
            {%- else -%}
              <li><a href="{{ child_link.url }}">{{ child_link.title }}</a></li>
            {%- endif -%}
          {%- endfor -%}
        </ul>
      </div>
    {%- endif -%}
  {%- endfor -%}
</nav>
```

**delivery-calculation.liquid**
```liquid
<!-- Advanced delivery calculation with vendor rules -->
{%- liquid
  assign delivery_zone = customer.metafields.custom.delivery_zone | default: 'standard'
  assign product_weight = product.variants.first.weight | times: 0.001
  assign vendor_code = product.vendor | handleize
  
  # Vendor-specific delivery rules
  case vendor_code
    when 'heavy-materials'
      assign base_delivery = 45.00
      assign per_kg_rate = 0.50
    when 'standard-supplies'
      assign base_delivery = 15.00
      assign per_kg_rate = 0.25
    else
      assign base_delivery = 25.00
      assign per_kg_rate = 0.35
  endcase
  
  # Zone multipliers
  case delivery_zone
    when 'remote'
      assign zone_multiplier = 1.5
    when 'highland'
      assign zone_multiplier = 2.0
    else
      assign zone_multiplier = 1.0
  endcase
  
  assign delivery_cost = base_delivery | plus: product_weight | times: per_kg_rate | times: zone_multiplier
-%}

<div class="delivery-calculation" data-vendor="{{ vendor_code }}" data-zone="{{ delivery_zone }}">
  <h4>Estimated Delivery Cost</h4>
  <p class="delivery-cost">
    {{ delivery_cost | money }}
  </p>
  <small>
    * Based on {{ product_weight }}kg to {{ delivery_zone | capitalize }} zone
  </small>
</div>
```

## Unique Features by Theme

### Build4Less (Most Comprehensive)

| Feature | Description | Implementation |
|---------|-------------|----------------|
| B2B Mega Menu | Dynamic menu filtering based on customer tags | `b2b-header-mega-menu.liquid` |
| Delivery Calculation | Complex vendor and zone-based pricing | `delivery-calculation.liquid` |
| Multi-tier Enquiry | 5+ different enquiry types with custom flows | `buy-buttons.liquid` |
| Product Key Points | USP highlighting for B2B customers | `product-key-selling-points.liquid` |
| Accept Alternatives | Customer consent for product substitutions | `cart-accept-alt.liquid` |
| Offload Confirmation | Delivery handling agreements | `cart-offloading-confirmation.liquid` |
| Clerk Analytics | Advanced tracking integration | `clerk-tracking.liquid` |
| Reviews.io | Product review system | External script integration |

### Tiles4Less

| Feature | Description | Implementation |
|---------|-------------|----------------|
| Tile Calculator | Square meter coverage calculation | `computeTileQuantity()` in `product-info.js` |
| Enhanced Variants | Advanced availability tracking | Data attributes in templates |
| Most B2B Features | Inherited from Build4Less | Shared snippets |

### Building Supplies Online

| Feature | Description | Implementation |
|---------|-------------|----------------|
| Simplified Cart | No validation systems | Reduced `cart.js` (10KB) |
| Hardcoded Contact | Direct phone/email in templates | Inline in templates |
| Group Product Styling | Visual indicators for variants | CSS class additions |
| Basic E-commerce | Standard Shopify features only | Minimal customization |

### Insulation4Us & Roofing4Us

| Feature | Description | Implementation |
|---------|-------------|----------------|
| Auto Shipping Protection | 3% of cart value protection | `cart.js` (24KB) |
| 100+ Protection Variants | Granular price matching | Arrays in JavaScript |
| ShopPay Integration | Cookie-based redirect detection | Cookie management |
| jQuery Cart Manipulation | AJAX-based cart updates | Legacy jQuery code |

## Code Sharing Opportunities

### 1. Feature Flag System Implementation

Create a unified configuration system in `settings_schema.json`:

```json
{
  "name": "Theme Features",
  "settings": [
    {
      "type": "checkbox",
      "id": "enable_b2b_features",
      "label": "Enable B2B Features",
      "default": false
    },
    {
      "type": "checkbox", 
      "id": "enable_delivery_calculation",
      "label": "Enable Delivery Calculation",
      "default": false
    },
    {
      "type": "checkbox",
      "id": "enable_shipping_protection",
      "label": "Enable Auto Shipping Protection",
      "default": false
    },
    {
      "type": "checkbox",
      "id": "enable_tile_calculator",
      "label": "Enable Tile Calculator",
      "default": false
    },
    {
      "type": "select",
      "id": "enquiry_system_type",
      "label": "Enquiry System Type",
      "options": [
        {"value": "none", "label": "None"},
        {"value": "basic", "label": "Basic (Call for Price)"},
        {"value": "advanced", "label": "Advanced (Multi-tier)"}
      ],
      "default": "none"
    }
  ]
}
```

### 2. Unified Cart.js Architecture

```javascript
// shared/assets/cart-base.js
class CartBase extends HTMLElement {
  constructor() {
    super();
    this.initializeFeatures();
  }
  
  initializeFeatures() {
    const features = window.themeFeatures || {};
    
    if (features.enableValidation) {
      this.initializeValidation();
    }
    
    if (features.enableShippingProtection) {
      this.initializeShippingProtection();
    }
    
    if (features.enableFastCheckout) {
      this.initializeFastCheckout();
    }
  }
  
  // Core cart functionality
  updateQuantity(line, quantity) {
    // Shared implementation
  }
}

// theme-specific/assets/cart.js
class CartItems extends CartBase {
  constructor() {
    super();
    
    // Theme-specific configuration
    window.themeFeatures = {
      enableValidation: true, // Build4Less, Tiles4Less
      enableShippingProtection: false, // Insulation4Us, Roofing4Us only
      enableFastCheckout: true,
      shippingProtectionRate: 0.03
    };
  }
}

customElements.define('cart-items', CartItems);
```

### 3. Modular Enquiry System

```liquid
<!-- shared/snippets/enquiry-system.liquid -->
{%- liquid
  # Load configuration from settings
  assign enquiry_config = section.settings.enquiry_system_config | default: shop.metafields.theme.enquiry_config
  
  # Determine enquiry type
  assign show_enquiry = false
  assign enquiry_type = nil
  
  if enquiry_config.enabled
    # Check various conditions
    for trigger in enquiry_config.triggers
      case trigger.field
        when 'metafield'
          if product.metafields[trigger.namespace][trigger.key] == trigger.value
            assign show_enquiry = true
            assign enquiry_type = trigger.type
            break
          endif
        when 'availability'
          unless product.available
            assign show_enquiry = true
            assign enquiry_type = 'out_of_stock'
            break
          endunless
      endcase
    endfor
  endif
-%}

{%- if show_enquiry -%}
  {%- render 'enquiry-button', 
      type: enquiry_type,
      product: product,
      labels: enquiry_config.labels,
      contact: enquiry_config.contact_info -%}
{%- else -%}
  {%- render 'standard-buy-button', product: product -%}
{%- endif -%}
```

### 4. Shared Component Library Structure

```
/shared/
├── assets/
│   ├── base/
│   │   ├── cart-base.js
│   │   ├── product-base.js
│   │   └── global-base.js
│   ├── modules/
│   │   ├── shipping-protection.js
│   │   ├── delivery-calculator.js
│   │   ├── tile-calculator.js
│   │   └── b2b-features.js
│   └── styles/
│       ├── base.css
│       └── components.css
├── snippets/
│   ├── core/
│   │   ├── product-card.liquid
│   │   ├── cart-item.liquid
│   │   └── buy-buttons.liquid
│   └── features/
│       ├── enquiry-system.liquid
│       ├── delivery-calc.liquid
│       └── shipping-protection.liquid
└── config/
    └── features.json
```

## Implementation Recommendations

### Phase 1: Quick Wins (1-2 weeks)
1. **Standardize Code Formatting**
   - Align quote styles across all themes
   - Consistent indentation and spacing
   - Remove commented code and unused functions

2. **Extract Configuration**
   - Move hardcoded values to settings
   - Create shared configuration files
   - Standardize metafield usage

3. **Unify Simple Components**
   - Merge identical CSS files
   - Combine global.js implementations
   - Share utility functions

### Phase 2: Feature Modularization (2-4 weeks)
1. **Create Feature Toggle System**
   - Implement settings schema changes
   - Add feature detection in JavaScript
   - Create conditional rendering in Liquid

2. **Build Shared Modules**
   - Extract shipping protection module
   - Create delivery calculation module
   - Separate tile calculator functionality

3. **Standardize Enquiry System**
   - Create configurable enquiry flow
   - Unify contact information handling
   - Implement flexible status checking

### Phase 3: Architecture Refactor (4-6 weeks)
1. **Implement Base Classes**
   - Create CartBase, ProductBase classes
   - Use inheritance for theme-specific features
   - Standardize event handling

2. **Create Component Library**
   - Build shared snippet library
   - Implement consistent APIs
   - Document component interfaces

3. **Optimize Build Process**
   - Set up automated testing
   - Implement feature flag validation
   - Create deployment verification

## Technical Debt Assessment

### High Priority Issues
1. **jQuery Dependency** in shipping protection (Insulation4Us/Roofing4Us)
   - Migrate to native fetch API
   - Remove jQuery library dependency
   - Modernize AJAX calls

2. **Hardcoded Values** in BSO theme
   - Move contact info to settings
   - Create configurable messages
   - Implement dynamic pricing

3. **Code Duplication** across themes
   - 70+ files with different content but similar functionality
   - Repeated validation logic
   - Duplicate utility functions

### Medium Priority Issues
1. **Inconsistent Error Handling**
   - Some themes have try-catch blocks, others don't
   - No unified error reporting
   - Missing user feedback for failures

2. **Performance Optimization**
   - Large JavaScript files (24KB+ for cart.js)
   - Synchronous operations that could be async
   - Unnecessary DOM queries

3. **Accessibility Concerns**
   - Missing ARIA labels in dynamic content
   - No keyboard navigation for custom components
   - Insufficient focus management

### Low Priority Issues
1. **Code Style Inconsistencies**
   - Mixed quote styles
   - Variable naming conventions
   - Comment formatting

2. **Missing Documentation**
   - No inline code documentation
   - Missing README files
   - No component usage examples

## Cost-Benefit Analysis

### Current State
- **Maintenance Cost**: High - 6 separate codebases
- **Development Time**: 6x for feature rollout
- **Bug Risk**: High - fixes needed in multiple places
- **Testing Effort**: 6x manual testing required

### After Implementation
- **Shared Code**: ~65% (up from 44%)
- **Development Time**: 2-3x (with feature flags)
- **Bug Risk**: Medium - centralized fixes
- **Testing Effort**: 2x (shared + theme-specific)

### ROI Calculation
- **Time Saved per Feature**: ~60% reduction
- **Bug Fix Time**: ~70% reduction
- **Onboarding Time**: ~50% reduction
- **Break-even Point**: ~3-4 months

## Conclusion

The analysis reveals significant opportunities for code sharing across the six Shopify themes. While each theme has evolved unique features for specific business requirements, many of these differences can be reconciled through:

1. **Feature flag system** for toggling functionality
2. **Modular architecture** with shared base components
3. **Configuration-driven** behavior instead of code duplication
4. **Standardized APIs** for common operations

Implementing these recommendations would increase code sharing from 44% to approximately 65%, reducing maintenance overhead and improving development velocity while preserving the unique business logic requirements of each store.

### Next Steps
1. Review and approve the proposed architecture
2. Prioritize implementation phases based on business needs
3. Establish feature flag governance process
4. Create migration timeline for each theme
5. Set up monitoring for shared component usage

### Success Metrics
- Reduction in deployment time per feature
- Decrease in theme-specific bugs
- Improved developer productivity metrics
- Reduced code review time
- Increased test coverage percentage