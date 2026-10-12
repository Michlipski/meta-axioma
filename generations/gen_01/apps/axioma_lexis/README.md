# Axioma Lexis

> **Adaptive Spaced Repetition Vocabulary & Flashcard Workspace for Android**  
> Compiled autonomously by **System $G_1$** (Meta-Axioma Recursive Compiler) to realize the High-Level Jettison.

---

## 1. Product Overview: The Free, Open Mem-App Alternative

**Axioma Lexis** is an adaptive vocabulary memorization app and offline dictionary built specifically for **Android mobile devices** and intermediate-to-advanced language learners.

It directly mirrors and elevates the workflow of **[Mem-App](https://www.mem-app.com/) ("Let's Memorise Vocabulary")**, while removing all paywalls, subscription tiers, and word limits.

- **Target Persona:** Intermediate+ English Learner / Android Mobile User.
- **100% Free Forever:** Zero subscription paywalls, no 50-word ceiling (unlike Mem-App's premium tier), zero external paid APIs.
- **Offline-First & Local:** High-speed local dictionary seed cache, decoupled JSON storage, and service worker offline caching.
- **Native Android Experience:** Designed as a mobile-first Progressive Web App (PWA) with thumb-reach navigation, 3D card flip animations, and 1-tap "Add to Home screen" installation on Android Chrome.

---

## 2. Key Product Mechanics & Ergonomics

### 📖 Progressive Dictionary Lookup
- Search any word instantly. Auto-suggests from offline seed data and queries free public definitions with offline fallbacks.
- View US (`/ˈepɪtəmi/`) and UK (`/ɪˈpɪtəmi/`) phonetic IPA transcriptions.
- Dual native audio pronunciation: tap **US 🇺🇸** or **UK 🇬🇧** to hear native browser speech synthesis.
- Includes parts of speech, rich contextual definitions, real-world usage examples, synonyms, antonyms, and bilingual translations.

### ⚡ 1-Tap "Add to Deck"
- In Mem-App, users must navigate across complex menus to turn a lookup into a study item.
- In Axioma Lexis, every dictionary result has a prominent **"+ Add to Deck"** button. One tap captures the word, phonetic guide, definition, and example into your active flashcard deck without leaving the screen.

### 🧠 Adaptive Spaced Repetition (SM-2)
- State-of-the-art SuperMemo-2 (SM-2) spaced repetition algorithm:
  - **Forgot** (Rating 1): Interval resets to 1 day; Ease Factor drops.
  - **Hard** (Rating 2): Interval increases moderately (1.2×).
  - **Good** (Rating 3): Standard SM-2 interval expansion (Ease Factor multiplier).
  - **Easy** (Rating 4): Interval expands with bonus multiplier (1.3× Ease Factor).
- Review due queue dynamically surfaces cards when review is due, with an on-demand review mode.

### ↩️ Functorial Undo (`L1-002`)
- **The #1 Pain Point of Mobile SRS Apps:** In traditional flashcard apps, an accidental finger tap on "Forgot" or "Easy" corrupts the card's interval schedule with no way to undo.
- Axioma Lexis implements **Functorial Reversibility (`L1-002`)**: tap the **Undo** button (or press `Cmd+Z` / `Ctrl+Z`) to immediately reverse accidental ratings and restore the exact prior deck state and queue position.

---

## 3. Invariant Architecture (The 7 Structural Axioms)

Axioma Lexis was compiled directly against the proven $G_1$ structural invariant suite:

| Axiom ID | Name | Application Role |
| :--- | :--- | :--- |
| **`L1-002`** | Functorial State Evolution | Reversible SRS rating morphisms; dual undo/redo history stacks. |
| **`L1-004`** | Universal Grammar Schemas | JSON Schema validation for all cards, dictionary entries, and deck state. |
| **`L1-011_3`** | Decoupled Persistence across Boundary 3 | Atomic, isolated disk writes to `data/app_state.json`. |
| **`L1-008`** | Landauer Thermodynamic Accounting | Live cognitive bit-erasure calculation ($k_B T \ln 2$) tracked on every card mutation. |
| **`L1-015`** | Zero-Trust State Gateway | Pure-function state machine enforcing valid transitions (`RATE_CARD`, `ADD_CARD`). |
| **`L1-016`** | Demarcated Exception Enclaves | Strict blast-radius containment with structured audit witnesses on failures. |
| **`L1-015_1`** | Compositional Boundary Isolation | Dictionary lookup engine and SRS review scheduler compose orthogonally. |

---

## 4. How to Run on Desktop & Android Mobile

### A. Run Locally (Desktop)
```bash
# Launch server (default port 8090)
python3 generations/gen_01/apps/axioma_lexis/run.py
```
Open **`http://localhost:8090`** in any modern web browser.

---

### B. Run on Android Mobile (Over Local Wi-Fi)
1. Ensure your laptop and Android phone are connected to the same Wi-Fi network.
2. Find your laptop's local IP address:
   ```bash
   # macOS:
   ipconfig getifaddr en0
   ```
3. Start the server (it automatically binds `0.0.0.0` to allow local network connections):
   ```bash
   python3 generations/gen_01/apps/axioma_lexis/run.py
   ```
4. Open **Google Chrome** on your Android phone and browse to:
   ```text
   http://<YOUR_LAPTOP_IP>:8090
   ```
5. **Install to Home Screen:**
   - Tap the banner **"Install Axioma Lexis"** or tap Chrome's three-dot menu `⋮` > **"Add to Home screen"** / **"Install app"**.
   - Axioma Lexis now opens full-screen without URL bars, looking and feeling like a native Android APK!

---

### C. Run on Android Mobile (Via USB / ADB Port Forwarding)
If your Wi-Fi blocks peer-to-peer traffic, use USB debugging:
```bash
# Forward port 8090 from device to host
adb reverse tcp:8090 tcp:8090

# Start app
python3 generations/gen_01/apps/axioma_lexis/run.py
```
Then open **`http://localhost:8090`** directly inside Chrome on Android!

---

## 5. Verification & Testing

Run the full automated test suite verifying dictionary lookups, SM-2 algorithms, functorial undo, and exception enclaves:

```bash
python3 -m unittest -v generations/gen_01/apps/axioma_lexis/tests/test_app.py
```
