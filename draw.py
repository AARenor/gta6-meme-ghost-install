from math import cos, hypot, pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SIZE = 1024
SCALE = 3
SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

Color = tuple[int, int, int]
Point = tuple[float, float]


def point(x: float, y: float) -> tuple[int, int]:
    return round(x * SCALE), round(y * SCALE)


def box(x0: float, y0: float, x1: float, y1: float) -> tuple[int, int, int, int]:
    return round(x0 * SCALE), round(y0 * SCALE), round(x1 * SCALE), round(y1 * SCALE)


def mix(start: Color, end: Color, fraction: float) -> Color:
    return (
        round(start[0] + (end[0] - start[0]) * fraction),
        round(start[1] + (end[1] - start[1]) * fraction),
        round(start[2] + (end[2] - start[2]) * fraction),
    )


def draw_background(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image)
    top = (42, 14, 74)
    middle = (122, 27, 107)
    bottom = (244, 100, 60)
    for y in range(761 * SCALE):
        position = y / SCALE
        if position <= 420:
            color = mix(top, middle, position / 420)
        else:
            color = mix(middle, bottom, min((position - 420) / 340, 1))
        draw.line((0, y, SIZE * SCALE - 1, y), fill=color)

    draw.rectangle(box(0, 761, SIZE, SIZE), fill=(90, 20, 80))

    ripple_color = (145, 51, 104)
    for y, left, right in ((800, 242, 786), (840, 305, 733), (880, 235, 795)):
        ripple = [
            point(left, y),
            point(left + (right - left) * 0.25, y - 2),
            point(left + (right - left) * 0.5, y + 1),
            point(left + (right - left) * 0.75, y - 2),
            point(right, y),
        ]
        draw.line(ripple, fill=ripple_color, width=3 * SCALE, joint="curve")

    draw.ellipse(
        box(362, 550, 662, 850),
        fill=(255, 179, 107),
        outline=(255, 214, 160),
        width=6 * SCALE,
    )


def bezier(start: Point, control1: Point, control2: Point, end: Point) -> list[Point]:
    points: list[Point] = []
    for step in range(41):
        t = step / 40
        u = 1 - t
        points.append(
            (
                u**3 * start[0]
                + 3 * u**2 * t * control1[0]
                + 3 * u * t**2 * control2[0]
                + t**3 * end[0],
                u**3 * start[1]
                + 3 * u**2 * t * control1[1]
                + 3 * u * t**2 * control2[1]
                + t**3 * end[1],
            )
        )
    return points


def frond(start: Point, end: Point, width: float) -> list[Point]:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = hypot(dx, dy)
    middle_x = (start[0] + end[0]) / 2
    middle_y = (start[1] + end[1]) / 2
    return [
        (
            middle_x + dx / 2 * cos(angle) - dy / length * width / 2 * sin(angle),
            middle_y + dy / 2 * cos(angle) + dx / length * width / 2 * sin(angle),
        )
        for angle in (2 * pi * step / 64 for step in range(64))
    ]


def draw_palms(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image)
    trunk = bezier((20, 900), (28, 800), (34, 590), (34, 470)) + bezier(
        (46, 470), (49, 590), (55, 800), (64, 900)
    )
    fronds = [
        frond((40, 470), end, width)
        for end, width in (
            ((1, 420), 12),
            ((8, 386), 12),
            ((30, 375), 12),
            ((59, 377), 12),
            ((79, 402), 12),
            ((87, 438), 12),
        )
    ]
    for mirrored in (False, True):
        for shape in (trunk, *fronds):
            points = [point(SIZE - x if mirrored else x, y) for x, y in shape]
            draw.polygon(points, fill=(0, 0, 0))


def draw_panel(image: Image.Image) -> None:
    ImageDraw.Draw(image).rounded_rectangle(
        box(96, 120, 928, 600), radius=28 * SCALE, fill=(18, 7, 27, 255)
    )
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle(
        box(96, 120, 928, 600),
        radius=28 * SCALE,
        fill=(18, 7, 27, 240),
        outline=(255, 61, 154, 255),
        width=4 * SCALE,
    )
    image.alpha_composite(layer)

    draw = ImageDraw.Draw(image)
    title_font = ImageFont.truetype(SERIF_BOLD, 46 * SCALE)
    vi_font = ImageFont.truetype(SERIF_BOLD, 150 * SCALE)

    draw.text(
        point(512, 168),
        "GRAND THEFT AUTO",
        font=title_font,
        fill=(255, 217, 236),
        anchor="mt",
    )

    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).text(
        point(518, 238), "VI", font=vi_font, fill=(255, 140, 200, 102), anchor="mt"
    )
    image.alpha_composite(glow)
    draw.text(point(512, 232), "VI", font=vi_font, fill=(255, 61, 154), anchor="mt")


