# Feature Implementation Guide: Build4Less to All Sites

## Overview
This guide provides detailed instructions for implementing three key features from the Build4Less theme across all other Shopify sites. All shared files have already been copied to the `/multisite/shared/` folder.

## Table of Contents
1. [Feature 1: Enquiry System](#feature-1-enquiry-system-with-enabledisable-setting)
2. [Feature 2: Product Unavailability Handling](#feature-2-product-unavailability-handling)
3. [Feature 3: Custom Grouped Product](#feature-3-custom-grouped-product)
4. [Required Metafields](#required-metafields-configuration)
5. [Testing Checklist](#testing-checklist)
6. [Deployment Strategy](#deployment-strategy)

---

## Feature 1: Enquiry System (with Enable/Disable Setting)

### 1.1 Theme Settings Configuration
**File:** `config/settings_schema.json`  
**Location:** Add this section before the closing bracket of the JSON array  
**Line:** Approximately line 600-650 (varies by store)

```json
{
  "name": "Enquiry System",
  "settings": [
    {
      "type": "checkbox",
      "id": "enable_enquiry_system",
      "label": "Enable Enquiry System",
      "default": false,
      "info": "Enable the quote/enquiry system for products marked as POA or custom"
    },
    {
      "type": "text",
      "id": "enquiry_button_text",
      "label": "Enquiry Button Text",
      "default": "Get a Quote",
      "info": "Text shown on enquiry buttons"
    }
  ]
}
```

### 1.2 Theme Layout Integration
**File:** `layout/theme.liquid`  
**Location:** Add before `</body>` tag  
**Line:** Approximately line 350-400

```liquid
{%- comment -%} Enquiry System Integration {%- endcomment -%}
{% if settings.enable_enquiry_system %}
  {{ 'component-enquiry.css' | asset_url | stylesheet_tag }}
  {{ 'enquiry-checkout-style.css' | asset_url | stylesheet_tag }}
  <script src="{{ 'enquiry-config.js' | asset_url }}" defer="defer"></script>
  <script src="{{ 'enquiry.js' | asset_url }}" defer="defer"></script>
  <script src="{{ 'enquiry-form.js' | asset_url }}" defer="defer"></script>
  
  {% render 'enquiry-drawer' %}
  {% render 'enquiry-notification' %}
  
  <script>
    // Mock checkout object to prevent pixel errors
    if (!window.Shopify) window.Shopify = {};
    if (!window.Shopify.checkout) {
      window.Shopify.checkout = {
        email: '',
        billing_address: {},
        shipping_address: {}
      };
    }
  </script>
{% endif %}
```

### 1.3 Header Integration
**File:** `sections/header.liquid`  
**Location:** After cart-icon-bubble render  
**Line:** Search for `cart-icon-bubble` (usually around line 450-500)

```liquid
{%- comment -%} Enquiry Icon in Header {%- endcomment -%}
{% if settings.enable_enquiry_system %}
  {% render 'enquiry-icon-bubble' %}
{% endif %}
```

### 1.4 Product Availability Integration
**File:** `snippets/buy-buttons.liquid`  
**Location:** After the product form closing tag  
**Line:** Approximately line 150

```liquid
{%- comment -%} Enquiry System for POA Products {%- endcomment -%}
{% if settings.enable_enquiry_system %}
  {% assign product_status = product.metafields.custom.product_availability_status %}
  {% if product_status == 'poa' or product_status == 'custom' %}
    <div class="product-form__buttons">
      <a href="/pages/enquiry-form" class="button button--full-width button--primary enquiry-link">
        {{ settings.enquiry_button_text | default: 'Get a Quote' }}
      </a>
    </div>
  {% endif %}
{% endif %}
```

### 1.5 Custom Product Availability Snippet
**File:** `snippets/custom-product-availability.liquid` (Create new if doesn't exist)  
**Full file content:**

```liquid
{%- comment -%}
  Renders product availability status with enquiry integration
  
  Accepts:
  - product: {Object} Product Liquid object (required)
  - product_form_id: {String} Form ID for product form
  - section_id: {String} Section ID
  
  Usage:
  {% render 'custom-product-availability', product: product, product_form_id: product_form_id, section_id: section.id %}
{%- endcomment -%}

{% if settings.enable_enquiry_system %}
  {% assign product_status = product.metafields.custom.product_availability_status %}
  
  {% case product_status %}
    {% when 'poa' %}
      <div class="product-availability product-availability--poa">
        <span class="availability-label">Price on Application</span>
        <add-to-enquiry-button 
          data-product-id="{{ product.id }}"
          data-variant-id="{{ product.selected_or_first_available_variant.id }}"
          data-product-title="{{ product.title | escape }}"
          data-product-handle="{{ product.handle }}"
          class="button button--full-width button--primary">
          <span>Add to Enquiry</span>
        </add-to-enquiry-button>
      </div>
      
    {% when 'custom' %}
      <div class="product-availability product-availability--custom">
        <span class="availability-label">Custom Product - Quote Required</span>
        <add-to-enquiry-button 
          data-product-id="{{ product.id }}"
          data-variant-id="{{ product.selected_or_first_available_variant.id }}"
          data-product-title="{{ product.title | escape }}"
          data-product-handle="{{ product.handle }}"
          class="button button--full-width button--primary">
          <span>Request Quote</span>
        </add-to-enquiry-button>
      </div>
      
    {% else %}
      {% render 'buy-buttons', 
        product: product, 
        product_form_id: product_form_id, 
        section_id: section_id, 
        show_pickup_availability: true 
      %}
  {% endcase %}
{% else %}
  {% render 'buy-buttons', 
    product: product, 
    product_form_id: product_form_id, 
    section_id: section_id, 
    show_pickup_availability: true 
  %}
{% endif %}
```

### 1.6 Main Product Section Update
**File:** `sections/main-product.liquid`  
**Location:** Replace buy-buttons render  
**Line:** Search for `render 'buy-buttons'` (usually around line 280-320)

```liquid
{%- comment -%} Product Availability and Buy Buttons {%- endcomment -%}
{% if settings.enable_enquiry_system and product.metafields.custom.product_availability_status != blank %}
  {% render 'custom-product-availability', 
    product: product, 
    product_form_id: product_form_id, 
    section_id: section.id 
  %}
{% else %}
  {% render 'buy-buttons', 
    product: product, 
    product_form_id: product_form_id, 
    section_id: section.id, 
    show_pickup_availability: true 
  %}
{% endif %}
```

---

## Feature 2: Product Unavailability Handling

### 2.1 Main Product Section - Unavailable Product Notice
**File:** `sections/main-product.liquid`  
**Location:** After product media gallery  
**Line:** Approximately line 50-60

```liquid
{%- comment -%} Unavailable Product Handling {%- endcomment -%}
{% assign product_status = product.metafields.custom.product_availability_status %}
{% if product_status == 'discontinued' or product_status == 'not_for_sale' %}
  <div class="product product--unavailable" id="original-product-display">
    {% render 'unavailable-product-notice', product: product %}
  </div>
  
  <script src="{{ 'unavailable-product.js' | asset_url }}" defer="defer"></script>
  
  <style>
    .product--unavailable { display: none; }
    body.showing-archived .product--unavailable { display: block; }
    body.showing-archived #alternative-product-container,
    body.showing-archived #recommended-products-container { display: none !important; }
    body.showing-alternative .product--unavailable { display: none; }
  </style>
{% endif %}
```

### 2.2 Product Info Attributes
**File:** `sections/main-product.liquid`  
**Location:** In the product-info element  
**Line:** Search for `<product-info` (around line 180-200)

Add these attributes to the `<product-info` element:
```liquid
data-product-id="{{ product.id }}"
data-all-variants-unavailable="{% if product_status == 'discontinued' or product_status == 'not_for_sale' %}true{% else %}false{% endif %}"
data-current-variant-status="{{ product.selected_or_first_available_variant.metafields.custom.variant_availability_status }}"
```

### 2.3 Variant Picker Integration
**File:** `snippets/product-variant-picker.liquid`  
**Location:** In the variant option loop  
**Line:** Approximately line 30-40

Add to each variant option input:
```liquid
{% assign variant_status = variant.metafields.custom.variant_availability_status %}
data-variant-status="{{ variant_status }}"
{% if variant_status == 'discontinued' or variant_status == 'not_for_sale' %}
  data-variant-unavailable="true"
{% endif %}
```

### 2.4 Variant Unavailability Notice
**File:** `snippets/product-variant-picker.liquid`  
**Location:** Before closing of snippet  
**Line:** At the end of file

```liquid
{%- comment -%} Variant Unavailability Handling {%- endcomment -%}
{% assign has_unavailable_variants = false %}
{% for variant in product.variants %}
  {% assign variant_status = variant.metafields.custom.variant_availability_status %}
  {% if variant_status == 'discontinued' or variant_status == 'not_for_sale' %}
    {% assign has_unavailable_variants = true %}
    {% break %}
  {% endif %}
{% endfor %}

{% if has_unavailable_variants %}
  <div class="product-form__input" data-variant-notice style="display: none;">
    {% render 'unavailable-variant-notice' %}
  </div>
  
  {%- comment -%} Variant metafields data for JavaScript {%- endcomment -%}
  <script type="application/json" data-variant-metafields>
    {
      {% for variant in product.variants %}
        "{{ variant.id }}": {
          "status": "{{ variant.metafields.custom.variant_availability_status }}",
          "hasAlternatives": {% if variant.metafields.custom.alternative_variant %}true{% else %}false{% endif %}
        }{% unless forloop.last %},{% endunless %}
      {% endfor %}
    }
  </script>
  
  <script src="{{ 'unavailable-variant-handler.js' | asset_url }}" defer="defer"></script>
{% endif %}
```

---

## Feature 3: Custom Grouped Product

### 3.1 Main Product Section - Variant Picker Replacement
**File:** `sections/main-product.liquid`  
**Location:** Replace variant picker render  
**Line:** Search for `render 'product-variant-picker'` (around line 250-270)

```liquid
{%- comment -%} Product Options: Grouped or Standard {%- endcomment -%}
{% if product.metafields.custom.custom_grouped_product %}
  {% render 'custom-grouped-product-option-picker', 
    product: product, 
    section: section,
    block: block,
    product_form_id: product_form_id
  %}
  {{ 'custom-grouped-product.css' | asset_url | stylesheet_tag }}
{% else %}
  {% render 'product-variant-picker', 
    product: product, 
    block: block, 
    product_form_id: product_form_id, 
    update_url: false, 
    hide_sold_out_variants: block.settings.hide_sold_out_variants 
  %}
{% endif %}
```

### 3.2 Product Pricing Integration
**File:** `sections/main-product.liquid`  
**Location:** After price render  
**Line:** Search for `render 'price'` (around line 200-220)

```liquid
{%- comment -%} Custom Grouped Product Pricing {%- endcomment -%}
{% if product.metafields.custom.custom_grouped_product %}
  {% render 'custom-grouped-product-pricing', product: product, section_id: section.id %}
{% endif %}
```

### 3.3 Product Form Modifications
**File:** `sections/main-product.liquid`  
**Location:** In the product-form element  
**Line:** Search for `<product-form` (around line 270-290)

Add class to product-form:
```liquid
<product-form class="product-form{% if product.metafields.custom.custom_grouped_product %} grouped-product-form{% endif %}"
```

---

## Required Metafields Configuration

### Product Metafields
Create these in **Settings > Custom data > Products**:

| Namespace.Key | Type | Description | Possible Values |
|--------------|------|-------------|-----------------|
| `custom.product_availability_status` | Single line text | Product availability status | `discontinued`, `not_for_sale`, `poa`, `custom`, or empty |
| `custom.alternative_product` | Product reference | Alternative product suggestion | Product reference |
| `custom.custom_grouped_product` | JSON | Grouped product configuration | JSON structure |
| `custom.option1_name` | Single line text | First option name | e.g., "Size", "Color" |
| `custom.option2_name` | Single line text | Second option name | e.g., "Material", "Style" |
| `custom.option3_name` | Single line text | Third option name | e.g., "Finish", "Pattern" |
| `custom.option1_value` | Single line text | First option value | Specific value |
| `custom.option2_value` | Single line text | Second option value | Specific value |
| `custom.option3_value` | Single line text | Third option value | Specific value |

### Variant Metafields
Create these in **Settings > Custom data > Variants**:

| Namespace.Key | Type | Description | Possible Values |
|--------------|------|-------------|-----------------|
| `custom.variant_availability_status` | Single line text | Variant availability status | `discontinued`, `not_for_sale`, `no_restock_date`, or empty |
| `custom.alternative_variant` | Variant reference | Alternative variant suggestion | Variant reference |

---

## Testing Checklist

### For Each Store After Implementation:

#### 1. Enquiry System (if enabled)
- [ ] **Header Integration**
  - Enquiry icon appears in header next to cart
  - Icon shows correct count
  - Icon links to enquiry form page
  
- [ ] **Product Page - POA Products**
  - POA products show "Add to Enquiry" button instead of "Add to Cart"
  - Button successfully adds item to enquiry
  - Notification appears when item added
  
- [ ] **Enquiry Drawer**
  - Opens when clicking enquiry icon
  - Shows all enquiry items
  - Quantity can be updated
  - Items can be removed
  - "View Enquiry Form" button works
  
- [ ] **Enquiry Form Page** (`/pages/enquiry-form`)
  - Page loads correctly
  - Shows all enquiry items
  - Form fields validate properly
  - Email capture works (step 1)
  - Full form submission works (step 2)
  - File upload functions (if applicable)

#### 2. Product Unavailability Handling
- [ ] **Discontinued Products**
  - Shows discontinued notice
  - "View archived product page" link works
  - Alternative product loads (if configured)
  - Recommended products load (if no alternative)
  
- [ ] **Variant-Level Unavailability**
  - Unavailable variants show correct status
  - Buy button updates to show unavailability
  - Notice appears for unavailable variants
  - Alternative suggestions work (if configured)
  
- [ ] **Toggle Functionality**
  - Can toggle between archived and alternative views
  - Animations/transitions work smoothly
  - State persists during navigation

#### 3. Custom Grouped Products
- [ ] **Option Display**
  - All configured options appear
  - Options show in correct hierarchy
  - Dependent options update correctly
  
- [ ] **Product Updates**
  - Selecting options updates product info
  - Images update based on selection
  - Price updates correctly
  - SKU/inventory updates
  
- [ ] **Add to Cart**
  - Correct variant/product added to cart
  - Cart drawer/notification shows correct item
  - Quantity selection works
  
- [ ] **Navigation**
  - Browser back/forward works correctly
  - URL updates with selection (if applicable)
  - No duplicate history entries

---

## Deployment Strategy

### Recommended Deployment Order

1. **tiles4less** (Test Store)
   - Most similar structure to build4less
   - Lower traffic for safe testing
   - Complete all features and test thoroughly

2. **building-supplies-online**
   - Second deployment after tiles4less success
   - Higher traffic - monitor closely

3. **insulation4less**
   - Third deployment
   - Verify all features working

4. **insulation4us**
   - Fourth deployment
   - Similar to insulation4less

5. **roofing4us**
   - Final deployment
   - Last verification of all features

### Deployment Steps for Each Store

1. **Backup Current Theme**
   ```bash
   # Download current theme as backup
   shopify theme pull --store=[store-name]
   ```

2. **Apply Code Changes**
   - Update `config/settings_schema.json`
   - Modify `layout/theme.liquid`
   - Update `sections/header.liquid`
   - Modify `sections/main-product.liquid`
   - Update/create snippets as needed

3. **Configure Theme Settings**
   - Go to Theme Customizer
   - Navigate to Theme Settings > Enquiry System
   - Enable/disable as needed
   - Configure button text

4. **Test Features**
   - Use testing checklist above
   - Test on mobile and desktop
   - Verify in multiple browsers

5. **Monitor Performance**
   - Check page load times
   - Monitor JavaScript errors
   - Verify API calls (for enquiry system)

---

## Troubleshooting

### Common Issues and Solutions

#### Enquiry System Not Appearing
- Verify theme setting is enabled
- Check browser console for JavaScript errors
- Ensure enquiry assets are loading in network tab
- Verify API endpoint is accessible

#### Unavailable Products Not Working
- Check product metafields are set correctly
- Verify JavaScript files are loading
- Check for conflicting theme modifications

#### Grouped Products Not Updating
- Ensure all metafields are configured
- Check for JavaScript errors in console
- Verify product relationships are set correctly

### Debug Mode
To enable debug mode for enquiry system:
1. Open browser console
2. Run: `localStorage.setItem('enquiryDebug', 'true')`
3. Reload page to see debug messages

---

## API Configuration

The enquiry system uses a Cloudflare Worker API:
- **Endpoint:** `https://shopify-enquiry-system.diarmuid-1c2.workers.dev`
- **Configured in:** `assets/enquiry-config.js`
- Works across all stores without modification

---

## Support and Maintenance

### Regular Maintenance Tasks
- Monitor enquiry submissions
- Check for JavaScript errors in production
- Update metafields as products change
- Review unavailable product alternatives

### Future Enhancements
- Database integration for enquiry storage
- Email notifications for enquiry submissions
- Advanced grouped product configurations
- A/B testing for unavailability handling

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024 | Initial implementation guide |

---

## Notes

- All JavaScript and CSS files are assumed to be in `/shared/assets/`
- All liquid snippets are assumed to be in `/shared/snippets/`
- Each store maintains its own theme settings
- The enquiry system can be enabled/disabled per store
- Product metafields must be configured in each store's admin