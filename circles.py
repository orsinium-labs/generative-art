from __future__ import annotations
from argparse import ArgumentParser
from dataclasses import dataclass
import math
from random import randint, random, seed
from typing import Iterator, NamedTuple
import svg


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
            dark=f'hsl({hue}, {saturation}%, 20%)',
            light=f'hsl({hue}, {saturation}%, 80%)',
        )


class Point(NamedTuple):
    x: float
    y: float

    @property
    def distance(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def distance_to(self, p: Point) -> float:
        dx = abs(self.x - p.x)
        dy = abs(self.y - p.y)
        return math.sqrt(dx ** 2 + dy ** 2)


class Circle(NamedTuple):
    x: float
    y: float
    r: float

    def render(self, color: str) -> svg.Element:
        return svg.Circle(
            cx=self.x, cy=self.y, r=self.r,
            stroke=color, stroke_width=1,
            fill="none",
        )

    def min_distance(self, p: Point) -> float:
        """Shortest distance from circle side to the point
        """
        dx = abs(self.x - p.x)
        dy = abs(self.y - p.y)
        return abs(self.r - Point(dx, dy).distance)


@dataclass
class Generator:
    size: int
    min_shift: int
    max_shift: int
    min_width: int
    min_circles: int
    max_circles: int

    def generate(self) -> svg.SVG:
        return svg.SVG(
            width=self.size,
            height=self.size,
            xmlns='http://www.w3.org/2000/svg',
            elements=list(self.iter_elements()),
        )

    def iter_elements(self) -> Iterator[svg.Element]:
        palette = Palette.new_random()
        outer_r = self.size // 2
        outer_circle = Circle(x=outer_r, y=outer_r, r=outer_r)
        inner_x = outer_r + randint(self.min_shift, self.max_shift)
        inner_y = outer_r + randint(self.min_shift, self.max_shift)
        inner_circle = Circle(
            x=inner_x, y=inner_y,
            r=outer_circle.min_distance(Point(inner_x, inner_y)) - self.min_width,
        )
        assert inner_circle.r < outer_circle.r
        yield inner_circle.render(palette.light)
        yield outer_circle.render(palette.light)

        circles_count = randint(self.min_circles, self.max_circles)
        min_distance = round(inner_circle.min_distance(Point(outer_r, outer_r)))
        for _ in range(circles_count):
            for _ in range(40):
                distance = randint(min_distance, outer_r)
                angle = random() * math.pi * 2
                cx = outer_r + math.cos(angle) * distance
                cy = outer_r + math.sin(angle) * distance
                assert cx >= 0
                assert cy >= 0
                r = 5
                inner_distance = Point(cx, cy).distance_to(Point(inner_x, inner_y))
                if inner_distance < inner_circle.r:
                    continue
                yield Circle(x=cx, y=cy, r=r).render(palette.dark)
                break


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument('--size', type=int, default=200)
    parser.add_argument('--min-shift', type=int, default=10)
    parser.add_argument('--max-shift', type=int, default=20)
    parser.add_argument('--min-width', type=int, default=10)
    parser.add_argument('--min-circles', type=int, default=10)
    parser.add_argument('--max-circles', type=int, default=20)
    parser.add_argument('--seed', type=int)
    args = parser.parse_args()
    if args.seed:
        seed(args.seed)
    generator = Generator(
        size=args.size,
        min_shift=args.min_shift,
        max_shift=args.max_shift,
        min_width=args.min_width,
        min_circles=args.min_circles,
        max_circles=args.max_circles,
    )
    print(generator.generate())


if __name__ == '__main__':
    main()