def draw_foreground(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image)
    tagline_font = ImageFont.truetype(SANS_BOLD, 30 * SCALE)
    percentage_font = ImageFont.truetype(SANS_BOLD, 22 * SCALE)
    remaining_font = ImageFont.truetype(SANS_BOLD, 34 * SCALE)

    draw.text(
        point(512, 420),
        "13 YEARS WAITING. DAY 3 INSTALLING.",
        font=tagline_font,
        fill=(191, 179, 214),
        anchor="mt",
        stroke_width=2 * SCALE,
        stroke_fill=(16, 12, 20),
    )
    draw.rounded_rectangle(
        box(176, 458, 848, 484), radius=13 * SCALE, fill=(52, 32, 72)
    )
    draw.rounded_rectangle(
        box(176, 458, 820, 484), radius=13 * SCALE, fill=(255, 61, 154)
    )
    draw.text(
        point(820, 458),
        "99%",
        font=percentage_font,
        fill=(255, 217, 236),
        anchor="mt",
        stroke_width=2 * SCALE,
        stroke_fill=(16, 12, 20),
    )
    draw.text(
        point(512, 512),
        "13 YEARS REMAINING",
        font=remaining_font,
        fill=(255, 214, 160),
        anchor="mt",
        stroke_width=2 * SCALE,
        stroke_fill=(16, 12, 20),
    )


def sparkle(cx: float, cy: float) -> list[tuple[int, int]]:
    return [
        point(cx + x, cy + y)
        for x, y in (
            (0, -17),
            (4, -4),
            (17, 0),
            (4, 4),
            (0, 17),
            (-4, 4),
            (-17, 0),
            (-4, -4),
        )
    ]


def draw_ghost(image: Image.Image) -> None:
    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse(box(690, 860, 910, 906), fill=(10, 5, 15, 153))
    image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(6 * SCALE)))

    draw = ImageDraw.Draw(image)
    head = [
        point(800 + 95 * cos(pi + pi * step / 96), 700 + 95 * sin(pi + pi * step / 96))
        for step in range(97)
    ]
    hem = [
        point(895 - 190 * step / 120, 873 + 7 * cos(10 * pi * step / 120))
        for step in range(121)
    ]
    contour = [*head, *hem]
    draw.polygon(contour, fill=(255, 255, 255))
    draw.line(
        [*contour, contour[0]], fill=(16, 12, 20), width=8 * SCALE, joint="curve"
    )
    draw.polygon(sparkle(770, 690), fill=(16, 12, 20))
    draw.polygon(sparkle(830, 690), fill=(16, 12, 20))

    draw.ellipse(
        box(883, 728, 967, 812),
        fill=(226, 0, 126),
        outline=(16, 12, 20),
        width=6 * SCALE,
    )
    star = []
    for step in range(10):
        angle = -pi / 2 + step * pi / 5
        radius = 22 if step % 2 == 0 else 9
        star.append(point(925 + radius * cos(angle), 770 + radius * sin(angle)))
    draw.polygon(star, fill=(255, 255, 255))
    draw.ellipse(
        box(870, 740, 910, 780),
        fill=(255, 255, 255),
        outline=(16, 12, 20),
        width=8 * SCALE,
    )


def draw_footer(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image)
    brand_font = ImageFont.truetype(SANS_BOLD, 40 * SCALE)
    slogan_font = ImageFont.truetype(SANS, 22 * SCALE)
    brand = "make.fun"
    slogan = "people and their agents earn money here"
    brand_box = draw.textbbox((0, 0), brand, font=brand_font, anchor="lt")
    slogan_box = draw.textbbox((0, 0), slogan, font=slogan_font, anchor="lt")
    brand_height = brand_box[3] - brand_box[1]
    slogan_height = slogan_box[3] - slogan_box[1]
    slogan_x = 64 * SCALE + round(draw.textlength(brand, font=brand_font)) + 12 * SCALE
    slogan_y = 960 * SCALE + (brand_height - slogan_height) // 2
    draw.text(point(64, 960), brand, font=brand_font, fill=(255, 255, 255), anchor="lt")
    draw.text(
        (slogan_x, slogan_y), slogan, font=slogan_font, fill=(255, 200, 230), anchor="lt"
    )


def main() -> None:
    image = Image.new("RGBA", (SIZE * SCALE, SIZE * SCALE), (90, 20, 80, 255))
    draw_background(image)
    draw_palms(image)
    draw_panel(image)
    draw_foreground(image)
    draw_ghost(image)
    draw_footer(image)
    image = image.convert("RGB").resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    output = Path(__file__).resolve().with_name("meme.png")
    image.save(output, format="PNG", optimize=True)
    print(output.stat().st_size)


if __name__ == "__main__":
    main()
