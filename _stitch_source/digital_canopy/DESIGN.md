---
name: Digital Canopy
colors:
  surface: '#101413'
  surface-dim: '#101413'
  surface-bright: '#363a38'
  surface-container-lowest: '#0b0f0e'
  surface-container-low: '#181c1b'
  surface-container: '#1c201f'
  surface-container-high: '#272b29'
  surface-container-highest: '#323634'
  on-surface: '#e0e3e0'
  on-surface-variant: '#bacac3'
  inverse-surface: '#e0e3e0'
  inverse-on-surface: '#2d3130'
  outline: '#85948e'
  outline-variant: '#3b4a45'
  surface-tint: '#32deb9'
  primary: '#4cf0c9'
  on-primary: '#00382c'
  primary-container: '#19d3ae'
  on-primary-container: '#005645'
  inverse-primary: '#006b57'
  secondary: '#4addb9'
  on-secondary: '#00382c'
  secondary-container: '#00b896'
  on-secondary-container: '#004234'
  tertiary: '#d0d9d5'
  on-tertiary: '#2a3230'
  tertiary-container: '#b4bdba'
  on-tertiary-container: '#444d4a'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#5bfbd4'
  primary-fixed-dim: '#32deb9'
  on-primary-fixed: '#002019'
  on-primary-fixed-variant: '#005141'
  secondary-fixed: '#6cfad4'
  secondary-fixed-dim: '#4addb9'
  on-secondary-fixed: '#002018'
  on-secondary-fixed-variant: '#005140'
  tertiary-fixed: '#dce4e1'
  tertiary-fixed-dim: '#c0c8c5'
  on-tertiary-fixed: '#151d1b'
  on-tertiary-fixed-variant: '#404946'
  background: '#101413'
  on-background: '#e0e3e0'
  surface-variant: '#323634'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 48px
    fontWeight: '800'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '800'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '500'
    lineHeight: '1.6'
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '500'
    lineHeight: '1.5'
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1.0'
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  container-padding-desktop: 40px
  container-padding-mobile: 20px
  gutter: 24px
  section-gap: 80px
---

## Brand & Style

The brand personality is authoritative, scientific, and premium. It positions itself as a sophisticated intelligence layer for high-end agriculture, moving away from "earthy" cliches toward a high-tech, data-centric aesthetic. The UI should evoke a sense of precision and calm, akin to a high-performance laboratory or an aerospace cockpit.

The design style is **Modern Minimalist with Organic Glassmorphism**. It utilizes heavy whitespace to allow complex data to breathe. Backgrounds remain deep and dark to minimize eye strain and emphasize glowing data visualizations. Subtle glass effects and translucent layers provide depth without clutter, while "organic" influences are felt through curved corners and fluid motion rather than literal imagery.

## Colors

The palette is rooted in deep, atmospheric darks to create a "void" where data and insights can shine. 

- **Backgrounds:** Use `#050807` for the primary canvas and `#07100D` for distinct section containers.
- **Accents:** Emerald Green (`#19D3AE`) serves as the primary action color and indicator of health/growth. Turquoise/Mint (`#55E6C1`) is reserved for highlights, secondary call-to-actions, and data visualization gradients.
- **Neutrals:** Use a scale of muted teals and charcoals for borders and text to maintain the "scientific" feel, avoiding pure grays to keep the palette cohesive.

## Typography

This design system utilizes **Plus Jakarta Sans** for its modern, geometric construction that feels both technical and approachable. 

- **Headings:** Use Bold or ExtraBold weights with tighter letter spacing to create a commanding presence. 
- **Body:** Stick to Medium (500) weight as the default for readability against dark backgrounds; Regular weight should be used sparingly for secondary metadata. 
- **Labels:** Use uppercase with slight letter spacing for technical data points, status indicators, and category labels to reinforce the scientific aesthetic.

## Layout & Spacing

The layout follows a **fluid grid** with strict adherence to an 8px spacing scale. 

- **Desktop:** 12-column grid with a maximum content width of 1440px. Use generous margins (40px) to maintain a premium, spacious feel.
- **Tablet:** 8-column grid with 32px margins.
- **Mobile:** 4-column grid with 20px margins.
- **Rhythm:** Use large vertical gaps (80px+) between major sections to define the "High Whitespace" narrative. Components within cards should use tight 16px or 24px padding to maintain a compact, data-dense technical feel inside a minimalist frame.

## Elevation & Depth

Depth is achieved through **Tonal Layering** and **Glassmorphism**, rather than traditional drop shadows.

- **Level 0:** Base background (`#050807`).
- **Level 1:** Surface containers (`#0D1513`) with a 1px stroke of `rgba(255, 255, 255, 0.05)`.
- **Level 2:** Floating panels/Modals using a backdrop filter (blur: 20px) and a semi-transparent fill of `#0D1513` at 80% opacity.
- **Highlights:** Use an inner glow or a subtle top-border (1px) in the Emerald accent color for active or high-priority elements to simulate "lit" hardware interfaces.

## Shapes

The shape language is **Rounded**, balancing technical precision with organic flow. 

- Standard components (Buttons, Inputs) use a **0.5rem (8px)** corner radius.
- Large containers and cards use **1rem (16px)**.
- Data visualization nodes and status chips use **Pill-shapes** to provide visual contrast against the more structured grid-based layout.
- Avoid perfectly sharp corners to maintain the "organic" brand ethos.

## Components

- **Buttons:** Primary buttons are solid Emerald (`#19D3AE`) with black text. Secondary buttons are ghost-style with an Emerald border and Turquoise text.
- **Cards:** Use the Dark Charcoal surface with a subtle 1px border. No shadows; depth is conveyed via color contrast and internal padding.
- **Inputs:** Darker than the surface background with a 1px border that glows Emerald on focus. Labels sit outside the field in a smaller, semi-transparent font.
- **Chips/Status:** Pill-shaped with a low-opacity background tint of the status color (e.g., 10% Emerald for "Healthy") and a solid high-contrast text.
- **Data Visuals:** Use thin, glowing lines for charts. Avoid solid fills; use gradients that transition from Emerald to transparent.
- **Icons:** Thin-stroke (1.5pt) linear icons. Avoid filled icons to keep the interface light and "airy."