import curses
import random
import unittest
from collections import namedtuple
from curses import wrapper
from enum import Enum

Coord = namedtuple('Coord', ['y', 'x'])


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class Speed(Enum):
    SLOW = 5
    FAST = 10


SnakePart = namedtuple('SnakePart', ['coord', 'char'])
Prize = namedtuple('Prize', ['coord', 'char'])


def draw_snake(screen, snake: list):
    for p in snake:
        screen.addch(p.coord.y, p.coord.x, p.char)


def move_coord(coord: Coord, direction) -> Coord:
    y, x = coord.y, coord.x
    # move
    if direction == Direction.LEFT:
        return Coord(y, x - 1)
    elif direction == Direction.RIGHT:
        return Coord(y, x + 1)
    elif direction == Direction.UP:
        return Coord(y - 1, x)
    elif direction == Direction.DOWN:
        return Coord(y + 1, x)
    return Coord(y, x)


def add_new_part(snake: list):
    snake.append(SnakePart(None, '0'))


def move_snake(curr_snake: list, head_direction):
    next_snake = [SnakePart(
        coord=move_coord(curr_snake[0].coord, head_direction),
        char=curr_snake[0].char
    )]
    for i in range(1, len(curr_snake)):
        next_snake.append(
            SnakePart(
                coord=curr_snake[i - 1].coord,
                char=curr_snake[i].char))
    return next_snake


def draw_prizes(screen, prizes):
    for p in prizes:
        screen.addch(p.coord.y, p.coord.x, p.char)


LINES = 10
COLS = 100


def main(screen):
    play_window = curses.newwin(LINES, COLS, 0, 0)

    speed = Speed.SLOW
    head_pos = Coord(LINES // 2, COLS // 2)
    snake = [SnakePart(head_pos, 'X')]
    # don't show the cursor
    curses.curs_set(False)
    head_direction = None
    # don't wait for the user input
    screen.nodelay(True)
    prizes = set()
    total_prizes = 5

    while True:
        if len(prizes) < total_prizes:
            prizes.add(
                Prize(
                    Coord(
                        y=random.randint(1, LINES - 2),
                        x=random.randint(1, COLS - 2)),
                    char='$'
                ))
        # Draw
        play_window.clear()
        play_window.box('|', '-')
        draw_snake(play_window, snake)
        draw_prizes(play_window, prizes)
        play_window.refresh()
        curses.napms(1000 // speed.value)

        head = snake[0]

        c = screen.getch()
        if c == ord('q'):
            exit(1)
        elif c == ord('a'):
            add_new_part(snake)
        elif c == curses.KEY_LEFT:
            head_direction = Direction.LEFT
        elif c == curses.KEY_RIGHT:
            head_direction = Direction.RIGHT
        elif c == curses.KEY_UP:
            head_direction = Direction.UP
        elif c == curses.KEY_DOWN:
            head_direction = Direction.DOWN

        head_pos = head.coord

        # check borders
        if (head_pos.y < 1 or
                head_pos.y > LINES - 2 or
                head_pos.x < 1 or
                head_pos.x > COLS - 2):
            exit(1)

        # check self collision
        if head_pos in [p.coord for p in snake[1:]]:
            exit(1)

        # check prize
        if head_pos in [p.coord for p in prizes]:
            add_new_part(snake)
            prizes.remove(Prize(head_pos, '$'))

        snake = move_snake(snake, head_direction)


class TestSnake(unittest.TestCase):

    def test_add_part(self):
        test = [SnakePart(Coord(1, 1), 'x')]
        expected = [
            SnakePart(Coord(1, 1), 'x'),
            SnakePart(None, '0'),
        ]
        add_new_part(test)
        self.assertEqual(expected, test)

    def test_move_head(self):
        test = [SnakePart(Coord(1, 1), 'x')]
        expected = [SnakePart(Coord(1, 0), 'x')]
        self.assertEqual(expected, move_snake(test, head_direction=Direction.LEFT))

    def test_move_2(self):
        test = [
            SnakePart(Coord(1, 1), 'x'),
            SnakePart(Coord(1, 2), '0'),
        ]
        expected = [
            SnakePart(Coord(1, 0), 'x'),
            SnakePart(Coord(1, 1), '0')
        ]
        self.assertEqual(expected, move_snake(test, head_direction=Direction.LEFT))


if __name__ == '__main__':
    # unittest.main()
    wrapper(main)
