import curses
from random import randrange, choice
from collections import defaultdict

# 定义动作，一共6个动作
actions = ['Up', 'Left', 'Down', 'Right', 'Restart', 'Exit']
# 列表生成器，返回对应字符的ascii码，对应键盘键值
letter_codes = [ord(ch) for ch in 'WASDRQwasdrq']
# 关联动作与键盘键值的字典
actions_dict = dict(zip(letter_codes, actions*2))


# 获取键盘输入，当键盘输入在字典里时返回对应的动作
def get_user_action(keyboad):
    char = "N"
    while char not in actions_dict:
        char = keyboad.getch()
    return actions_dict[char]

# 将矩阵上下对调


def transpose(field):
    return [list(row) for row in zip(*field)]


# 将矩阵左右对调
def invert(field):
    return [row[::-1] for row in field]

# 定义游戏棋盘类


class GameField(object):
    def __init__(self, height=4, width=4, win=2048):
        self.height = height
        self.width = width
        self.win_value = win
        self.score = 0
        self.highscore = 0
        self.reset()
    # 每次随机在空格子上放置4或者2

    def spawn(self):
        # 随机选取2或4，2的概率占90%
        new_element = 4 if randrange(100) > 89 else 2
        # 随机选取一个空格子
        (i, j) = choice([(i, j) for i in range(self.width)
                         for j in range(self.height) if self.field[i][j] == 0])
        # 将空格子赋值为2或4
        self.field[i][j] = new_element
    # 棋盘重置，设置最高分，当前分数清零，所有格子数字清空

    def reset(self):
        if self.score > self.highscore:
            self.highscore = self.score
        self.score = 0
        #格子初始话矩阵为[[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.field = [[0 for i in range(self.width)] for j in
                      range(self.height)]
        self.spawn()
        self.spawn()

    def move(self, direction):
        def move_row_left(row):
            def tighten(row):
                # 每一行进行左移，先去掉为0的行，再在右边补0
                new_row = [i for i in row if i != 0]
                new_row += [0 for i in range(len(row) - len(new_row))]
                return new_row
            # 合并算法，将一致的合并到一起

            def merge(row):
                pair = False
                new_row = []
                for i in range(len(row)):
                    if pair:
                        new_row.append(2 * row[i])
                        self.score += 2*row[i]
                        pair = False
                    else:
                        if i + 1 < len(row) and row[i] == row[i+1]:
                            pair = True
                            new_row.append(0)
                        else:
                            new_row.append(row[i])
                # 断言检查新生成的row长度是否正确
                assert len(new_row) == len(row)
                return new_row
            return tighten(merge(tighten(row)))
        moves = {}
        moves['Left'] = lambda field: [
            move_row_left(row) for row in field]
        moves['Right'] = lambda field: invert(
            moves['Left'](invert(field)))
        moves['Up'] = lambda field: transpose(
            moves['Left'](transpose(field)))
        moves['Down'] = lambda field: transpose(
            moves['Right'](transpose(field)))
        if direction in moves:
            if self.move_is_possible(direction):
                self.field = moves[direction](self.field)
                self.spawn()
                return True
            else:
                return False

    def draw(self, screen):
        help_string1 = '(W)Up (S)Down (A)Left (D)Right'
        help_string2 = '     (R)Restart (Q)Exit'
        gameover_string = '          GAME OVER'
        win_string = '          YOU WIN'

        def cast(string):
            screen.addstr(string + '\n')

        def draw_hor_separator():
            line = '+' + ('+------' * self.width + '+')[1:]
            # defaultdict使用工厂函数构造字典的默认值，当字典separator匹配不到时，默认返回line
            #separator = defaultdict(lambda: line)
            cast(line)

        def draw_row(row):
            cast(''.join('|{:^5} '.format(num) if num >
                         0 else '|      ' for num in row)+'|')
        screen.clear()

        cast('SCORE: ' + str(self.score))
        if 0 != self.highscore:
            cast('HIGHSCORE: ' + str(self.highscore))

        for row in self.field:
            draw_hor_separator()
            draw_row(row)

        draw_hor_separator()

        if self.is_win():
            cast(win_string)
        else:
            if self.is_gameover():
                cast(gameover_string)
            else:
                cast(help_string1)
        cast(help_string2)

    def move_is_possible(self, direction):
        def row_is_left_movable(row):
            def change(i):
                if row[i] == 0 and row[i+1] != 0:
                    return True
                if row[i] != 0 and row[i+1] == row[i]:
                    return True
                return False
            return any(change(i) for i in range(len(row) - 1))

        check = {}

        check['Left'] = lambda field: any(
            row_is_left_movable(row) for row in field)
        check['Right'] = lambda field: check['Left'](invert(field))
        check['Up'] = lambda field: check['Left'](transpose(field))
        check['Down'] = lambda field: check['Right'](transpose(field))

        if direction in check:
            return check[direction](self.field)
        else:
            return False

    def is_win(self):
        return any(any(i >= self.win_value for i in row) for row in self.field)
    # game is over if no possible moves on field

    def is_gameover(self):
        return not any(self.move_is_possible(move) for move in actions)


def main(stdscr):
    def init():
        game_field.reset()
        return 'Game'

    def not_game(state):
        game_field.draw(stdscr)
        action = get_user_action(stdscr)
        responses = defaultdict(lambda: state)
        responses['Restart'], responses['Exit'] = 'Init', 'Exit'
        return responses[action]

    def game():
        game_field.draw(stdscr)
        action = get_user_action(stdscr)
        if action == 'Restart':
            return 'Init'
        if action == 'Exit':
            return 'Exit'
        if game_field.move(action):
            if game_field.is_win():
                return 'Win'
            if game_field.is_gameover():
                return 'Gameover'
        return 'Game'

    state_actions = {
        'Init': init,
        'Win': lambda: not_game('Win'),
        'Gameover': lambda: not_game('Gameover'),
        'Game': game
    }

    curses.use_default_colors()
    game_field = GameField(win=64)
    state = 'Init'

    while state != 'Exit':
        state = state_actions[state]()


curses.wrapper(main)
