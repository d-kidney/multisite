class CartRemoveButton extends HTMLElement {
  constructor() {
    super();

    this.addEventListener("click", (event) => {
      event.preventDefault();
      const cartItems =
        this.closest("cart-items") || this.closest("cart-drawer-items");
      cartItems.updateQuantity(this.dataset.index, 0);
    });
  }
}

customElements.define("cart-remove-button", CartRemoveButton);

class CartItems extends HTMLElement {
  constructor() {
    super();
    
    // Get feature flags from theme settings
    this.features = window.theme?.settings || {};
    
    this.lineItemStatusElement =
      document.getElementById("shopping-cart-line-item-status") ||
      document.getElementById("CartDrawer-LineItemStatus");

    // Only call estDeliveryDate if it exists
    if (typeof estDeliveryDate === 'function') {
      estDeliveryDate();
    }
    
    const debouncedOnChange = debounce((event) => {
      this.onChange(event);
    }, ON_CHANGE_DEBOUNCE_TIMER);

    this.addEventListener("change", debouncedOnChange.bind(this));
    
    // Initialize shipping protection if enabled
    if (this.features.shipping_protection) {
      this.initializeShippingProtection();
    }
  }

  cartUpdateUnsubscriber = undefined;

  connectedCallback() {
    this.cartUpdateUnsubscriber = subscribe(
      PUB_SUB_EVENTS.cartUpdate,
      (event) => {
        if (event.source === "cart-items") {
          return;
        }
        this.onCartUpdate();
      }
    );
  }

  disconnectedCallback() {
    if (this.cartUpdateUnsubscriber) {
      this.cartUpdateUnsubscriber();
    }
  }

  resetQuantityInput(id) {
    const input = this.querySelector(`#Quantity-${id}`);
    input.value = input.getAttribute("value");
    this.isEnterPressed = false;
  }

  setValidity(event, index, message) {
    event.target.setCustomValidity(message);
    event.target.reportValidity();
    this.resetQuantityInput(index);
    event.target.select();
  }

  validateQuantity(event) {
    const inputValue = parseInt(event.target.value);
    const index = event.target.dataset.index;
    let message = "";

    if (inputValue < event.target.dataset.min) {
      message = window.quickOrderListStrings.min_error.replace(
        "[min]",
        event.target.dataset.min
      );
    } else if (inputValue > parseInt(event.target.max)) {
      message = window.quickOrderListStrings.max_error.replace(
        "[max]",
        event.target.max
      );
    } else if (inputValue % parseInt(event.target.step) !== 0) {
      message = window.quickOrderListStrings.step_error.replace(
        "[step]",
        event.target.step
      );
    }

    if (message) {
      this.setValidity(event, index, message);
    } else {
      event.target.setCustomValidity("");
      event.target.reportValidity();
      this.updateQuantity(
        index,
        inputValue,
        document.activeElement.getAttribute("name"),
        event.target.dataset.quantityVariantId
      );
    }
  }

  onChange(event) {
    this.validateQuantity(event);
  }

  onCartUpdate() {
    if (this.tagName === "CART-DRAWER-ITEMS") {
      fetch(`${routes.cart_url}?section_id=cart-drawer`)
        .then((response) => response.text())
        .then((responseText) => {
          const html = new DOMParser().parseFromString(
            responseText,
            "text/html"
          );
          const selectors = ["cart-drawer-items", ".cart-drawer__footer"];
          for (const selector of selectors) {
            const targetElement = document.querySelector(selector);
            const sourceElement = html.querySelector(selector);
            if (targetElement && sourceElement) {
              targetElement.replaceWith(sourceElement);
            }
          }
        })
        .catch((e) => {
          console.error(e);
        });
    } else {
      fetch(`${routes.cart_url}?section_id=main-cart-items`)
        .then((response) => response.text())
        .then((responseText) => {
          const html = new DOMParser().parseFromString(
            responseText,
            "text/html"
          );
          const sourceQty = html.querySelector("cart-items");
          this.innerHTML = sourceQty.innerHTML;
        })
        .catch((e) => {
          console.error(e);
        });
    }
  }

