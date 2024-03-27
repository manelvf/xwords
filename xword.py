from copy import deepcopy
from pprint import pp
import random
import sqlite3


RANDOM_WORD = "SELECT word FROM words WHERE rowid=(?)"
TOTAL_WORDS = "SELECT COUNT(*) FROM words"

COLS = 7
ROWS = 10

TOTAL_LETTERS = 50

word_list = []


class Tilt:
    VERTICAL = 0
    HORIZONTAL = 1


board = []
for i in range(ROWS):
    board.append([None] * COLS)


new_board = deepcopy(board)


def main():
    global board, new_board

    orientation = Tilt.VERTICAL

    cursor, conn = init_db()

    res = cursor.execute(TOTAL_WORDS)
    total_words = res.fetchone()[0]
    print(f"Total words {total_words}")

    wx = None
    wy = None

    i = 10000
    while i:
        i -= 1

        rowid = random.randint(0, total_words - 1)

        res = cursor.execute(RANDOM_WORD, (rowid,))
        result = res.fetchone()
        if not result:
            continue

        word = result[0]
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

            place_vertical(wx, wy, word)

        else:
            words = [word for word, word_orientation, _ in word_list]
            if word in words:
                continue

            found, coords = place_word_random(word, orientation)
            if not found:
                continue

            wx = coords[0]
            wy = coords[1]

        word_list.append((word, orientation, (wx, wy)))

        board = deepcopy(new_board)

        total = calculate_filling()
        print(f"Total {total}")

        if total > TOTAL_LETTERS:
            break

        orientation = (orientation + 1) % 2

    pp(board)
    pp(word_list)


def place_word_random(word, orientation):
    print(f"Random: {word} {orientation}")
    if orientation == Tilt.VERTICAL:
        return place_word_vertical(word)
    else:
        return place_word_horizontal(word)


def place_word_horizontal(word):
    global new_board, board

    print("Place word horizontally\n")
    for i in range(ROWS):
        for j in range(COLS):
            if len(word) + j > COLS:
                break

            new_board = [row[:] for row in board]

            found = place_horizontal(i, j, word)
            if found:
                return True, (i, j)

    return False, None


def place_word_vertical(word):
    global new_board, board

    for i in range(COLS):
        for j in range(ROWS):
            if (len(word) + j) > ROWS:
                break

            new_board = [row[:] for row in board]

            found = place_vertical(i, j, word)
            if found:
                return True, (j, i)

    return False, None


def place_vertical(x, y, word):
    global board, new_board

    ymax = y + len(word)
    print("Ymax:")
    print(ymax)
    if ymax >= ROWS:
        return False

    found = False

    if check_head_vertical(x, y):
        return False

    c = y
    for i in word:
        letter = board[c][x]

        if letter:
            if i != letter:
                return False

            found = True

        if check_tail_vertical(x, y):
            return False

        new_board[c][x] = i
        c += 1

    return found


def place_horizontal(x, y, word):
    global board, new_board

    print(f"Placing horizontally {x} {y} {word}")

    xmax = x + len(word)
    print(f"Xmax: {xmax}")
    if xmax >= COLS:
        return False

    found = False

    if check_head_horizontal(x, y):
        return False

    c = x

    for i in word:
        letter = board[y][c]

        if letter:
            if i != letter:
                return False

            found = True
        else:
            if check_tail_horizontal(x, y):
                return False

        new_board[y][c] = i
        c += 1

    return found


def check_head_vertical(x, y):
    global board

    ym = y-1
    xm = x-1
    xp = x+1

    if ym >=0 and board[ym][x]:
        return True

    if xm >= 0 and board[y][xm]:
        return True

    if xp < COLS and board[y][xp]:
        return True

    return False


def check_tail_vertical(x, y):
    global board

    yp = y+1
    xm = x-1
    xp = x+1

    if yp < ROWS and board[yp][x]:
        return True

    if xm >= 0 and board[y][xm]:
        return True

    if xp < COLS and board[y][xp]:
        return True

    return False

def check_head_horizontal(x, y):
    global board

    ym = y-1
    yp = y+1
    xm = x-1

    if ym >= 0 and board[ym][x]:
        return True

    if yp < ROWS and board[yp][x]:
        return True

    if xm >= 0 and board[y][xm]:
        return True

    return False


def check_tail_horizontal(x, y):
    global board

    ym = y-1
    yp = y+1
    xp = x+1

    if ym > 0 and board[ym][x]:
        return True

    if yp < ROWS and board[yp][x]:
        return True

    if xp < COLS and board[y][xp]:
        return True

    return False


def calculate_filling():
    total = 0
    for col in board:
        for row in col:
            if row:
                total += 1

    return total


def init_db():
    conn = sqlite3.connect("dicionario.db")
    cursor = conn.cursor()

    return cursor, conn


if __name__ == "__main__":
    main()