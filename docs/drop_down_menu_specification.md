
# 📑 Specification – Dropdown Menu Component (Updated)

## 1. **Purpose**

Provide a lightweight, SEO-friendly dropdown menu for an HTML SEO Cloud Stack site (like Salvo Metal Works). The dropdown should automatically adapt to the number of child items, keeping the layout neat and user-friendly.

---

## 2. **Requirements**

### **Functional**

* Parent menu items open dropdowns on **hover (desktop)** and **tap (mobile)**.
* Dropdown supports **multi-level nesting** (at least 2 levels).
* If a dropdown has **4 or more items**, display them in a **stacked grid row**:

  * Maximum **4 items per row**.
  * Items wrap to the next row when exceeded.
* All links must remain crawlable and SEO-friendly.

### **Non-Functional**

* Semantic HTML `<nav>`, `<ul>`, `<li>`.
* Accessible (keyboard nav + ARIA roles).
* Lightweight: CSS-first approach; optional JS for mobile toggle.
* Fully responsive.

---

## 3. **Structure**

### **HTML Skeleton (unchanged)**

```html
<nav class="main-nav">
  <ul class="menu">
    <li><a href="/index.html">Home</a></li>
    <li class="has-dropdown">
      <a href="/products.html" aria-haspopup="true" aria-expanded="false">Products ▾</a>
      <ul class="dropdown">
        <li><a href="/products/cupolas.html">Cupolas</a></li>
        <li><a href="/products/chimney-shrouds.html">Chimney Shrouds</a></li>
        <li><a href="/products/finials.html">Finials</a></li>
        <li><a href="/products/roof-vents.html">Roof Vents</a></li>
        <li><a href="/products/leader-boxes.html">Leader Boxes</a></li>
        <li><a href="/products/snow-guards.html">Snow Guards</a></li>
      </ul>
    </li>
    <li><a href="/about.html">About Us</a></li>
    <li><a href="/contact.html">Contact</a></li>
  </ul>
</nav>
```

---

## 4. **Styling (CSS Spec)**

* **Dropdown (general)**

  * Hidden by default (`display: none`).
  * Positioned `absolute` under parent.
  * Background: white (or brand secondary).
  * Box-shadow for depth.
  * On hover/focus: `display: flex`.

* **When < 4 items**

  * Dropdown is a **vertical stack** (`flex-direction: column`).

* **When ≥ 4 items**

  * Dropdown becomes a **grid row**:

    * `display: grid;`
    * `grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));`
    * Limit 4 items per row (auto-wrap to next row).
  * Uniform item sizing for balance.

* **Mobile**

  * Dropdown items stack vertically regardless of count (to save space).
  * Hamburger toggle controls visibility.

---

## 5. **Accessibility**

* `role="navigation"` on `<nav>`.
* `aria-haspopup="true"` and dynamic `aria-expanded` on dropdown parents.
* Ensure keyboard navigation works across grid layout (arrow keys move correctly).

---

## 6. **Responsive Behavior**

* **Desktop (≥1024px):** horizontal nav, hover dropdowns, grid rows for ≥4 items.
* **Tablet (768–1023px):** similar behavior, dropdown rows collapse tighter.
* **Mobile (<768px):** hamburger toggles vertical stacked menu, no multi-column rows.

---

## 7. **Optional Enhancements**

* Smooth CSS transitions when opening.
* Active link highlighting.
* Sticky nav on scroll.
* Schema markup (`SiteNavigationElement`).

---

⚡ TL;DR of the update:

> **If a dropdown contains 4 or more items, display them in a grid row of max 4 per row. Additional items flow into the next row. Mobile always stays vertical.**