  getSectionsToRender() {
    return [
      {
        id: "main-cart-items",
        section: document.getElementById("main-cart-items").dataset.id,
        selector: ".js-contents",
      },
      {
        id: "cart-icon-bubble",
        section: "cart-icon-bubble",
        selector: ".shopify-section",
      },
      {
        id: "cart-live-region-text",
        section: "cart-live-region-text",
        selector: ".shopify-section",
      },
      {
        id: "main-cart-footer",
        section: document.getElementById("main-cart-footer").dataset.id,
        selector: ".js-contents",
      },
    ];
  }

  updateQuantity(line, quantity, name, variantId) {
    this.enableLoading(line);

    const body = JSON.stringify({
      line,
      quantity,
      sections: this.getSectionsToRender().map((section) => section.section),
      sections_url: window.location.pathname,
    });

    fetch(`${routes.cart_change_url}`, { ...fetchConfig(), ...{ body } })
      .then((response) => {
        return response.text();
      })
      .then((state) => {
        const parsedState = JSON.parse(state);
        const quantityElement =
          document.getElementById(`Quantity-${line}`) ||
          document.getElementById(`Drawer-quantity-${line}`);
        const items = document.querySelectorAll(".cart-item");

        if (parsedState.errors) {
          quantityElement.value = quantityElement.getAttribute("value");
          this.updateLiveRegions(line, parsedState.errors);
          return;
        }

        this.classList.toggle("is-empty", parsedState.item_count === 0);
        const cartDrawerWrapper = document.querySelector("cart-drawer");
        const cartFooter = document.getElementById("main-cart-footer");

        if (cartFooter)
          cartFooter.classList.toggle("is-empty", parsedState.item_count === 0);
        if (cartDrawerWrapper)
          cartDrawerWrapper.classList.toggle(
            "is-empty",
            parsedState.item_count === 0
          );

        this.getSectionsToRender().forEach((section) => {
          const elementToReplace =
            document
              .getElementById(section.id)
              .querySelector(section.selector) ||
            document.getElementById(section.id);
          elementToReplace.innerHTML = this.getSectionInnerHTML(
            parsedState.sections[section.section],
            section.selector
          );
        });
        const updatedValue = parsedState.items[line - 1]
          ? parsedState.items[line - 1].quantity
          : undefined;
        if (updatedValue && updatedValue !== quantity) {
          this.updateError(updatedValue, line);
        }

        this.updateLiveRegions(line, parsedState.item_count);
        const lineItem =
          document.getElementById(`CartItem-${line}`) ||
          document.getElementById(`CartDrawer-Item-${line}`);
        if (lineItem && lineItem.querySelector(`[name="${name}"]`)) {
          cartDrawerWrapper
            ? trapFocus(
                cartDrawerWrapper,
                lineItem.querySelector(`[name="${name}"]`)
              )
            : lineItem.querySelector(`[name="${name}"]`).focus();
        } else if (parsedState.item_count === 0 && cartDrawerWrapper) {
          trapFocus(
            cartDrawerWrapper.querySelector(".drawer__inner-empty"),
            cartDrawerWrapper.querySelector("a")
          );
        } else if (document.querySelector(".cart-item") && cartDrawerWrapper) {
          trapFocus(cartDrawerWrapper, document.querySelector(".cart-item__name"));
        }

        publish(PUB_SUB_EVENTS.cartUpdate, {
          source: "cart-items",
          cartData: parsedState,
          variantId: variantId,
        });
        this.disableLoading(line);
      })
      .catch(() => {
        this.querySelectorAll(".loading__spinner").forEach((overlay) =>
          overlay.classList.add("hidden")
        );
        const errors =
          document.getElementById("cart-errors") ||
          document.getElementById("CartDrawer-CartErrors");
        errors.textContent = window.cartStrings.error;
        this.disableLoading(line);
      });
  }

  updateError(updatedValue, line) {
    this.querySelectorAll(".cart-item__error-text").forEach((a) =>
      a.remove()
    );
    const lineItem =
      document.getElementById(`CartItem-${line}`) ||
      document.getElementById(`CartDrawer-Item-${line}`);
    const quantityElement =
      document.getElementById(`Quantity-${line}`) ||
      document.getElementById(`Drawer-quantity-${line}`);
    quantityElement.value = updatedValue;
    const selector = document.querySelector(".cart-item__error-text-template").cloneNode(true);
    selector.classList.remove("cart-item__error-text-template");
    selector.removeAttribute("aria-hidden");
    const errorTextElement = selector.querySelector(".cart-item__error-text");
    errorTextElement.innerHTML = window.cartStrings.quantityError.replace(
      "[quantity]",
      updatedValue
    );
    lineItem.appendChild(selector);
  }

