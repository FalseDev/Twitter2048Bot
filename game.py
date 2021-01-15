import math
import random
from io import BytesIO
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFont

fontpath = "./fonts/FiraCode-Retina.woff"


def rounded_corner(
    *,
    fill: Tuple[int],
    radius: int,
    colorspace: str,
        bg: Tuple[int] = (0, 0, 0)) -> Image.Image:
    """Generate a smoothened corner as an Image object"""
    corner = Image.new("RGBA", (radius, radius), bg)
    draw = ImageDraw.ImageDraw(corner)
    draw.pieslice((0, 0, radius * 2, radius * 2), 180, 270, fill=fill)
    return corner


def rounded_sqr(
    *,
    fill: Tuple[int],
    radius: int,
    side: int,
    colorspace: str = "RGBA",
    bg: Tuple[int] = (0, 0, 0)
) -> Image.Image:
    """Generate a square with smoothened corners"""
    # Blank image with fill
    square = Image.new(colorspace, (side, side), fill)
    # Get an appropriate corner
    corner = rounded_corner(
        fill=fill,
        radius=radius,
        colorspace=colorspace,
        bg=bg)
    # Paste corners
    square.paste(corner, (0, 0))
    square.paste(corner.rotate(90), (0, side - radius))
    square.paste(corner.rotate(180), (side - radius, side - radius))
    square.paste(corner.rotate(270), (side - radius, 0))
    return square


class Game:
    def __init__(self, boardstate: List[List[int]]):
        self.boardstate = boardstate

        # Number to color mapping
        self.FILL_MAP = {
            2048: (110, 52, 27),
            1024: (125, 58, 29),
            512: (138, 62, 29),
            256: (145, 64, 29),
            128: (158, 66, 27),
            64: (171, 70, 27),
            32: (179, 70, 23),
            16: (189, 71, 21),
            8: (207, 73, 17),
            4: (219, 74, 13),
            2: (224, 73, 9),
            1: (232, 74, 7),
            0: (252, 75, 0)
        }

    def left(self):
        for row in self.boardstate:
            for i in range(row.count(0)):
                row.remove(0)
                row.append(0)
            for i in range(3):
                if row[i] == row[i + 1]:
                    row[i] += row.pop(i + 1)
                    row.append(0)
        return self

    def right(self):
        return self.reverse_rows().left().reverse_rows()

    def up(self):
        return self.transpose().left().transpose()

    def down(self):
        return self.transpose().right().transpose()

    def reverse_rows(self):
        [r.reverse() for r in self.boardstate]
        return self

    def transpose(self):
        self.boardstate = [[row[i] for row in self.boardstate]
                           for i in range(4)]
        return self

    def dumps(self):
        return "-".join(map(lambda row: "-".join(map(str, row)),
                            self.boardstate))

    @classmethod
    def loads(cls, data: str):
        boxes = list(map(int, data.split("-")))
        return cls(boardstate=[boxes[i * 4:(i + 1) * 4] for i in range(4)])

    def print(self):
        pic = "\n".join(["\t".join(map(str, row)) for row in self.boardstate])
        print(pic)
        return self

    def to_twitter_image_bytes(self, controls: str):
        bytes_obj = BytesIO()
        bytes_obj.name = "image.png"
        self.to_twitter_image(controls).save(bytes_obj)
        bytes_obj.seek(0)
        return bytes_obj

    def to_twitter_image(self, controls: str):
        im = self.to_image(size=600)
        bg = Image.new("RGBA", (1200, 675), (233, 150, 122))
        bg.paste(im, (50, 37))
        draw = ImageDraw.Draw(bg)
        font = ImageFont.truetype(fontpath, 50)
        if controls == "LR":
            text = "RETWEET - LEFT\n\nLIKE - RIGHT"
            coords = (700, 250)
        elif controls == "UD":
            text = "RETWEET - UP\n\nLIKE - DOWN"
            coords = (725, 250)
        draw.text(coords, text=text, font=font, align="center", fill=(0, 0, 0))
        return bg

    def to_image(self, bg=(233, 150, 122),
                 second_bg=(101, 101, 101), size=1000):
        box_width = size // 5
        paste_offset = ((11 * size) // 100)

        font = ImageFont.truetype(
            fontpath, 3 * size // 50)
        im = Image.new("RGBA", (size, size), bg)
        im.paste(
            rounded_sqr(fill=second_bg, radius=2 * size // 25, side=size * 9 // 10, bg=bg), (size // 20, size // 20))
        for x in range(4):
            for y in range(4):
                value = self.boardstate[x][y]

                sqr = self.box(value, font=font, bg=second_bg, size=size)

                im.paste(sqr, (paste_offset + y *
                               box_width, paste_offset + x * box_width))
        return im

    def box(self, value, *, font: ImageFont.FreeTypeFont,
            bg: Tuple[int], size: int):
        """
        Draws and returns a box with rounded corners and given text
        """
        draw_x = (size * 9) // 100 - font.getlength(str(value)) / 2
        draw_y = (size * 9) // 100 - (font.font.height / 2)

        sqr = rounded_sqr(fill=self.FILL_MAP[value],
                          radius=size // 25, side=size * 9 // 50, bg=bg)
        draw = ImageDraw.ImageDraw(sqr)
        if value != 0:
            draw.text((draw_x, draw_y), text=str(value), font=font)
        return sqr

    def spawn_box(self):
        empties = sum([row.count(0) for row in self.boardstate])
        slot_no = random.randint(1, empties)
        passed = 0
        for row in self.boardstate:
            for i, val in enumerate(row):
                if val == 0:
                    passed += 1
                if passed == slot_no:
                    row[i] = random.choice((1, 2, 4))
                    return self

    @classmethod
    def new(cls):
        return cls(boardstate=[[0] * 4 for i in range(4)])

    def __repr__(self):
        return f"<2048 Game with state {self.boardstate}>"
