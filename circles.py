from __future__ import annotations
from argparse import ArgumentParser
from dataclasses import dataclass
from functools import cached_property
import math
from random import randint, random, seed
from typing import Iterator, NamedTuple
import svg


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

    def contains(self, point: Point) -> bool:
        """Check if the given point is inside the circle
        """
        return self.c.distance_to(point) <= self.r

    def min_distance(self, other: Point) -> float:
        """Shortest distance from circle side to the point
        """
        return abs(self.r - self.c.distance_to(other))


@dataclass
class Generator:
    size: int
    min_shift: int
    max_shift: int
    min_width: int
    min_circles: int
    max_circles: int
    min_radius: int

    def generate(self) -> svg.SVG:
        return svg.SVG(
            width=self.size,
            height=self.size,
            xmlns='http://www.w3.org/2000/svg',
            elements=list(self.iter_elements()),
        )

    @cached_property
    def color(self) -> str:
        hue = randint(0, 360)
        saturation = randint(75, 100)
        return f'hsl({hue}, {saturation}%, 20%)'

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

        circles_count = randint(self.min_circles, self.max_circles)
        min_distance = math.ceil(self.inner.min_distance(Point(self.outer.r, self.outer.r)))
        circles = [self.inner]
        for _ in range(circles_count):
            for _ in range(40):
                circle = self.get_random_circle(min_distance, circles)
                if circle is not None:
                    circles.append(circle)
                    yield circle.render(self.color)
                    break

    def get_random_circle(
        self, min_distance: int, circles: list[Circle],
    ) -> Circle | None:
        # pick random coordinates for the center
        distance = randint(min_distance, math.floor(self.outer.r))
        angle = random() * math.pi * 2
        cx = self.outer.r + math.cos(angle) * distance
        cy = self.outer.r + math.sin(angle) * distance
        assert cx >= 0
        assert cy >= 0
        center = Point(cx, cy)

        # do not draw the circle if the center is inside of another circle
        for other in circles:
            if other.contains(center):
                return None

        # pick radius so the circle touches the closest circle
        r = self.outer.min_distance(center)
        for other in circles:
            r = min(r, other.min_distance(center))

        if r < self.min_radius:
            return None
        return Circle(c=center, r=r)


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument('--size', type=int, default=800)
    parser.add_argument('--min-shift', type=int, default=20)
    parser.add_argument('--max-shift', type=int, default=60)
    parser.add_argument('--min-width', type=int, default=20)
    parser.add_argument('--min-radius', type=int, default=4)
    parser.add_argument('--min-circles', type=int, default=2000)
    parser.add_argument('--max-circles', type=int, default=3000)
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
        min_radius=args.min_radius,
    )
    print(generator.generate())


if __name__ == '__main__':
    main()