  updateLiveRegions(line, itemCount = undefined) {
    const lineItemError =
      document.getElementById(`Line-item-error-${line}`) ||
      document.getElementById(`CartDrawer-LineItemError-${line}`);
    if (lineItemError)
      lineItemError.querySelector(".cart-item__error-text").innerHTML =
        window.cartStrings.quantityError.replace(
          "[quantity]",
          document.getElementById(`Quantity-${line}`).value
        );

    this.lineItemStatusElement.setAttribute("aria-hidden", true);

    const cartStatus =
      document.getElementById("cart-live-region-text") ||
      document.getElementById("CartDrawer-LiveRegionText");
    cartStatus.setAttribute("aria-hidden", false);

    setTimeout(() => {
      cartStatus.setAttribute("aria-hidden", true);
    }, 1000);
  }

  getSectionInnerHTML(html, selector) {
    return new DOMParser()
      .parseFromString(html, "text/html")
      .querySelector(selector).innerHTML;
  }

  enableLoading(line) {
    const mainCartItems =
      document.getElementById("main-cart-items") ||
      document.getElementById("CartDrawer-CartItems");
    mainCartItems.classList.add("cart__items--disabled");

    const cartItemElements = this.querySelectorAll(
      `#CartItem-${line} .loading__spinner,
      #CartDrawer-Item-${line} .loading__spinner`
    );

    [...cartItemElements].forEach((overlay) => overlay.classList.remove("hidden"));

    document.activeElement.blur();
    this.lineItemStatusElement.setAttribute("aria-hidden", false);
  }

  disableLoading(line) {
    const mainCartItems =
      document.getElementById("main-cart-items") ||
      document.getElementById("CartDrawer-CartItems");
    mainCartItems.classList.remove("cart__items--disabled");

    const cartItemElements = this.querySelectorAll(
      `#CartItem-${line} .loading__spinner,
      #CartDrawer-Item-${line} .loading__spinner`
    );

    cartItemElements.forEach((overlay) => overlay.classList.add("hidden"));
  }
  
  // Shipping Protection Methods (only active when feature flag is enabled)
  initializeShippingProtection() {
    // This would be populated from theme settings or metafields
    this.shippingProtectionVariants = window.theme?.shippingProtectionVariants || [];
    this.shippingProtectionPercentage = window.theme?.settings?.shipping_protection_percentage || 3;
    
    // Add checkout button listener for shipping protection
    document.addEventListener('click', (e) => {
      if (e.target.matches('.cart__checkout-button')) {
        this.handleShippingProtectionCheckout(e);
      }
    });
  }
  
  handleShippingProtectionCheckout(event) {
    if (!this.features.shipping_protection) return;
    
    const cartTotal = this.getCartTotal();
    const protectionAmount = (cartTotal * this.shippingProtectionPercentage) / 100;
    const variantId = this.findClosestProtectionVariant(protectionAmount);
    
    if (variantId && !this.hasShippingProtection()) {
      event.preventDefault();
      this.addShippingProtection(variantId);
    }
  }
  
  getCartTotal() {
    const totalElement = document.querySelector('[data-cart-total]');
    return totalElement ? parseFloat(totalElement.dataset.cartTotal) / 100 : 0;
  }
  
  hasShippingProtection() {
    // Check if shipping protection is already in cart
    const cartItems = document.querySelectorAll('.cart-item');
    return Array.from(cartItems).some(item => 
      item.dataset.variantId && this.shippingProtectionVariants.includes(item.dataset.variantId)
    );
  }
  
  findClosestProtectionVariant(amount) {
    // Logic to find the closest variant based on price
    // This would need to be implemented based on actual variant data
    return this.shippingProtectionVariants[0]; // Placeholder
  }
  
