"""Golden Gate wallpaper: the bridge at sunset with fog rolling under the deck.

Usage: python3 -I extras/make-wallpaper.py backgrounds/golden-gate-sunset.jpg
"""
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 3840, 2160
HORIZON = 0.70
y, x = np.mgrid[0:H, 0:W].astype(np.float32)
u, v = x / W, y / H
rng = np.random.default_rng(1937)


def hexc(h):
    h = h.lstrip('#'); return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], np.float32) / 255


def ramp(t, stops):
    """Piecewise-linear colour ramp over (position, hex) stops."""
    t = np.clip(t, 0, 1)
    out = np.zeros(t.shape + (3,), np.float32)
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        k = np.clip((t - p0) / (p1 - p0), 0, 1)[..., None]
        inside = ((t >= p0) & (t <= p1))[..., None]
        out = np.where(inside, hexc(c0) + (hexc(c1) - hexc(c0)) * k, out)
    return out


def over(img, color, alpha):
    a = np.clip(alpha, 0, 1)[..., None]
    return img * (1 - a) + color * a


def ridge(xs, base, parts):
    return base + sum(a * np.sin(2 * np.pi * f * xs + p) for a, f, p in parts)


# Sky: deep Pacific night overhead, warming through violet into a gold horizon.
sky = ramp(v / HORIZON, [(0.0, '0b1430'), (0.35, '23285a'), (0.62, '6b3f6e'),
                          (0.82, 'd0663f'), (0.94, 'f39a4c'), (1.0, 'ffc777')])
sun_x, sun_y = 0.30, HORIZON - 0.035
d_sun = np.sqrt(((u - sun_x) * W / H) ** 2 + (v - sun_y) ** 2)
sky = sky + hexc('ffb45e') * (np.exp(-(d_sun / 0.16) ** 2) * 0.55)[..., None]
sky = sky + hexc('ff8a3d') * (np.exp(-(d_sun / 0.45) ** 2) * 0.22)[..., None]
sky = over(sky, hexc('fff1cf'), np.clip((0.034 - d_sun) / 0.004, 0, 1))
img = sky

# Water below the horizon: dark teal-navy with a broken sun path.
wv = np.clip((v - HORIZON) / (1 - HORIZON), 0, 1)
water = ramp(wv, [(0.0, '5b3a52'), (0.25, '1d2443'), (1.0, '070a17')])
ripple = (np.sin(v * H * 0.45 + np.sin(u * 53) * 4) * np.sin(u * W * 0.03 + v * 140)) > 0.6
path = np.exp(-((u - sun_x) / (0.035 + wv * 0.12)) ** 2) * (1 - wv) ** 1.5
water = water + hexc('ffb060') * (path * ripple * 0.75 + path * 0.12)[..., None]
img = np.where((v > HORIZON)[..., None], water, img)

# Distant ranges: East Bay haze on the left, Marin Headlands rising on the right.
far = ridge(u, HORIZON - 0.03, [(0.008, 3.1, 0.3), (0.004, 7.7, 1.9), (0.002, 17, 0.4)])
img = over(img, hexc('7a4a63'), np.clip((v - far) * H / 2, 0, 1) * (v <= HORIZON) * 0.85)
marin = ridge(u, HORIZON + 0.02 - np.clip((u - 0.55) / 0.45, 0, 1) ** 1.6 * 0.24,
              [(0.010, 2.3, 0.8), (0.005, 6.1, 2.6), (0.0025, 15, 1.1)])
marin_col = ramp((v - marin) / 0.2, [(0.0, '3a2a4a'), (1.0, '15132a')])
img = over(img, marin_col, np.clip((v - marin) * H / 2, 0, 1) * (u > 0.5) * np.clip((HORIZON + 0.004 - v) * H / 6, 0, 1))

# The bridge, drawn at 2x and downsampled for clean anti-aliasing.
S = 2
BW, BH = W * S, H * S
deck_y = 0.615
towers = [(0.305, 0.215), (0.735, 0.255)]   # (x, top y): the far tower sits a touch lower
tw = 0.0105                                   # leg width
bridge = Image.new('L', (BW, BH), 0)
draw = ImageDraw.Draw(bridge)
P = lambda px, py: (px * BW, py * BH)


def cable_y(px):
    (x0, t0), (x1, t1) = towers
    if px < x0:   # side span down to the San Francisco anchorage
        k = (x0 - px) / (x0 + 0.02); return t0 + 0.012 + (deck_y - 0.02 - t0) * k ** 0.85
    if px > x1:   # side span down to the Marin anchorage
        k = (px - x1) / (1.02 - x1); return t1 + 0.012 + (deck_y - 0.02 - t1) * k ** 0.85
    k = (px - x0) / (x1 - x0)
    top = t0 + (t1 - t0) * k + 0.012
    return top + (deck_y - 0.018 - top) * (1 - (2 * k - 1) ** 2)


# Suspender cables, then the main cable on top of them.
for px in np.arange(-0.02, 1.02, 0.0062):
    if any(abs(px - tx) < tw * 1.6 for tx, _ in towers):
        continue
    draw.line([P(px, cable_y(px)), P(px, deck_y)], fill=150, width=max(1, int(1.6 * S)))
