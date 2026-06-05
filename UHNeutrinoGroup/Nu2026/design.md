# Poster Color & Accessibility — Design Document

**Project:** Neutrino 2026 poster — antineutrino source localization (IBD, Li-6 doped scintillator)
**Scope:** Color and color-accessibility for all generated figures (matplotlib/seaborn) and the Geant4 IBD event-display render.
**Status:** Authoritative / source of truth.
**Design target:** Red-green color vision deficiency (deuteranopia + protanopia, ~8% of males). Accessibility takes precedence over institutional theming for all data-bearing color.

---

## How to use this document (read first, agent)

1. This file is the **single source of truth** for color decisions. When generating or regenerating any plot or render, conform to it.
2. **Do not reintroduce University of Hawaiʻi brand colors into data encodings.** They were deliberately removed (see Decision Log D1). UH colors are permitted **only** in non-data poster chrome (§9).
3. When you add, remove, or recolor any series/category that appears together in one figure, **run the verification protocol (§7)** and confirm the acceptance criteria before considering the figure done.
4. Color is never the only channel. Every multi-series figure must carry a redundant encoding (linestyle, marker, direct label, or position) per §5.
5. All figures and renders use a **white background**.
6. If a rule here conflicts with a request, surface the conflict rather than silently overriding the rule.

---

## 1. Quick reference

```
Categorical palette : Okabe-Ito (color-universal-design set)
Background          : white, everywhere
Sequential colormap : cividis   (CVD-optimized; default for likelihood/density maps)
Diverging colormap  : PuOr or RdBu  (colorblind-safe; for signed residuals)
Redundancy          : MANDATORY for multi-line plots (color + linestyle)
Acceptance floor    : worst-pair ΔE (CAM02-UCS) > 12 under deuteranopia AND protanopia
Never on white      : #F0E442 (pure yellow) for thin lines — washes out
Verification        : colorspacious worst-pair ΔE + 4-way CVD render (see §7)
```

Okabe-Ito hex values:

| Name | Hex |
|---|---|
| Black | `#000000` |
| Orange | `#E69F00` |
| Sky blue | `#56B4E9` |
| Bluish green | `#009E73` |
| Yellow | `#F0E442` |
| Blue | `#0072B2` |
| Vermillion | `#D55E00` |
| Reddish purple | `#CC79A7` |

---

## 2. Core accessibility principles (doctrine)

These are the *why* behind every rule below. Do not violate them to satisfy an aesthetic preference.

- **Distinguish by lightness and the blue↔yellow axis, never by red↔green hue alone.** Red-green deficiency collapses the red-green direction but preserves lightness contrast and blue-yellow contrast. Two colors that differ only along red-green will merge for ~8% of male viewers.
- **Protanopia darkens reds.** Loss of the L-cone reduces the luminance of long-wavelength light, so saturated dark reds can nearly vanish as thin lines on white. Prefer the established palette's calibrated tones over ad-hoc reds.
- **Color is a secondary channel.** Meaning must also be carried by linestyle, marker, direct label, or spatial position. This also protects against grayscale printing and poor projectors.
- **A palette is only as safe as its worst pair.** Evaluate the *minimum* pairwise perceptual distance, not the average.
- **Theming is a layout concern, not a data concern.** Institutional identity is conveyed through poster chrome (§9); data colors answer only to accessibility.

---

## 3. Categorical palette (Okabe-Ito)

Use this pool for all categorical/qualitative data color. Lead with the high-contrast members; reserve pure yellow.

| Role priority | Color | Hex | White-bg notes |
|---|---|---|---|
| 1 | Black | `#000000` | Ideal for "total"/reference series |
| 2 | Vermillion | `#D55E00` | Strong on white; good for signal |
| 3 | Blue | `#0072B2` | Strong on white |
| 4 | Bluish green | `#009E73` | Good on white |
| 5 | Orange | `#E69F00` | Good on white |
| 6 | Reddish purple | `#CC79A7` | Medium contrast |
| 7 | Sky blue | `#56B4E9` | Light — thicken thin lines if faint |
| — | Yellow | `#F0E442` | **Do not use for thin lines on white** (fills/markers only) |

