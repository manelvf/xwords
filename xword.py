from copy import deepcopy
from pprint import pp
import random
import sqlite3


RANDOM_WORD = "SELECT word FROM words WHERE rowid=(?)"
TOTAL_WORDS = "SELECT COUNT(*) FROM words"

COLS = 9
ROWS = 10

MIN_WORD_LENGTH = 3
TOTAL_LETTERS = 50

word_list = []


class Tilt:
    VERTICAL = 0
    HORIZONTAL = 1


board = []
for i in range(ROWS):
    board.append([None] * COLS)

new_board = []


class TouchError(Exception):
    pass


def init_db():
    conn = sqlite3.connect("dicionario.db")
    cursor = conn.cursor()

    return cursor


class Crossword:
    def __init__(self):
        global board, new_board

        orientation = Tilt.VERTICAL

        cursor = init_db()

        res = cursor.execute(TOTAL_WORDS)
        total_words = res.fetchone()[0]
        print(f"Total words {total_words}")

        wx = None
        wy = None

        new_board = deepcopy(board)

        i = 10000
        while i:
            i -= 1

            rowid = random.randint(0, total_words - 1)

            res = cursor.execute(RANDOM_WORD, (rowid,))
            result = res.fetchone()
            if not result:
                continue

            word = result[0]
            if len(word) < MIN_WORD_LENGTH:
                continue

            word = word.replace("á","a").replace("é", "e").replace("í","i").replace("ó", "o").replace("ú", "u").replace("ü", "u")
            print(f"Word: {word}")

            if orientation == Tilt.VERTICAL and len(word) > ROWS:
                print(f"Word too big {word}")
                continue

            if orientation == Tilt.HORIZONTAL and len(word) > COLS:
                print(f"Word too big {word}")
                continue

            if not word_list:
                wx = int((COLS - 1) / 2)
                wy = int((ROWS - 1) / 2) - (int(len(word) / 2))

                self.place_vertical(wx, wy, word)

            else:
                words = [word for word, word_orientation, _ in word_list]
                if word in words:
                    continue

                found, coords = self.place_word_random(word, orientation)
                if not found:
                    continue

                wx = coords[0]
                wy = coords[1]

            word_list.append((word, orientation, (wx, wy)))

            board = deepcopy(new_board)

            total = self.calculate_filling()
            print(f"Total {total}")

            if total > TOTAL_LETTERS:
                break

            orientation = (orientation + 1) % 2

        pp(board)
        pp(word_list)


    def place_word_random(self, word, orientation):
        print(f"Random: {word} {orientation}")
        if orientation == Tilt.VERTICAL:
            return self.place_word_vertical(word)
        else:
            return self.place_word_horizontal(word)


    def place_word_horizontal(self, word):
        global new_board, board

        print("Place word horizontally\n")
        for i in range(ROWS):
            for j in range(COLS):
                if len(word) + j > COLS:
                    break

                new_board = [row[:] for row in board]

                try:
                    found = self.place_horizontal(i, j, word)
                except TouchError:
                    continue

                if found:
                    return True, (i, j)

        return False, None


    def place_word_vertical(self, word):
        global new_board, board

        for i in range(COLS):
            for j in range(ROWS):
                if (len(word) + j) > ROWS:
                    break

                new_board = [row[:] for row in board]

                try:
                    found = self.place_vertical(i, j, word)
                except TouchError:
                    continue

                if found:
                    return True, (j, i)

        return False, None


    def place_vertical(self, x, y, word):
        global board, new_board

        # new_board = deepcopy(board)

        ymax = y + len(word)
        print("Ymax:")
        print(ymax)
        if ymax >= ROWS:
            return False

        found = False

        self.check_head_vertical(x, y)

        c = y
        for i in word:
            letter = board[c][x]

            if letter:
                if i != letter:
                    return False

                found = True
            else:
                self.check_tail_vertical(x, c)

            new_board[c][x] = i
            c += 1

        if c < ROWS and board[c][x]:
            raise TouchError

        return found


    def place_horizontal(self, x, y, word):
        global board, new_board

        # new_board = deepcopy(board)

        print(f"Placing horizontally {x} {y} {word}")

        xmax = x + len(word)
        print(f"Xmax: {xmax}")
        if xmax >= COLS:
            return False

        found = False

        self.check_head_horizontal(x, y)

        c = x

        for i in word:
            letter = board[y][c]

            if letter:
                if i != letter:
                    return False

                found = True
            else:
                self.check_tail_horizontal(c, y)

            new_board[y][c] = i
            c += 1

        if c < COLS and board[y][c]:
            raise TouchError

        return found


    def check_head_vertical(self, x, y):
        global board, COLS

        ym = y-1
        xm = x-1
        xp = x+1

        if ym >=0 and board[ym][x]:
            raise TouchError

        if xm >= 0 and board[y][xm]:
            raise TouchError

        if xp < COLS and board[y][xp]:
            raise TouchError


    def check_tail_vertical(self, x, y):
        global board, COLS

        xm = x-1
        xp = x+1
        
        if xm >= 0 and board[y][xm]:
            raise TouchError

        if xp < COLS and board[y][xp]:
            raise TouchError


    def check_head_horizontal(self, x, y):
        global board

        ym = y-1
        yp = y+1
        xm = x-1

        if ym >= 0 and board[ym][x]:
            raise TouchError

        if yp < ROWS and board[yp][x]:
            raise TouchError

        if xm >= 0 and board[y][xm]:
            raise TouchError


    def check_tail_horizontal(self, x, y):
        global board

        ym = y-1
        yp = y+1

        if ym > 0 and board[ym][x]:
            raise TouchError

        if yp < ROWS and board[yp][x]:
            raise TouchError

        return False


    def calculate_filling(self):
        total = 0
        for col in board:
            for row in col:
                if row:
                    total += 1

        return total


