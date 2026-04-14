# Design System Specification: Editorial Vitality

## 1. Overview & Creative North Star
**The Creative North Star: "The Clinical Curator"**

This design system moves beyond the sterile, utilitarian aesthetic typical of medical platforms. It adopts a "High-End Editorial" approach, treating life-saving data and donor interactions with the same prestige as a luxury boutique or a premium news publication. 

To break the "template" look, we leverage **intentional asymmetry** and **breathable compositions**. By utilizing expansive white space (generous `surface` and `surface_container_lowest`) and high-contrast typography, we create an environment that feels urgent yet calm, authoritative yet deeply human. We reject rigid boxes in favor of layered surfaces that bleed into one another, creating a fluid, modern narrative for the donor journey.

---

## 2. Colors & Tonal Depth

Our palette is anchored by a sophisticated interplay of clean whites, deep charcoals, and a high-energy primary red that serves as a pulse throughout the UI.

### The "No-Line" Rule
To achieve a premium feel, **1px solid borders are strictly prohibited for sectioning.** Boundaries must be defined through background color shifts. 
- Use `surface` (#f8f9fa) as your base.
- Shift to `surface_container_low` (#f3f4f5) to define secondary content zones.
- Use `surface_container_highest` (#e1e3e4) for subtle inset areas.

### Surface Hierarchy & Nesting
Think of the UI as physical layers of fine paper. 
- **Layer 0 (Background):** `surface` or `background`.
- **Layer 1 (Main Content):** `surface_container_low`.
- **Layer 2 (Floating Cards):** `surface_container_lowest` (#ffffff).
By nesting a "Lowest" white card on a "Low" grey background, we create natural depth without visual clutter.

### The Glass & Gradient Rule
To prevent a "flat" appearance:
- **Glassmorphism:** Use semi-transparent `surface_container_lowest` (80% opacity) with a `backdrop-blur: 20px` for navigation bars or floating status overlays.
- **Signature Textures:** Main CTAs should utilize a subtle linear gradient from `primary` (#af101a) to `primary_container` (#d32f2f) at a 135-degree angle. This adds a "jewel-toned" depth that feels intentional and premium.

---

## 3. Typography

We utilize **Inter** for its modern, neutral characteristics, allowing the hierarchy and scale to do the heavy lifting.

*   **Display (Large/Medium/Small):** Used for heroic impact. `display-lg` (3.5rem) should be used sparingly to drive the "Editorial" feel, often with tighter letter-spacing (-0.02em).
*   **Headlines:** The workhorses of the system. `headline-lg` (2rem) conveys authority. Use `on_surface` (#191c1d) to ensure maximum readability against white backgrounds.
*   **Body:** `body-lg` (1rem) is our standard for donor information. It provides a comfortable reading rhythm with a generous line-height (1.6).
*   **Labels:** Use `label-md` (0.75rem) in all-caps with increased letter-spacing (+0.05em) for category tags or small metadata to contrast against the bold headlines.

---

## 4. Elevation & Depth

### The Layering Principle
Depth is achieved through **Tonal Layering**. Avoid shadows for standard components. Instead, place a `surface_container_lowest` card on a `surface_container_high` section to create an immediate, soft focal point.

### Ambient Shadows
When an element must "float" (e.g., a critical notification or a primary modal):
- **Color:** Use a tinted shadow based on `on_surface` (19, 28, 29) at 4% to 6% opacity.
- **Blur:** Large and soft (e.g., `box-shadow: 0 20px 40px rgba(25, 28, 29, 0.05)`).

### The "Ghost Border" Fallback
If a border is required for accessibility (e.g., form inputs), use the **Ghost Border**: `outline_variant` (#e4beba) at **20% opacity**. Never use 100% opaque borders; they break the editorial flow.

---

## 5. Components

### Buttons
*   **Primary:** Gradient of `primary` to `primary_container`. Corner radius: `md` (0.75rem). High-contrast `on_primary` text.
*   **Secondary:** `surface_container_highest` background with `on_surface` text. No border.
*   **Tertiary:** Transparent background, `primary` text. Used for "Learn More" or "Cancel" actions.

### Cards & Lists
*   **The Divider Ban:** Strictly forbid 1px horizontal dividers. Separate list items using `1.5rem` (xl) vertical padding or subtle background shifts between `surface_container_low` and `surface_container_lowest`.
*   **Radius:** Cards must use `lg` (1rem) roundedness to feel approachable and modern.

### Input Fields
*   **Styling:** Use `surface_container_low` as the field background. 
*   **States:** On focus, transition the background to `surface_container_lowest` and apply a "Ghost Border" of `primary` at 40% opacity.

### Specialized Components: The Vitality Tracker
*   **Progress Indicators:** Use the `primary` red for active states, but set the track to `primary_fixed` (#ffdad6) to ensure the "Red" identity is present even in the background elements.

---

## 6. Do’s and Don'ts

### Do:
*   **DO** use generous white space. If a section feels "busy," increase the padding from `lg` to `xl`.
*   **DO** use `display-lg` typography to create an editorial "Centerpiece" on landing pages.
*   **DO** utilize `secondary` (#4c616c) for sub-captions to create a sophisticated tonal contrast with the primary headlines.

### Don't:
*   **DON'T** use black (#000000). Always use `on_surface` (#191c1d) for text to maintain a premium charcoal feel.
*   **DON'T** use standard 1px borders to separate content. Use background color shifts.
*   **DON'T** use sharp 90-degree corners. Always adhere to the `DEFAULT` (0.5rem) to `lg` (1rem) roundedness scale to keep the platform feeling "human."
*   **DON'T** clutter the UI with icons. Let the typography and the vibrant `primary` red drive the hierarchy.