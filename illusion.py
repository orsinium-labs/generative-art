from __future__ import annotations
from argparse import ArgumentParser
from dataclasses import dataclass
from itertools import cycle
from random import choice
from typing import Iterator
import svg


LINE_COLORS = ['red', 'green', 'blue']


@dataclass
class Generator:
    width: int
    height: int
    line_width: int
    radius: int
    circle_color: str

    def generate(self) -> svg.SVG:
        return svg.SVG(
            width=self.width,
            height=self.height,
            elements=list(self.iter_elements()),
        )

    def iter_elements(self) -> Iterator[svg.Element]:
        # draw horizontal lines on the background
        colors = cycle(LINE_COLORS)
        for y in range(0, self.height, self.line_width):
            yield svg.Rect(
                x=0, y=y,
                width=self.width,
                height=self.line_width,
                fill=next(colors),
            )

        # draw the circles
        r = self.radius
        for cx in range(r * 2, self.width - r, r * 3):
            for cy in range(r * 2, self.height - r, r * 3):
                yield svg.Circle(
                    cx=cx, cy=cy, r=r,
                    fill=self.circle_color,
                )
                yield from self.draw_lines_over(cx=cx, cy=cy)

    # draw some lines over the circle
    def draw_lines_over(self, cx: int, cy: int) -> Iterator[svg.Rect]:
        r = self.radius
        color = choice(LINE_COLORS)
        index = LINE_COLORS.index(color)
        start_y = cy - r + index * self.line_width
        step_y = self.line_width * len(LINE_COLORS)
        for y in range(start_y, cy + r, step_y):
            yield svg.Rect(
                x=cx-r, y=y,
                width=r*2,
                height=self.line_width,
                fill=color,
            )


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument('--width', type=int, default=800, help='the canvas width')
    parser.add_argument('--height', type=int, default=800, help='the canvas height')
    parser.add_argument('--line-width', type=int, default=5, help='vertical (oy) size of each stripe')
    parser.add_argument('--radius', type=int, default=60, help='radius of each circle')
    parser.add_argument('--circle-color', type=str, default='#cd7f32')
    args = parser.parse_args()
    generator = Generator(**vars(args))
    print(generator.generate())


if __name__ == '__main__':
    main()
