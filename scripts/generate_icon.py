"""
Script tạo icon FaceBox.ico đa kích thước cho ứng dụng Windows.
Thiết kế theo chuẩn Industrial Smart Locker:
- Máy ảnh phẳng màu vàng #FFD500, viền đen #171717.
- Ống kính tròn màu đen #171717.
- Bên trong ống kính là hộp kiện hàng vuông vức màu vàng #FFD500 có băng dính chữ thập viền đen.
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "assets"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ICO_PATH = OUTPUT_DIR / "FaceBox.ico"
PNG_PATH = OUTPUT_DIR / "FaceBox.png"


def draw_facebox_logo(size: int = 512) -> Image.Image:
    """Vẽ logo FaceBox ở độ phân giải cao với alpha channel."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    yellow = "#FFD500"
    dark = "#171717"
    line_w = max(2, int(size * 0.035))

    # Tọa độ thân máy ảnh
    # Thân máy ảnh chiếm ~86% width, ~65% height
    body_w = int(size * 0.88)
    body_h = int(size * 0.65)
    body_x = int((size - body_w) / 2)
    body_y = int(size * 0.26)

    # 1. Gờ ống ngắm phía trên (Bump)
    bump_w = int(size * 0.28)
    bump_h = int(size * 0.12)
    bump_x = int((size - bump_w) / 2)
    bump_y = int(size * 0.14)
    draw.rounded_rectangle(
        [bump_x, bump_y, bump_x + bump_w, body_y + line_w],
        radius=int(size * 0.02),
        fill=yellow,
        outline=dark,
        width=line_w
    )

    # 2. Thân máy ảnh chính (vàng, viền đen)
    draw.rounded_rectangle(
        [body_x, body_y, body_x + body_w, body_y + body_h],
        radius=int(size * 0.03),
        fill=yellow,
        outline=dark,
        width=line_w
    )

    # Đèn flash nhỏ góc phải
    flash_w = int(size * 0.12)
    flash_h = int(size * 0.07)
    flash_x = body_x + body_w - flash_w - int(size * 0.07)
    flash_y = body_y + int(size * 0.07)
    draw.rectangle(
        [flash_x, flash_y, flash_x + flash_w, flash_y + flash_h],
        fill=dark
    )

    # 3. Ống kính máy ảnh (vòng tròn màu đen)
    cx = size // 2
    cy = body_y + body_h // 2
    lens_r = int(body_h * 0.38)
    draw.ellipse(
        [cx - lens_r, cy - lens_r, cx + lens_r, cy + lens_r],
        fill=dark,
        outline=dark,
        width=line_w
    )

    # 4. Hộp kiện hàng hình vuông (Square Package Box) bên trong ống kính
    box_size = int(lens_r * 1.05)
    half = box_size // 2
    bx0 = cx - half
    by0 = cy - half
    bx1 = cx + half
    by1 = cy + half

    box_line_w = max(1, int(size * 0.022))
    draw.rectangle(
        [bx0, by0, bx1, by1],
        fill=yellow,
        outline=dark,
        width=box_line_w
    )

    # Đường băng keo chữ thập kiện hàng
    # Đường dọc giữa
    draw.line([(cx, by0), (cx, by1)], fill=dark, width=box_line_w)
    # Đường ngang nắp hộp
    seam_y = cy - int(box_size * 0.15)
    draw.line([(bx0, seam_y), (bx1, seam_y)], fill=dark, width=box_line_w)

    return img


def generate_icons():
    print("Đang tạo icon FaceBox...")
    base_img = draw_facebox_logo(512)

    # Lưu bản PNG 256x256
    png_img = base_img.resize((256, 256), Image.Resampling.LANCZOS)
    png_img.save(PNG_PATH, format="PNG")
    print(f"✓ Đã lưu PNG: {PNG_PATH}")

    # Tạo ICO chứa đầy đủ kích thước Windows (16, 32, 48, 64, 128, 256)
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    base_img.save(
        ICO_PATH,
        format="ICO",
        sizes=icon_sizes
    )
    print(f"✓ Đã lưu ICO: {ICO_PATH}")


if __name__ == "__main__":
    generate_icons()