  addShippingProtection(variantId) {
    fetch('/cart/add.js', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        id: variantId,
        quantity: 1,
        properties: {
          '_shipping_protection': 'true',
          '_percentage': this.shippingProtectionPercentage
        }
      })
    })
    .then(response => response.json())
    .then(() => {
      // Proceed with checkout
      document.querySelector('.cart__checkout-button').click();
    })
    .catch(error => {
      console.error('Error adding shipping protection:', error);
      // Proceed with checkout anyway
      document.querySelector('.cart__checkout-button').click();
    });
  }
}

customElements.define("cart-items", CartItems);

class CartDrawer extends HTMLElement {
  constructor() {
    super();

    this.addEventListener("keyup", (evt) => evt.code === "Escape" && this.close());
    this.querySelector("#CartDrawer-Overlay").addEventListener(
      "click",
      this.close.bind(this)
    );
    this.setHeaderCartIconAccessibility();
  }

  setHeaderCartIconAccessibility() {
    const cartLink = document.querySelector("#cart-icon-bubble");
    cartLink.setAttribute("role", "button");
    cartLink.setAttribute("aria-haspopup", "dialog");
    cartLink.addEventListener("click", (event) => {
      event.preventDefault();
      this.open(cartLink);
    });
    cartLink.addEventListener("keydown", (event) => {
      if (event.code.toUpperCase() === "SPACE") {
        event.preventDefault();
        this.open(cartLink);
      }
    });
  }

  open(triggeredBy) {
    if (triggeredBy) this.setActiveElement(triggeredBy);
    const cartDrawerNote = this.querySelector('[id^="Details-"] summary');
    if (cartDrawerNote && !cartDrawerNote.hasAttribute("role"))
      this.setSummaryAccessibility(cartDrawerNote);
    setTimeout(() => {
      this.classList.add("animate", "active");
    });

    this.addEventListener(
      "transitionend",
      () => {
        const containerToTrapFocusOn = this.classList.contains("is-empty")
          ? this.querySelector(".drawer__inner-empty")
          : document.getElementById("CartDrawer");
        const focusElement = this.querySelector(".drawer__inner") || this.querySelector(".drawer__close");
        trapFocus(containerToTrapFocusOn, focusElement);
      },
      { once: true }
    );

    document.body.classList.add("overflow-hidden");
  }

  close() {
    this.classList.remove("active");
    removeTrapFocus(this.activeElement);
    document.body.classList.remove("overflow-hidden");
  }

  setSummaryAccessibility(cartDrawerNote) {
    cartDrawerNote.setAttribute("role", "button");
    cartDrawerNote.setAttribute("aria-expanded", "false");

    if (cartDrawerNote.nextElementSibling.getAttribute("id")) {
      cartDrawerNote.setAttribute(
        "aria-controls",
        cartDrawerNote.nextElementSibling.id
      );
    }

    cartDrawerNote.addEventListener("click", (event) => {
      event.currentTarget.setAttribute(
        "aria-expanded",
        !event.currentTarget.closest("details").hasAttribute("open")
      );
    });

    cartDrawerNote.parentElement.addEventListener("keyup", onKeyUpEscape);
  }

  renderContents(parsedState) {
    this.querySelector(".drawer__inner").classList.contains("is-empty") &&
      this.querySelector(".drawer__inner").classList.remove("is-empty");
    this.productId = parsedState.id;
    this.getSectionsToRender().forEach((section) => {
      const sectionElement = section.selector
        ? document.querySelector(section.selector)
        : document.getElementById(section.id);
      sectionElement.innerHTML = this.getSectionInnerHTML(
        parsedState.sections[section.id],
        section.selector
      );
    });

    setTimeout(() => {
      this.querySelector("#CartDrawer-Overlay").addEventListener(
        "click",
        this.close.bind(this)
      );
      this.open();
    });
  }

  getSectionInnerHTML(html, selector = ".shopify-section") {
    return new DOMParser()
      .parseFromString(html, "text/html")
      .querySelector(selector).innerHTML;
  }

  getSectionsToRender() {
    return [
      {
        id: "cart-drawer",
        selector: "#CartDrawer",
      },
      {
        id: "cart-icon-bubble",
      },
    ];
  }

  getSectionDOM(html, selector = ".shopify-section") {
    return new DOMParser()
      .parseFromString(html, "text/html")
      .querySelector(selector);
  }

  setActiveElement(element) {
    this.activeElement = element;
  }
}

