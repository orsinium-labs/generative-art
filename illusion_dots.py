from __future__ import annotations
from argparse import ArgumentParser
from dataclasses import dataclass
from typing import Iterator
import svg


LINE_COLORS = ['red', 'green', 'blue']


@dataclass
class Generator:
    width: int
    height: int
    square_size: int
    padding: int

    def generate(self) -> svg.SVG:
        return svg.SVG(
            width=self.width,
            height=self.height,
            elements=list(self.iter_elements()),
        )

    def iter_elements(self) -> Iterator[svg.Element]:
        # grey background
        yield svg.Rect(
            x=0, y=0,
            width=self.width,
            height=self.height,
            fill='grey',
        )

        # black squares
        step = self.square_size + self.padding
        half_padding = self.padding // 2
        for x in range(self.padding, self.width - step + half_padding, step):
            for y in range(self.padding, self.height - step + half_padding, step):
                yield svg.Rect(
                    x=x, y=y,
                    width=self.square_size,
                    height=self.square_size,
                    fill='black',
                )

        # white circles between squares
        radius = round(self.padding / (2 ** .5), 2)
        for x in range(0, self.width, step):
            for y in range(0, self.height, step):
                yield svg.Circle(
                    cx=x + half_padding,
                    cy=y + half_padding,
                    r=radius,
                    fill='white',
                )


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument('--width', type=int, default=780, help='the canvas width')
    parser.add_argument('--height', type=int, default=780, help='the canvas height')
    parser.add_argument('--square-size', type=int, default=60, help='size of each square')
    parser.add_argument('--padding', type=int, default=10, help='space between squares')
    args = parser.parse_args()
    generator = Generator(**vars(args))
    print(generator.generate())


if __name__ == '__main__':
    main()
