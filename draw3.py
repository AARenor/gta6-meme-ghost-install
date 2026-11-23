from math import cos, pi, sin
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

SIZE = 1024
SCALE = 3
CANVAS = (SIZE * SCALE, SIZE * SCALE)
FONT_DIR = Path('/usr/share/fonts/truetype/dejavu')
INK = (20, 18, 16, 255)


def box(coords: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    left, top, right, bottom = coords
    return left * SCALE, top * SCALE, right * SCALE, bottom * SCALE


def font(size: int, style: str = '') -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / f'DejaVuSans{style}.ttf'), size * SCALE)


def line(
    layer: Image.Image,
    pieces: list[tuple[str, ImageFont.FreeTypeFont]],
    y: int,
    width: int,
) -> None:
    measure = ImageDraw.Draw(layer)
    widths = [round(measure.textlength(text, font=face)) for text, face in pieces]
    bounds = [face.getbbox(text) for text, face in pieces]
    top = min(bound[1] for bound in bounds)
    bottom = max(bound[3] for bound in bounds)
    text = Image.new('RGBA', (sum(widths) + 2 * SCALE, bottom - top + 2 * SCALE))
    draw = ImageDraw.Draw(text)
    x = SCALE
    for (value, face), piece_width in zip(pieces, widths):
        draw.text((x, SCALE - top), value, font=face, fill=INK)
        x += piece_width
    original_width = text.width
    if text.width > width * SCALE:
        text = text.resize((width * SCALE, text.height), Image.Resampling.LANCZOS)
    print(f'{pieces[0][0]}: {original_width / SCALE:.1f}px to {text.width / SCALE:.1f}px')
    layer.alpha_composite(text, (150 * SCALE, (y - 1) * SCALE))


def star(cx: int, cy: int, outer: int, inner: int) -> list[tuple[int, int]]:
    return [
        (
            round((cx + (outer if i % 2 == 0 else inner) * cos(-pi / 2 + i * pi / 4)) * SCALE),
            round((cy + (outer if i % 2 == 0 else inner) * sin(-pi / 2 + i * pi / 4)) * SCALE),
        )
        for i in range(8)
    ]


def render() -> Image.Image:
    image = Image.new('RGBA', CANVAS, (34, 30, 26, 255))
    glow = Image.new('RGBA', CANVAS)
    ImageDraw.Draw(glow).ellipse(box((-220, -250, 560, 510)), fill=(210, 177, 120, 35))
    image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120 * SCALE)))
    ImageDraw.Draw(image).rectangle(box((75, 683, 949, 792)), fill=(28, 42, 34, 255))

    paper = Image.new('RGBA', CANVAS)
    pd = ImageDraw.Draw(paper)
    pd.rectangle(box((90, 110, 934, 774)), fill=(250, 246, 236, 255), outline=(150, 132, 110, 255), width=3 * SCALE)
    for x in range(109, 139, 7):
        pd.line([(x * SCALE, 128 * SCALE), (x * SCALE, 755 * SCALE)], fill=(222, 215, 201, 110), width=SCALE)
    pd.line([(150 * SCALE, 245 * SCALE), (874 * SCALE, 245 * SCALE)], fill=INK, width=2 * SCALE)
    pd.line([(150 * SCALE, 680 * SCALE), (800 * SCALE, 680 * SCALE)], fill=INK, width=2 * SCALE)

    text = Image.new('RGBA', CANVAS)
    line(text, [('OVERDUE NOTICE', font(54, '-Bold'))], 170, 710)
    line(text, [('ITEM: GRAND THEFT AUTO V', font(34, '-Bold'))], 285, 710)
    line(text, [('BORROWED', font(26, '-Bold')), ('  17 SEP 2013', font(26))], 345, 710)
    line(text, [('DUE', font(26, '-Bold')), ('  1 OCT 2013', font(26))], 382, 710)
    line(text, [('4,813 DAYS OVERDUE', font(72, '-Bold'))], 450, 724)
    line(text, [('FINE: $48.13', font(44, '-Bold')), ('   1 cent a day', font(28, '-Oblique'))], 560, 710)
    line(text, [('paid by my agent, from bounties on make.fun', font(30, '-Oblique'))], 625, 650)
    line(text, [('make.fun    people and their agents earn money here', font(22))], 706, 650)

    stamp = Image.new('RGBA', CANVAS)
    sd = ImageDraw.Draw(stamp)
    red = (150, 30, 40, 255)
    sd.rounded_rectangle(box((695, 128, 915, 150)), radius=5 * SCALE, outline=red, width=2 * SCALE)
    face = font(20, '-Bold')
    label = 'VICE CITY PUBLIC LIBRARY'
    bounds = face.getbbox(label)
    label_image = Image.new('RGBA', (bounds[2] - bounds[0] + 2 * SCALE, bounds[3] - bounds[1] + 2 * SCALE))
    ImageDraw.Draw(label_image).text((SCALE - bounds[0], SCALE - bounds[1]), label, font=face, fill=red)
    if label_image.width > 210 * SCALE:
        label_image = label_image.resize((210 * SCALE, label_image.height), Image.Resampling.LANCZOS)
    stamp.alpha_composite(label_image, (805 * SCALE - label_image.width // 2, 132 * SCALE))
    stamp = stamp.rotate(8, resample=Image.Resampling.BICUBIC, center=(805 * SCALE, 139 * SCALE))
    paper.alpha_composite(stamp)
    paper.alpha_composite(text)
    paper = paper.rotate(-1, resample=Image.Resampling.BICUBIC)
    text = text.rotate(-1, resample=Image.Resampling.BICUBIC)
    shadow = Image.new('RGBA', CANVAS, (0, 0, 0, 0))
    shadow.putalpha(paper.getchannel('A').filter(ImageFilter.GaussianBlur(8 * SCALE)).point(lambda a: a * 60 // 255))
    image.alpha_composite(shadow, (5 * SCALE, 7 * SCALE))
    image.alpha_composite(paper)

    ghost = Image.new('RGBA', CANVAS)
    gd = ImageDraw.Draw(ghost)
    gd.ellipse(box((818, 638, 942, 762)), fill='white', outline='black', width=7 * SCALE)
    for x in (857, 901):
        gd.polygon(star(x, 690, 12, 4), fill='black')
    gd.ellipse(box((900, 710, 960, 770)), fill=(235, 188, 59, 255), outline='black', width=7 * SCALE)
    gd.polygon(star(930, 740, 15, 7), fill=(255, 241, 181, 255))
    gd.ellipse(box((893, 714, 919, 740)), fill='white', outline='black', width=7 * SCALE)
    if ImageChops.multiply(text.getchannel('A'), ghost.getchannel('A')).getbbox():
        raise ValueError('Paper text overlaps the ghost')
    image.alpha_composite(ghost)
    return image.convert('RGB').resize((SIZE, SIZE), Image.Resampling.LANCZOS)


def main() -> None:
    image = render()
    output = Path(__file__).with_name('meme3.png')
    image.save(output, format='PNG', optimize=True)
    byte_size = output.stat().st_size
    print(f'{image.width}x{image.height}, {byte_size} bytes')
    if byte_size >= 1024 * 1024:
        raise ValueError('PNG must be smaller than 1 MiB')


if __name__ == '__main__':
    main()
