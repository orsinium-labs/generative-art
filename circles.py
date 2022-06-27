from __future__ import annotations
from argparse import ArgumentParser
from dataclasses import dataclass
from functools import cached_property
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

    def distance_to(self, p: Point) -> float:
        dx = abs(self.x - p.x)
        dy = abs(self.y - p.y)
        return math.sqrt(dx ** 2 + dy ** 2)


class Circle(NamedTuple):
    c: Point
    r: float

    def render(self, color: str) -> svg.Element:
        return svg.Circle(
            cx=self.c.x, cy=self.c.y, r=self.r,
            stroke=color, stroke_width=1,
            fill="none",
        )

    def min_distance(self, p: Point) -> float:
        """Shortest distance from circle side to the point
        """
        return abs(self.r - self.c.distance_to(p))


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

    @cached_property
    def palette(self) -> Palette:
        return Palette.new_random()

    @cached_property
    def outer(self) -> Circle:
        outer_r = self.size // 2
        outer_center = Point(outer_r, outer_r)
        return Circle(c=outer_center, r=outer_r)

    @cached_property
    def inner(self) -> Circle:
        inner_x = self.outer.r + randint(self.min_shift, self.max_shift)
        inner_y = self.outer.r + randint(self.min_shift, self.max_shift)
        inner_center = Point(inner_x, inner_y)
        r = self.outer.min_distance(inner_center) - self.min_width
        return Circle(c=inner_center, r=r)

    def iter_elements(self) -> Iterator[svg.Element]:
        assert self.inner.r < self.outer.r
        yield self.inner.render(self.palette.light)
        yield self.outer.render(self.palette.light)

        circles_count = randint(self.min_circles, self.max_circles)
        min_distance = math.ceil(self.inner.min_distance(Point(self.outer.r, self.outer.r)))
        for _ in range(circles_count):
            for _ in range(40):
                circle = self.get_random_circle(min_distance)
                inner_distance = circle.c.distance_to(self.inner.c)
                if inner_distance < self.inner.r:
                    continue
                yield circle.render(self.palette.dark)
                break

    def get_random_circle(self, min_distance: int) -> Circle:
        distance = randint(min_distance, math.floor(self.outer.r))
        angle = random() * math.pi * 2
        cx = self.outer.r + math.cos(angle) * distance
        cy = self.outer.r + math.sin(angle) * distance
        assert cx >= 0
        assert cy >= 0
        r = 5
        return Circle(c=Point(cx, cy), r=r)


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
