"""Okabe-Ito colourblind-safe palette and the segment-size -> colour mapping
used across the directionality plots, replacing the old red/green/blue mapping.

Reference: Okabe & Ito (2008), "Color Universal Design (CUD)". The eight colours
are distinguishable for viewers with deuteranopia, protanopia, and tritanopia.
"""

# Okabe-Ito 8-colour qualitative palette.
OKABE_ITO = {
    "black":          "#000000",
    "orange":         "#E69F00",
    "sky_blue":       "#56B4E9",
    "bluish_green":   "#009E73",
    "yellow":         "#F0E442",
    "blue":           "#0072B2",
    "vermillion":     "#D55E00",
    "reddish_purple": "#CC79A7",
}

# Segment size (mm) -> colour. Warm->cool ordering preserved from the old
# red/green/blue mapping, but colourblind-safe (vermillion / bluish-green / blue).
SEG_COLOR = {
    5:   OKABE_ITO["vermillion"],    # was red
    50:  OKABE_ITO["bluish_green"],  # was green
    150: OKABE_ITO["blue"],          # was blue
}
