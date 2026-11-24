#!/usr/bin/env python3
"""BerkiOS wallpaper generator.

Regenerates the 1920x1080 berkiOS wallpaper (violet gradient #8A5CFF ->
#4A1FD0 with soft light blobs and white "berkiOS" text) into both places
the build needs it:
  - branding/wallpaper.png (preview / reference copy)
  - config/includes.chroot/usr/share/backgrounds/berkios.png (copied into
    the live ISO by live-build)

Run from anywhere; paths are resolved relative to this script. No Apple
artwork is used. Requires Pillow (python3-pil).
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH, HEIGHT = 1920, 1080
TOP = (0x8A, 0x5C, 0xFF)      # #8A5CFF
BOTTOM = (0x4A, 0x1F, 0xD0)    # #4A1FD0

ROOT = Path(__file__).resolve().parent.parent
TARGETS = [
    ROOT / "branding" / "wallpaper.png",
    ROOT / "config" / "includes.chroot" / "usr" / "share" / "backgrounds" / "berkios.png",
]


def gradient() -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT))
    d = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        r = round(TOP[0] + (BOTTOM[0] - TOP[0]) * t)
        g = round(TOP[1] + (BOTTOM[1] - TOP[1]) * t)
        b = round(TOP[2] + (BOTTOM[2] - TOP[2]) * t)
        d.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    return img


def add_blobs(img: Image.Image) -> Image.Image:
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # Soft light blobs, like macOS-style wallpaper glow.
    d.ellipse([1100, -260, 2100, 620], fill=(255, 255, 255, 46))
    d.ellipse([-320, 560, 700, 1250], fill=(255, 255, 255, 34))
    d.ellipse([700, 700, 1500, 1300], fill=(255, 210, 90, 26))
    layer = layer.filter(ImageFilter.GaussianBlur(140))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def add_text(img: Image.Image) -> Image.Image:
    d = ImageDraw.Draw(img)
    size = 150
    font = None
    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    ):
        try:
            font = ImageFont.truetype(candidate, size)
            break
        except OSError:
            continue
    if font is None:  # last resort: Pillow's built-in bitmap font
        font = ImageFont.load_default()
    text = "berkiOS"
    box = d.textbbox((0, 0), text, font=font)
    x = (WIDTH - (box[2] - box[0])) // 2 - box[0]
    y = (HEIGHT - (box[3] - box[1])) // 2 - box[1]
    d.text((x, y), text, font=font, fill=(255, 255, 255))
    return img


def main() -> None:
    img = add_text(add_blobs(gradient()))
    for target in TARGETS:
        target.parent.mkdir(parents=True, exist_ok=True)
        img.save(target, "PNG")
        print(f"wrote {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