**Rationale for choosing this over the UH brand palette:** see Decision Log D1. In short, the UH palette's worst-pair floor collapsed to ΔE 6.0 under protanopia (purple/blue merge); Okabe-Ito holds ~14 (§8).

---

## 4. matplotlib / seaborn setup

```python
# file: poster_style.py
# Shared style + palette for all poster figures. Import and call apply_style() first.
import matplotlib as mpl
import seaborn as sns

OKABE_ITO = {
    "black":        "#000000",
    "vermillion":   "#D55E00",
    "blue":         "#0072B2",
    "bluish_green": "#009E73",
    "orange":       "#E69F00",
    "purple":       "#CC79A7",  # reddish purple
    "sky_blue":     "#56B4E9",
    "yellow":       "#F0E442",  # fills/markers only, never thin lines on white
}

# Default categorical order (high-contrast first; yellow excluded from the line cycle)
PALETTE = [OKABE_ITO[k] for k in
           ["black", "vermillion", "blue", "bluish_green", "orange", "purple", "sky_blue"]]

# Redundant linestyle cycle, paired positionally with PALETTE
LINESTYLES = ["-", "-", "--", ":", "-.", (0, (3, 1, 1, 1)), (0, (5, 2))]

SEQ_CMAP = "cividis"   # sequential: likelihood / density / localization maps
DIV_CMAP = "PuOr"      # diverging: signed residuals / asymmetries (or "RdBu")

def apply_style():
    mpl.rcParams.update({
        "font.family":      "DejaVu Sans",
        "figure.facecolor": "white",
        "axes.facecolor":   "white",
        "axes.edgecolor":   "#666666",
        "axes.grid":        True,
        "grid.alpha":       0.25,
        "axes.axisbelow":   True,
        "savefig.dpi":      300,
        "savefig.bbox":     "tight",
    })
    sns.set_palette(PALETTE)
```

Notes:
- The earlier custom `uh_green` / `uh_greengold` colormaps are **deprecated for quantitative maps** (not perceptually uniform; the diverging one places its ends on the wrong axis). Use `SEQ_CMAP` / `DIV_CMAP`.
- The Okabe-Ito pool is shared across both domains (data plots and the event display), but color→meaning assignments are made **per figure**; they need not match between the spectrum plot and the Geant4 render. Within each figure, follow the rules in §5 / §6.

---

## 5. Plot-type rules

### 5.1 Multi-line plots (spectra, time series) — strictest
- **Mandatory:** color **and** linestyle redundancy. Pair `PALETTE[i]` with `LINESTYLES[i]`.
- Reference/total series: black, solid, heaviest weight (`lw≈3`).
- Primary signal: vermillion, solid, bold — must remain the only bold solid colored curve.
- Backgrounds: dashed / dotted / dash-dot variants.
- Cap at ~6–7 series in one axes; beyond that, split the figure or use small multiples.
- Do not place the two closest-in-appearance colors on curves that overlap spatially.

Reference template (the verified IBD spectrum):

| Component | Color | Hex | Linestyle |
|---|---|---|---|
| Total model | black | `#000000` | solid, lw 3 |
| Reactor IBD signal | vermillion | `#D55E00` | solid, lw 2.4 |
| Accidental bkg | sky blue | `#56B4E9` | dashed |
| Fast-neutron bkg | bluish green | `#009E73` | dotted |
| Cosmogenic ⁹Li/⁸He | reddish purple | `#CC79A7` | dash-dot |
| ⁶Li correlated | blue | `#0072B2` | dash-dot-dot |

### 5.2 Categorical bar charts
- Direct text labels on/beside each bar make color **non-critical** for distinguishability. With direct labels, the full palette may be used freely and color becomes decorative.
- If bars are *not* directly labeled (color-keyed legend only), apply the §7 acceptance floor to the set of bar colors.

