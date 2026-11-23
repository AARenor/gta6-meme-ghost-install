from math import cos, pi, sin
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

SIZE = 1024
SCALE = 3
CANVAS = (SIZE * SCALE, SIZE * SCALE)
FONT_DIR = Path('/usr/share/fonts/truetype/dejavu')
BLACK = (24, 20, 16, 255)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = 'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'
    return ImageFont.truetype(str(FONT_DIR / name), size * SCALE)


def scaled_box(box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    left, top, right, bottom = box
    return left * SCALE, top * SCALE, right * SCALE, bottom * SCALE


def text_line(
    layer: Image.Image,
    text: str,
    size: int,
    y: int,
    center: int,
    width: int,
    color: tuple[int, int, int, int] = BLACK,
    bold: bool = False,
) -> None:
    face = font(size, bold)
    bounds = face.getbbox(text)
    text_width = bounds[2] - bounds[0]
    text_height = bounds[3] - bounds[1]
    line = Image.new('RGBA', (text_width + SCALE * 2, text_height + SCALE * 2))
    ImageDraw.Draw(line).text(
        (SCALE - bounds[0], SCALE - bounds[1]), text, font=face, fill=color
    )
    if line.width > width * SCALE:
        line = line.resize((width * SCALE, line.height), Image.Resampling.LANCZOS)
    layer.alpha_composite(line, (center * SCALE - line.width // 2, y * SCALE))


def star(cx: int, cy: int, outer: int, inner: int, points: int) -> list[tuple[int, int]]:
    return [
        (
            round((cx + (outer if i % 2 == 0 else inner) * cos(-pi / 2 + i * pi / points)) * SCALE),
            round((cy + (outer if i % 2 == 0 else inner) * sin(-pi / 2 + i * pi / points)) * SCALE),
        )
        for i in range(points * 2)
    ]


def render() -> Image.Image:
    image = Image.new('RGBA', CANVAS, (30, 22, 34, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle(scaled_box((0, 700, 1024, 1024)), fill=(60, 38, 26, 255))
    draw.line([(0, 702 * SCALE), (1024 * SCALE, 702 * SCALE)], fill=(83, 51, 33, 255), width=3 * SCALE)
    draw.line([(0, 918 * SCALE), (1024 * SCALE, 918 * SCALE)], fill=(53, 32, 23, 255), width=2 * SCALE)

    neon = Image.new('RGBA', CANVAS)
    nd = ImageDraw.Draw(neon)
    nd.line([(155 * SCALE, 66 * SCALE), (869 * SCALE, 66 * SCALE)], fill=(241, 61, 185, 125), width=16 * SCALE)
    image.alpha_composite(neon.filter(ImageFilter.GaussianBlur(14 * SCALE)))
    draw = ImageDraw.Draw(image)
    draw.line([(155 * SCALE, 66 * SCALE), (869 * SCALE, 66 * SCALE)], fill=(255, 94, 201, 255), width=5 * SCALE)
    draw.line([(155 * SCALE, 66 * SCALE), (869 * SCALE, 66 * SCALE)], fill=(255, 213, 241, 255), width=2 * SCALE)

    ticket = Image.new('RGBA', CANVAS)
    td = ImageDraw.Draw(ticket)
    points = [(110, 120), (914, 120), (914, 750)]
    points.extend((x, 760 if (914 - x) // 16 % 2 == 0 else 750) for x in range(914, 109, -16))
    points.append((110, 120))
    polygon = [(x * SCALE, y * SCALE) for x, y in points]
    td.polygon(polygon, fill=(247, 240, 224, 255))
    td.line(polygon, fill=(120, 104, 86, 255), width=3 * SCALE, joint='curve')
    td.line([(150 * SCALE, 270 * SCALE), (874 * SCALE, 270 * SCALE)], fill=BLACK, width=2 * SCALE)
    td.line([(150 * SCALE, 610 * SCALE), (708 * SCALE, 610 * SCALE)], fill=BLACK, width=2 * SCALE)

    text = Image.new('RGBA', CANVAS)
    text_line(text, 'VICE CITY PAWN & LOAN', 40, 190, 512, 720, bold=True)
    text_line(text, 'TICKET No. 13', 26, 240, 512, 700, (110, 96, 80, 255))
    text_line(text, 'PAWNED:', 30, 310, 512, 700, bold=True)
    text_line(text, '13 YEARS OF MY LIFE', 62, 365, 512, 720, bold=True)
    text_line(text, 'BOUGHT BACK BY MY AGENT', 44, 470, 512, 720, bold=True)
    text_line(text, "it earned the game's price", 30, 540, 420, 560, (40, 34, 28, 255))
    text_line(text, 'on make.fun while I waited', 30, 576, 420, 560, (40, 34, 28, 255))

    footer = Image.new('RGBA', CANVAS)
    fd = ImageDraw.Draw(footer)
    first = font(34, True)
    second = font(22)
    first_width = fd.textlength('make.fun', font=first)
    second_width = fd.textlength('people and their agents earn money here', font=second)
    gap = 16 * SCALE
    total_width = round(first_width + gap + second_width)
    footer_line = Image.new('RGBA', (total_width + 2 * SCALE, 50 * SCALE))
    fdraw = ImageDraw.Draw(footer_line)
    fdraw.text((0, 38 * SCALE), 'make.fun', font=first, fill=BLACK, anchor='ls')
    fdraw.text((round(first_width + gap), 38 * SCALE), 'people and their agents earn money here', font=second, fill=BLACK, anchor='ls')
    if footer_line.width > 560 * SCALE:
        footer_line = footer_line.resize((560 * SCALE, footer_line.height), Image.Resampling.LANCZOS)
    footer.alpha_composite(footer_line, (420 * SCALE - footer_line.width // 2, 628 * SCALE))
    text.alpha_composite(footer)

    ticket = ticket.rotate(2, resample=Image.Resampling.BICUBIC)
    text = text.rotate(2, resample=Image.Resampling.BICUBIC)
    shadow = Image.new('RGBA', CANVAS, (45, 40, 42, 0))
    shadow.putalpha(ticket.getchannel('A').filter(ImageFilter.GaussianBlur(8 * SCALE)).point(lambda a: a * 45 // 255))
    image.alpha_composite(shadow, (6 * SCALE, 8 * SCALE))
    image.alpha_composite(ticket)
    image.alpha_composite(text)

    shadow = Image.new('RGBA', CANVAS)
    ImageDraw.Draw(shadow).ellipse(scaled_box((754, 685, 1000, 731)), fill=(0, 0, 0, 100))
    image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(10 * SCALE)))
    ghost = Image.new('RGBA', CANVAS)
    gd = ImageDraw.Draw(ghost)
    gd.ellipse(scaled_box((731, 641, 929, 785)), fill='white', outline='black', width=8 * SCALE)
    gd.ellipse(scaled_box((740, 550, 920, 730)), fill='white', outline='black', width=8 * SCALE)
    for x in (800, 860):
        gd.polygon(star(x, 620, 17, 5, 4), fill='black')
    # The counter hides the bottom of the shopkeeper, not the ticket.
    gd.rectangle((0, 700 * SCALE, CANVAS[0], CANVAS[1]), fill=(0, 0, 0, 0))
    if ImageChops.multiply(text.getchannel('A'), ghost.getchannel('A')).getbbox():
        raise ValueError('Ticket text overlaps the ghost')
    image.alpha_composite(ghost)

    draw = ImageDraw.Draw(image)
    draw.ellipse(scaled_box((890, 660, 970, 740)), fill=(224, 31, 153, 255), outline='black', width=8 * SCALE)
    draw.polygon(star(930, 700, 23, 10, 5), fill='white')
    draw.ellipse(scaled_box((882, 672, 918, 708)), fill='white', outline='black', width=8 * SCALE)
    return image.convert('RGB').resize((SIZE, SIZE), Image.Resampling.LANCZOS)


def main() -> None:
    image = render()
    output = Path(__file__).with_name('meme2.png')
    image.save(output, format='PNG', optimize=True)
    byte_size = output.stat().st_size
    print(f'{image.width}x{image.height}, {byte_size} bytes')
    if byte_size >= 1024 * 1024:
        raise ValueError('PNG must be smaller than 1 MiB')


if __name__ == '__main__':
    main()
