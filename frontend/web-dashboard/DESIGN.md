# Nebula Dashboard v2 Design Specification

## 1. Aesthetic Identity
*   **Theme**: **Nebula Command Center** (Deep Space Cyberpunk)
*   **Colors**:
    *   `bg-deep`: `#05070A`
    *   `bg-surface`: `rgba(13, 17, 23, 0.7)`
    *   `accent-primary`: `#00F5FF` (Neon Cyan)
    *   `accent-danger`: `#FF2D55` (Crimson Pulse)
    *   `border-glass`: `rgba(255, 255, 255, 0.1)`
*   **Typography**:
    *   Headers: `Syncopate` (via Google Fonts) - Space-grade technical feel.
    *   Data/Body: `JetBrains Mono` - Clear, monospace for technical verification data.

## 2. Layout Structure
*   **HUD (Heads-Up Display)**: Minimal top bar showing API connectivity with a "scanning" pulse wave.
*   **Dashboard Grid**: 
    *   Top: 4 dynamic HUD metrics (Active Scans, Threats, Takedowns, Revenue Saved).
    *   Middle-Left (60%): **Threat Command Map** (SVG-based geographic visualization).
    *   Middle-Right (40%): **Real-time Threat Feed** (Animated card list).
    *   Bottom: Jurisdictional Control panels.

## 3. UI Components (Nebula Edition)
*   **GlassPanels**: Cards with `backdrop-filter: blur(20px)` and subtle internal glows.
*   **Threat Cards**: Hovering over a card highlights its location on the map.
*   **The "Notice Modal"**: A full-screen overlay with a sliding entry animation. The notice text is displayed in a "Legal Console" view with a print/copy button.

## 4. Interaction & Motion
*   **Entry**: Staggered reveal of all panels on load.
*   **Threat Pulse**: Detected threats pulse from Crimson to Transparent on the map.
*   **Modal**: Smooth fade-in with a scale-up effect for the notice content.

## 5. Bug Fixes (Targeted)
*   Ensure the modal close button has a high `z-index` and `pointer-events: all`.
*   Ensure notice content is properly rendered as Markdown or pre-formatted text before the modal opens.