customElements.define("cart-drawer", CartDrawer);

// B2B Validation (only active when b2b_features flag is enabled)
document.addEventListener("DOMContentLoaded", function () {
  const features = window.theme?.settings || {};
  
  if (!features.b2b_features) return;

  // Radio validation for accept alternatives and offload confirmation
  function setupRadioValidation(name, alertClass) {
    const radioButtons = document.querySelectorAll(`input[name="${name}"]`);
    const alert = document.querySelector(`.${alertClass}`);

    if (radioButtons.length === 0) return null;

    // Hide alert initially
    if (alert) alert.style.display = "none";

    function validate() {
      const isChecked = Array.from(radioButtons).some((radio) => radio.checked);
      if (!isChecked && alert) {
        alert.style.display = "block";
        alert.scrollIntoView({ behavior: "smooth", block: "center" });
      } else if (alert) {
        alert.style.display = "none";
      }
      return isChecked;
    }

    radioButtons.forEach((radio) => {
      radio.addEventListener("change", () => {
        if (alert) alert.style.display = "none";
      });
    });

    return {
      validate,
      getSelectedValue: () => {
        const selected = Array.from(radioButtons).find((r) => r.checked);
        return selected ? selected.value : null;
      },
    };
  }

  // Setup validation and attribute collection for each group
  const altValidation = setupRadioValidation(
    "attributes[accept_alt]",
    "accept_alt"
  );
  const offloadValidation = setupRadioValidation(
    "attributes[offload_confirmation]",
    "offload_confirmation"
  );

  // Main checkout button
  const checkoutButton = document.querySelector(".cart__checkout-button:not(.cart__checkout-button-original)");
  if (checkoutButton) {
    // Clone and hide the original button
    const originalButton = checkoutButton.cloneNode(true);
    originalButton.classList.add("cart__checkout-button-original");
    originalButton.style.display = "none";
    checkoutButton.after(originalButton);

    // Override the visible button behavior
    checkoutButton.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      
      let isFormValid = true;
      if (altValidation && !altValidation.validate()) isFormValid = false;
      if (offloadValidation && !offloadValidation.validate()) isFormValid = false;

      if (!isFormValid) {
        window.scrollTo({ top: 0, behavior: "smooth" });
        return false;
      }

      // Create form data with attributes
      const form = document.querySelector("form[action='/cart']");
      if (!form) {
        originalButton.click();
        return;
      }

      // Add selected values as hidden inputs
      [altValidation, offloadValidation].forEach((validationObj) => {
        if (validationObj) {
          const val = validationObj.getSelectedValue();
          if (val) {
            const input = document.createElement("input");
            input.type = "hidden";
            input.name = validationObj === altValidation 
              ? "attributes[accept_alt]" 
              : "attributes[offload_confirmation]";
            input.value = val;
            form.appendChild(input);
          }
        }
      });

      // Trigger the original checkout
      originalButton.click();
    });
  }

  // Handle fast checkout buttons (ShopPay, Apple Pay, etc.)
  function getSelectedValue(name) {
    const radios = document.querySelectorAll(`input[name="${name}"]`);
    const selected = Array.from(radios).find((r) => r.checked);
    return selected ? selected.value : null;
  }

  function handleFastCheckoutClick(event) {
    const acceptAlt = getSelectedValue("attributes[accept_alt]");
    const offloadConf = getSelectedValue("attributes[offload_confirmation]");

    const attrs = {};
    if (acceptAlt) attrs["accept_alt"] = acceptAlt;
    if (offloadConf) attrs["offload_confirmation"] = offloadConf;

    if (Object.keys(attrs).length === 0) return;

    // Save attributes to cart
    fetch("/cart/update.js", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ attributes: attrs }),
    });
  }

  // Monitor for fast checkout buttons
  const observer = new MutationObserver(() => {
    const fastButtons = document.querySelectorAll(
      ".shopify-payment-button button, .additional-checkout-buttons button"
    );
    fastButtons.forEach((btn) => {
      if (!btn.hasAttribute("data-validation-attached")) {
        btn.setAttribute("data-validation-attached", "true");
        btn.addEventListener("click", handleFastCheckoutClick);
      }
    });
  });

  observer.observe(document.body, { childList: true, subtree: true });
});