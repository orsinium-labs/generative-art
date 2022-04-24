from __future__ import annotations
from argparse import ArgumentParser
import math
from random import randint, random, seed
from typing import Iterator
from dataclasses import dataclass
import svg


def random_float(start: float, end: float) -> float:
    return start + random() * (end - start)


@dataclass
class Palette:
    primary: str
    dark: str
    light: str

    @classmethod
    def new_random(cls) -> Palette:
        hue = randint(0, 360)
        saturation = randint(75, 100)
        lightness = randint(75, 95)
        return cls(
            primary=f'hsl({hue}, {saturation}%, {lightness}%)',
            dark=f'hsl({hue}, {saturation}%, 2%)',
            light=f'hsl({hue}, {saturation}%, 98%)',
        )


@dataclass
class Generator:
    """
    https://georgefrancis.dev/writing/generative-svg-blob-characters/
    """
    width: int
    height: int
    line_width: int

    # properties

    @property
    def center_x(self) -> int:
        return self.width // 2

    @property
    def center_y(self) -> int:
        return self.height // 2

    # methods

    def generate(self) -> svg.SVG:
        return svg.SVG(
            width=self.width,
            height=self.height,
            xmlns="http://www.w3.org/2000/svg",
            elements=list(self.iter_elements()),
        )

    def iter_elements(self) -> Iterator[svg.Path]:
        palette = Palette.new_random()
        body_size = randint(25, 40) * min(self.width, self.height) // 100
        yield self.get_body(palette, body_size)
        yield from self.iter_eyes(palette, body_size // 2)

    def get_body(self, palette: Palette, size: int) -> svg.Path:
        points = list(self.iter_body_points(size))
        first_point = points[0]
        points.append(first_point)  # close the path
        path_data: list[svg.PathData] = [svg.MoveTo(*first_point)]
        for x, y in points:
            path_data.append(svg.LineTo(x, y))
        return svg.Path(
            d=path_data,
            fill="none",
            stroke=palette.dark,
            stroke_width=self.line_width,
        )

    def iter_body_points(self, size: int) -> Iterator[tuple[int, int]]:
        n_points = randint(3, 12)   # how many points do we want?
        angle_step = math.pi * 2 / n_points  # step used to place each point at equal distances
        for point_number in range(0, n_points):
            pull = random_float(.75, 1)
            angle = point_number * angle_step
            x = self.center_x + math.cos(angle) * size * pull
            y = self.center_x + math.sin(angle) * size * pull
            yield (round(x), round(y))

    def iter_eyes(self, palette: Palette, max_size: int):
        half_size = max_size // 2
        size = randint(half_size, max_size)
        yield self.get_eye(palette, self.center_x - half_size, self.center_y, size)
        yield self.get_eye(palette, self.center_x + half_size, self.center_y, size)

    def get_eye(self, palette: Palette, x: int, y: int, size: int) -> svg.Element:
        return svg.G(
            transform=[svg.Translate(x, y)],
            elements=[
                # outer ring
                svg.Circle(
                    cx=0, cy=0, r=size // 2,
                    stroke=palette.dark,
                    fill=palette.light,
                    stroke_width=self.line_width,
                ),
                # pupil
                svg.Circle(
                    cx=0, cy=0, r=size // 4,
                    fill=palette.dark,
                    stroke_width=self.line_width,
                ),
            ],
        )


def main():
    parser = ArgumentParser()
    parser.add_argument('--width', type=int, default=200)
    parser.add_argument('--height', type=int, default=200)
    parser.add_argument('--line-width', type=int, default=2)
    parser.add_argument('--seed', type=int)
    args = parser.parse_args()
    if args.seed:
        seed(args.seed)
    generator = Generator(
        width=args.width,
        height=args.height,
        line_width=args.line_width,
    )
    print(generator.generate())


if __name__ == "__main__":
    main()
