from __future__ import annotations
from argparse import ArgumentParser
import math
from random import choice, randint, random, seed
from typing import Iterator, NamedTuple
from dataclasses import dataclass
import svg


class Point(NamedTuple):
    x: float
    y: float


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
    body_tension: int

    @property
    def cx(self) -> int:
        return self.width // 2

    @property
    def cy(self) -> int:
        return self.height // 2

    def generate_grid(self, size_x: int, size_y: int) -> svg.SVG:
        if size_x == 1 and size_y == 1:
            return self.generate()
        elements: list[svg.Element] = []
        for ix in range(size_x):
            x = self.width * ix
            for iy in range(size_y):
                y = self.width * iy
                elements.append(svg.G(
                    transform=[svg.Translate(x, y)],
                    elements=[self.generate()],
                ))
        return svg.SVG(
            width=self.width * size_x,
            height=self.height * size_y,
            xmlns='http://www.w3.org/2000/svg',
            elements=elements,
        )

    def generate(self) -> svg.SVG:
        return svg.SVG(
            width=self.width,
            height=self.height,
            xmlns='http://www.w3.org/2000/svg',
            elements=list(self.iter_elements()),
        )

    def iter_elements(self) -> Iterator[svg.Path]:
        palette = Palette.new_random()
        body_size = randint(25, 40) * min(self.width, self.height) // 100
        yield self.get_body(palette, body_size)
        yield from self.iter_eyes(palette, body_size // 2)

    def get_body(self, palette: Palette, size: int) -> svg.Path:
        points = list(self.iter_body_points(size))
        return svg.Path(
            d=list(self.spline(points)),
            fill=palette.light,
            stroke=palette.dark,
            stroke_width=self.line_width,
        )

    def iter_body_points(self, size: int) -> Iterator[Point]:
        n_points = randint(3, 12)   # how many points do we want?
        angle_step = math.pi * 2 / n_points  # step used to place each point at equal distances
        for point_number in range(1, n_points + 1):
            pull = random_float(.75, 1)
            angle = point_number * angle_step
            x = self.cx + math.cos(angle) * size * pull
            y = self.cx + math.sin(angle) * size * pull
            yield Point(x, y)

    def spline(self, points: list[Point]) -> Iterator[svg.PathData]:
        """
        https://github.com/georgedoescode/splinejs
        """
        yield svg.MoveTo(*points[-1])
        first_point = points[0]
        second_point = points[1]
        points.insert(0, points[-1])
        points.insert(0, points[-2])
        points.append(first_point)
        points.append(second_point)
        for p0, p1, p2, p3 in zip(points, points[1:], points[2:], points[3:]):
            yield svg.CubicBezier(
                x1=p1.x + (p2.x - p0.x) / 6 * self.body_tension,
                y1=p1.y + (p2.y - p0.y) / 6 * self.body_tension,
                x2=p2.x - (p3.x - p1.x) / 6 * self.body_tension,
                y2=p2.y - (p3.y - p1.y) / 6 * self.body_tension,
                x=p2.x,
                y=p2.y,
            )

    def iter_eyes(self, palette: Palette, max_size: int):
        half_size = max_size // 2
        size = randint(half_size, max_size - 1)
        n_eyes = choice([1, 2, 2, 2, 3, 4])
        if n_eyes == 1:
            yield self.get_eye(palette, self.cx, self.cy, size)
        if n_eyes == 2:
            yield self.get_eye(palette, self.cx - half_size, self.cy, size)
            yield self.get_eye(palette, self.cx + half_size, self.cy, size)
        if n_eyes == 3:
            yield self.get_eye(palette, self.cx - half_size, self.cy - half_size, size)
            yield self.get_eye(palette, self.cx + half_size, self.cy - half_size, size)
            yield self.get_eye(palette, self.cx, self.cy + half_size, size)
        if n_eyes == 4:
            yield self.get_eye(palette, self.cx - half_size, self.cy - half_size, size)
            yield self.get_eye(palette, self.cx + half_size, self.cy - half_size, size)
            yield self.get_eye(palette, self.cx - half_size, self.cy + half_size, size)
            yield self.get_eye(palette, self.cx + half_size, self.cy + half_size, size)

    def get_eye(self, palette: Palette, x: int, y: int, size: int) -> svg.Element:
        radius = size // 2
        return svg.G(
            transform=[svg.Translate(x, y)],
            elements=[
                # outer ring
                svg.Circle(
                    cx=0, cy=0, r=radius,
                    stroke=palette.dark,
                    fill='white',
                    stroke_width=self.line_width,
                ),
                # pupil
                svg.Circle(
                    cx=0, cy=0, r=radius // 2,
                    fill=palette.dark,
                    stroke_width=self.line_width,
                ),
            ],
        )


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument('--width', type=int, default=200)
    parser.add_argument('--height', type=int, default=200)
    parser.add_argument('--line-width', type=int, default=2)
    parser.add_argument('--body-tension', type=float, default=1)
    parser.add_argument('--seed', type=int)
    parser.add_argument('--grid-x', type=int, default=1)
    parser.add_argument('--grid-y', type=int, default=1)
    args = parser.parse_args()
    if args.seed:
        seed(args.seed)
    generator = Generator(
        width=args.width,
        height=args.height,
        line_width=args.line_width,
        body_tension=args.body_tension,
    )
    print(generator.generate_grid(args.grid_x, args.grid_y))


if __name__ == '__main__':
    main()