### 5.3 Heatmaps / 2D maps (localization likelihood, density)
- Sequential quantities: `cividis` (default) or `viridis`.
- Signed/diverging quantities: `PuOr` or `RdBu`. **Never** a red↔green diverging map.
- Always show the colorbar; if readers must read values off it, perceptual uniformity (cividis/viridis) is required.

---

## 6. Geant4 IBD event-display render

**Background:** white (`/vis/viewer/set/background white`). Matches the data plots, lets the darker Okabe-Ito tones and the black alpha read correctly.

**Particle → color mapping (fixed scheme):**

| Particle | Color | Hex | Reason |
|---|---|---|---|
| e⁺ (positron) | vermillion | `#D55E00` | warm, prompt; split from gamma across blue-yellow |
| γ (511 keV) | sky blue | `#56B4E9` | cool; co-located with e⁺ at annihilation → safe contrast |
| neutron | blue | `#0072B2` | cool "bridge"; darker than gamma by lightness |
| ³H (triton) | orange | `#E69F00` | warm; max-separated from neutron at capture vertex |
| α | black | `#000000` | heavy ionization; CVD-invariant; anchors the capture vertex |
| ν̄ₑ guide | grey, dashed | `#BBBBBB` | annotation only — not a real trajectory |

**Design logic (co-location, not legend separation):**
- *Prompt vertex* (e⁺ + its annihilation γ overlap): warm/cool split, never two warm tones.
- *Capture vertex* (neutron track ends where triton + alpha begin — the most crowded point): blue / orange / black = the three most-separated options; black alpha anchors it under every CVD type.
- The only smallest gap (e⁺ vs triton, both warm) falls between particles at **different vertices**, separated in space and time — lowest-risk place for the smallest gap.

**Vis macro:**

```
# file: vis_ibd_colors.mac
/vis/viewer/set/background white
/vis/modeling/trajectories/create/drawByParticleID ibd
/vis/modeling/trajectories/ibd/set e+      0xD55E00
/vis/modeling/trajectories/ibd/set gamma   0x56B4E9
/vis/modeling/trajectories/ibd/set neutron 0x0072B2
/vis/modeling/trajectories/ibd/set triton  0xE69F00
/vis/modeling/trajectories/ibd/set alpha   0x000000
/vis/modeling/trajectories/ibd/setDefault  0xBBBBBB
/vis/modeling/trajectories/select ibd
```

**Implementation notes:**
- If the build rejects hex, use `set <particle> setRGBA r g b a` (0–1 floats), e.g. `setRGBA e+ 0.835 0.369 0.000 1.0`.
- The antineutrino has no trajectory (gone before tracking). Composite its incoming dashed line into the figure in post.
- Sky blue is the lightest track color; if 511 keV γ tracks look faint on white, increase the model line width. Compton-scattered γ tracks are usually short regardless.
- No bulk image-editor recolor is needed: `drawByParticleID` assigns unique colors at the source, and triton/alpha are intrinsically sub-mm heavy stubs vs the neutron's long kinked path — track **morphology** backs up the color before hue is even read.

---

## 7. Verification protocol

Run this whenever a figure's set of co-displayed colors changes (new series, recolor, new categorical set, new particle).

