# -*- coding: utf-8 -*-

import curses
from collections import defaultdict
from random import randrange, choice

actions = ['Left', 'Right', 'Up', 'Down', 'Restart', 'Exit']
letters = [ord(i) for i in 'adwsqeADWSQE']
# 两个list合成dict
actions_letter = dict(zip(letters, actions*2))


def get_user_action(keyboad):
    char = 'N'
    while char not in actions_letter:
        char = keyboad.getch()
    return actions_letter[char]


def transpose(field):
    return [list(row) for row in zip(*field)]


def invert(field):
    return [row[::-1] for row in field]


class Game_Field(object):
    def __init__(self, wid=4, hei=4, win=2048):
        self.width = wid
        self.height = hei
        self.win_value = win
        self.score = 0
        self.heighscore = 0
        self.reset()

    def reset(self):
        if self.score > self.heighscore:
            self.heighscore = self.score
        self.score = 0
        self.field = [[0 for i in range(self.width)]
                      for j in range(self.height)]
        self.spawn()
        self.spawn()

    def spawn(self):
        s = 4 if randrange(100) > 89 else 2
        (i, j) = choice([(i, j) for i in range(self.width)
                         for j in range(self.height) if self.field[i][j] == 0])
        self.field[i][j] = s

    def move_is_possible(self, direction):
        def row_left_movable(row):
            def change(i):
                if row[i] == 0 and row[i+1] != 0:
                    return True
                if row[i] != 0 and row[i] == row[i+1]:
                    return True
                else:
                    return False
            return any(change(i) for i in range(len(row) - 1))

        checks = {}
        checks['Left'] = lambda field: any(
            row_left_movable(row) for row in field)
        checks['Right'] = lambda field: checks['Left'](invert(field))
        checks['Up'] = lambda field: checks['Left'](transpose(field))
        checks['Down'] = lambda field: checks['Right'](transpose(field))
        if direction in checks:
            return checks[direction](self.field)
        else:
            return False

    def move(self, direction):
        def move_row_left(row):
            def tig(row):
                new_row = [i for i in row if i > 0]
                new_row += [0 for i in range(len(row)-len(new_row))]
                return new_row

            def merge(row):
                pair = False
                new_row = []
                for i in range(len(row)):
                    if pair:
                        new_row.append(row[i]*2)
                        pair = False
                        self.score += row[i]*2
                    else:
                        if i < len(row)-1 and row[i] == row[i+1]:
                            new_row.append(0)
                            pair = True
                        else:
                            new_row.append(row[i])
                assert len(new_row) == len(row)
                return new_row
            return tig(merge(tig(row)))

        moves = {}
        moves['Left'] = lambda field: [move_row_left(row) for row in field]
        moves['Right'] = lambda field: invert(moves['Left'](invert(field)))
        moves['Up'] = lambda field: transpose(moves['Left'](transpose(field)))
        moves['Down'] = lambda field: transpose(
            moves['Right'](transpose(field)))

        if direction in moves:
            if self.move_is_possible(direction):
                self.field = moves[direction](self.field)
                self.spawn()
                return True
            else:
                return False

    def is_win(self):
        return any(any(i > self.win_value for i in row) for row in self.field)

    def is_gameover(self):
        return not any(self.move_is_possible(action) for action in actions)

    def draw(self, screen):
        help_string = 'Left(A),Right(D),Up(W),Down(S)'
        help_string1 = '     Restart(Q),Exit(E)'
        win_string = 'You Win!'
        gameover_string = 'Gameover'

        def cast(string):
            screen.addstr(string + '\n')

        def draw_row_seprator():
            line = '+' + ('+-----'*self.width+'+')[1:]
            separator = defaultdict(lambda: line)
            if not hasattr(draw_row_seprator, "countor"):
                draw_row_seprator.countor = 0
            cast(separator[draw_row_seprator.countor])
            draw_row_seprator.countor += 1

        def draw_row(row):
            cast(''.join('|{:^5}'.format(num) if num >
                         0 else '|     ' for num in row)+'|')

        screen.clear()
        cast('score:' + str(self.score))
        for row in self.field:
            draw_row_seprator()
            draw_row(row)
        draw_row_seprator()
        if self.is_win():
            cast(win_string)
        else:
            if self.is_gameover():
                cast(gameover_string)
            else:
                cast(help_string)
        cast(help_string1)


def main(stdsrc):
    def init():
        gamefield.reset()
        return 'Game'

    def not_game(state):
        gamefield.draw(stdsrc)
        action = get_user_action(stdsrc)
        response = defaultdict(lambda: state)
        response['Restart'], response['Exit'] = 'Init', 'Exit'
        return response[action]

    def game():
        gamefield.draw(stdsrc)
        action = get_user_action(stdsrc)
        if action == 'Restart':
            return 'Init'
        if action == 'Exit':
            return 'Exit'
        if gamefield.move(action):
            if gamefield.is_win():
                return 'Win'
            if gamefield.is_gameover():
                return 'Gameover'
        return 'Game'

    state_action = {'Init': init, 'Win': lambda: not_game(
        'Win'), 'Gameover': lambda: not_game('Gameover'), 'Game': game}

    curses.use_default_colors()
    state = 'Init'
    gamefield = Game_Field(win=2048)
    while state != 'Exit':
        state = state_action[state]()


curses.wrapper(main)