xs = np.linspace(-0.02, 1.02, 1600)
draw.line([P(px, cable_y(px)) for px in xs], fill=255, width=int(6 * S), joint='curve')

# Towers: two tapering legs, Art Deco portal struts, stepped tops.
for tx, top in towers:
    base = 0.73
    for side in (-1, 1):
        cx_top, cx_base = tx + side * tw * 0.85, tx + side * tw * 1.05
        hw_top, hw_base = tw * 0.38, tw * 0.5
        draw.polygon([P(cx_top - hw_top, top), P(cx_top + hw_top, top),
                      P(cx_base + hw_base, base), P(cx_base - hw_base, base)], fill=255)
        draw.rectangle([P(cx_top - hw_top * 0.7, top - 0.012), P(cx_top + hw_top * 0.7, top)], fill=255)
    for k, sy in enumerate(np.linspace(top + 0.02, deck_y - 0.03, 4)):
        h = 0.016 if k == 0 else 0.011
        draw.rectangle([P(tx - tw * 1.25, sy), P(tx + tw * 1.25, sy + h)], fill=255)

# Deck with a stiffening truss below it.
draw.rectangle([P(-0.02, deck_y), P(1.02, deck_y + 0.010)], fill=255)
draw.rectangle([P(-0.02, deck_y + 0.010), P(1.02, deck_y + 0.022)], fill=170)
for px in np.arange(-0.02, 1.02, 0.004):
    draw.line([P(px, deck_y + 0.010), P(px + 0.004, deck_y + 0.022)], fill=255, width=S)
# Approach piers on the Marin side.
for px in np.arange(0.80, 1.02, 0.045):
    draw.rectangle([P(px - 0.003, deck_y + 0.02), P(px + 0.003, HORIZON + 0.02)], fill=255)

bmask = np.asarray(bridge.resize((W, H), Image.LANCZOS), np.float32) / 255
# International Orange, darkened where it faces away from the sun, rim-lit near it.
lit = np.exp(-((u - sun_x) / 0.22) ** 2)
bcol = ramp(v / HORIZON, [(0.25, 'a8402c'), (0.8, '8a2f22'), (1.0, '4a1a18')])
bcol = bcol + hexc('ff9a50')[None, None] * (lit * 0.25)[..., None]
img = over(img, bcol, bmask)

# Reflection of the bridge, broken up by the ripples.
refl_rows = np.clip((2 * HORIZON - v) * H, 0, H - 1).astype(np.int32)
refl = bmask[refl_rows, x.astype(np.int32)] * (v > HORIZON)
img = over(img, hexc('3c1b24'), refl * 0.4 * (1 - wv) ** 2 * (0.5 + 0.5 * ripple))

# Fog: Karl the Fog pouring through the strait under the deck, plus a high haze.
def fbm(scale, octaves, seed):
    acc = np.zeros((H, W), np.float32)
    r = np.random.default_rng(seed)
    for o in range(octaves):
        n = Image.fromarray((r.random((max(2, int(H / scale * 2 ** o)), max(2, int(W / scale * 2 ** o)))) * 255).astype(np.uint8))
        acc += np.asarray(n.resize((W, H), Image.BICUBIC), np.float32) / 255 / 2 ** o
    return acc / (2 - 2 ** (1 - octaves))


noise = fbm(260, 5, 7)
fog_top = deck_y + 0.012 + 0.025 * np.sin(u * 9 + 1.3) + 0.03 * (noise - 0.5)
fog = np.clip((v - fog_top) / 0.05, 0, 1) * np.clip((HORIZON + 0.06 - v) / 0.08, 0, 1)
fog *= np.clip(0.55 + (noise - 0.5) * 1.6, 0, 1) * np.clip(1.25 - np.abs(u - 0.62) * 1.4, 0, 1)
fog_col = ramp(u, [(0.0, 'f2b98c'), (0.35, 'eac3a6'), (1.0, 'a99ab0')])
img = over(img, fog_col, fog * 0.85)
haze = np.exp(-((v - 0.47) / 0.06) ** 2) * np.clip(noise - 0.35, 0, 1) * 0.35
img = over(img, hexc('e7a07a'), haze)

# A few early stars in the deep sky.
stars = (rng.random((H, W)) > 0.99965) & (v < 0.3)
img = over(img, hexc('ffffff'), stars * (0.3 + 0.7 * (1 - v / 0.3)) * rng.random((H, W)))

# Vignette, a soft bloom, and dither against banding.
vig = 1 - 0.4 * (((u - 0.5) * 1.15) ** 2 + ((v - 0.5) * 1.3) ** 2)
img = img * np.clip(vig, 0.55, 1)[..., None]
out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
bloom = np.asarray(out.filter(ImageFilter.GaussianBlur(24)), np.float32) / 255
img = 1 - (1 - img) * (1 - bloom * 0.12)
img = img + (rng.random(img.shape, dtype=np.float32) - 0.5) / 255
Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(sys.argv[1], quality=93, subsampling=0)