```python
# file: check_cvd.py
# Worst-pair perceptual-distance check under simulated color vision deficiency.
# pip install colorspacious  (add --break-system-packages on managed Python)
import itertools, numpy as np
from colorspacious import cspace_convert, deltaE

CVDS = {"deuteranopia": "deuteranomaly",
        "protanopia":   "protanomaly",
        "tritanopia":   "tritanomaly"}

def _hex2rgb(h): return np.array([int(h[i:i+2], 16) for i in (1, 3, 5)]) / 255.0
def _sim(rgb, cvd):
    return np.clip(cspace_convert(rgb, {"name": "sRGB1+CVD", "cvd_type": cvd,
                                        "severity": 100}, "sRGB1"), 0, 1)

def worst_pair(palette_hex, cvd=None):
    """Minimum pairwise CAM02-UCS distance across a palette (its safety floor)."""
    cols = [_hex2rgb(h) for h in palette_hex]
    if cvd:
        cols = [_sim(c, cvd) for c in cols]
    return min(deltaE(a, b, input_space="sRGB1", uniform_space="CAM02-UCS")
               for a, b in itertools.combinations(cols, 2))

def report(palette_hex):
    rows = {"normal": worst_pair(palette_hex)}
    rows.update({k: worst_pair(palette_hex, v) for k, v in CVDS.items()})
    return rows

# Visual confirmation: render the figure to an RGB array (fig.canvas.buffer_rgba),
# then apply _sim(...) to the whole image array for each cvd type and display
# a 2x2 grid (normal + 3 CVD). Inspect that co-located elements remain distinct.
```

**Acceptance criteria:**
- Worst-pair floor of any co-displayed color set: **ΔE > 12 under both deuteranopia and protanopia.** (6–12 is acceptable only when a redundant non-color channel separates the pair; < 6 fails.)
- For the event display, the smallest gap is permitted only between particles at *different vertices*. Co-located particle pairs must exceed the floor.
- Plus a visual pass: render the 4-way CVD simulation of the actual figure and confirm no co-located elements merge.

---

## 8. Verified results (measured, severity 100)

Worst-pair floor (minimum pairwise ΔE, CAM02-UCS):

| Palette | Normal | Deuteranopia | Protanopia | Tritanopia |
|---|---|---|---|---|
| UH brand (7) — rejected | 15.7 | 10.1 | **6.0** | 11.8 |
| Okabe-Ito (7) — adopted | 21.6 | 14.8 | **14.0** | 11.0 |
| IBD particles (5) | 21.6 | 15.2 | 20.2 | 18.9 |

Notes: Okabe-Ito's tritanopia floor (11.0) is marginally below the UH palette's — an accepted trade, since tritanopia is ~0.01% prevalence vs ~8% for red-green. The IBD particle floor's binding pair is e⁺ vs triton (separated vertices).

---

## 9. UH theming (chrome only)

Permitted **only** in non-data poster elements: title bar, section rules, header bands, the event-display panel frame. Never in data marks, lines, bars, or colormaps.

| Element | Color | Hex |
|---|---|---|
| Mānoa Green (primary chrome) | dark green | `#024731` |
| UH System Gold (accent) | gold | `#B3995D` |
| Kelly Green (secondary) | green | `#009A44` |

---

## 10. Environment

- Python: `matplotlib`, `seaborn`, `colorspacious` (`pip install colorspacious`; add `--break-system-packages` on externally managed interpreters).
- Geant4 with an OpenGL (or equivalent) visualization driver for the vis macro.

---

## 11. Decision log

- **D1 — Categorical palette: UH brand → Okabe-Ito.** UH palette's protanopia worst-pair floor was ΔE 6.0 (purple/blue merge; gold/orange/red warm cluster collapses). Okabe-Ito is purpose-built for red-green safety and holds ~14. Accessibility prioritized over theming per stakeholder direction.
- **D2 — Event display: dark background + gold gamma → white background + Okabe-Ito.** Gold gamma was a theming flourish and created a warm/warm collision with the positron at the annihilation vertex. White background unifies the poster and supports the darker, white-safe palette tones plus a black alpha.
- **D3 — Approved alternative palette: Paul Tol "bright."** If a physicist-authored citation is preferred for the methods/caption, Tol's qualitative sets are acceptable; re-run §7 if substituted.
- **D4 — Colormaps: custom green ramps deprecated for quantitative use.** Replaced by cividis (sequential) and PuOr/RdBu (diverging).
- **D5 — Redundancy mandated.** Multi-line figures must encode meaning in linestyle as well as color (CVD + grayscale + projector robustness).

---

## 12. Out of scope

Poster layout and typography, figure content/physics, LaTeX/Overleaf structure, and data analysis. This document governs color and color-accessibility only.
