import tkinter as tk
import csv
import sys


class BasicRock:
    def __init__(self, Color, isQ, isBlack):
        self.color = Color
        self.isQ = isQ
        self.isBlack = isBlack
        self.isWhite = not isBlack

    def isWhite(self):
        return self.isWhite

    def isBlack(self):
        return self.isBlack

    def getColor(self):
        return self.color

    def getQ(self):
        return self.isQ

    def getOutline(self):
        if self.getQ():
            return "Green"
        else:
            return self.color

    def isHostile(self, enemy):
        if (enemy.isWhite == self.isWhite) or (enemy.isBlack == self.isBlack):
            return False
        else:
            return True


class WhiteRock(BasicRock):
    def __init__(self, isQ):
        super().__init__("Gray", isQ, False)

    def isBlack(self):
        return False

    def isWhite(self):
        return True


class BlackRock(BasicRock):
    def __init__(self, isQ):
        super().__init__("Black", isQ, True)

    def isBlack(self):
        return True

    def isWhite(self):
        return False


# Hlavni okno
root = tk.Tk()
# Velikost policka
SIZE_OF_PIECE = 100
# Tah hrace
TURN = -1

canvas = tk.Canvas(root, width=SIZE_OF_PIECE * 10, height=SIZE_OF_PIECE * 10)
# Pozice hrace
CURRENT_X = -1

CURRENT_Y = -1

TAKE_MOVE_POSSIBLE = False

WINNER = -1
# Index oznacuje mozne tahy
ATTACK_GLOBAL_INDEX = 20

WHITE_TURN = -1

BLACK_TURN = 1


# Vykresli mapu
def draw(map):
    global WINNER
    canvas.delete("all")
    for x, row in enumerate(board):
        for y, column in enumerate(row):
            color = "white"

            if (x + y) % 2 == 1:
                color = "#5c2300"
            if board[y][x] == 1:
                color = "black"
            if map[y][x] == 8 or (int(repr(map[y][x])[-1]) == 0 and map[y][x] > 10):
                color = "green"
            if int(repr(map[y][x])[-1]) == 9:
                color = "red"
            if CURRENT_X == x and CURRENT_Y == y:
                color = "yellow"

            canvas.create_rectangle(SIZE_OF_PIECE * x, SIZE_OF_PIECE * y, SIZE_OF_PIECE * x + 100,
                                    SIZE_OF_PIECE * y + 100,
                                    fill=color)

            if isinstance(board[y][x], BasicRock):
                canvas.create_oval(SIZE_OF_PIECE * x + 10, SIZE_OF_PIECE * y + 10,
                                   SIZE_OF_PIECE * x + SIZE_OF_PIECE - 10,
                                   SIZE_OF_PIECE * y + SIZE_OF_PIECE - 10,
                                   fill=board[y][x].getColor(), outline=(board[y][x]).getOutline(), width=10)

    if TURN == WHITE_TURN:
        canvas.create_rectangle(0, 0, SIZE_OF_PIECE, SIZE_OF_PIECE,
                                fill="White", outline="yellow")
    else:
        canvas.create_rectangle(0, 0, SIZE_OF_PIECE, SIZE_OF_PIECE,
                                fill="Black", outline="yellow")

    # V pripade vyherce
    if WINNER != -1:
        text = "Remiza"
        if WINNER == 1:
            text = "Vyhra Cerne"
        if WINNER == 2:
            text = "Vyhra Bile"
        canvas.create_rectangle(SIZE_OF_PIECE * 2, SIZE_OF_PIECE * 3, SIZE_OF_PIECE * 8, SIZE_OF_PIECE * 7,
                                fill="white")
        canvas.create_text(SIZE_OF_PIECE * 5, SIZE_OF_PIECE * 5, fill="darkblue", font="Times 15 bold",
                           text=text)


# Vypocitá mozne tahy pro figurku na pozici x y
def calculate_moves(x, y, map):
    global TURN, CURRENT_X, CURRENT_Y

    clear_map(map)

    global ATTACK_GLOBAL_INDEX

    ATTACK_GLOBAL_INDEX = 20

    if not isinstance(board[y][x], BasicRock):
        return

    if board[y][x].isBlack and not board[y][x].isQ:
        move_Rock(y, x, 1, 1, map)
        move_Rock(y, x, 1, -1, map)
        CURRENT_X = x
        CURRENT_Y = y

    if board[y][x].isWhite and not board[y][x].isQ:
        move_Rock(y, x, -1, 1, map)
        move_Rock(y, x, -1, -1, map)
        CURRENT_X = x
        CURRENT_Y = y

    if board[y][x].isBlack and board[y][x].isQ:
        for tt in range(-1, 2, 1):
            for rr in range(-1, 2, 1):
                move_Queen(y, x, rr, tt, map)
        CURRENT_X = x
        CURRENT_Y = y

    if board[y][x].isWhite and board[y][x].isQ:
        for tt in range(-1, 2, 1):
            for rr in range(-1, 2, 1):
                move_Queen(y, x, rr, tt, map)
        CURRENT_X = x
        CURRENT_Y = y

    non_killing_move_delete(map)

    for tt in range(8):
        if isinstance(board[1][tt + 1], BasicRock):
            if board[1][tt + 1].isWhite:
                board[1][tt + 1].isQ = True
        if isinstance(board[8][tt + 1], BasicRock):
            if board[8][tt + 1].isBlack:
                board[8][tt + 1].isQ = True


# Hlavni okno
def move_Queen(y, x, w, z, map):
    q = 0
    r = 0
    q += z
    r += w
    global ATTACK_GLOBAL_INDEX

    if (is_enemy(board[y][x], y + w, x + z)) and board[y + w + w][x + z + z] == 0:
        map[y + w][x + z] = ATTACK_GLOBAL_INDEX - 1
        map[y + w + w][x + z + z] = ATTACK_GLOBAL_INDEX
        ATTACK_GLOBAL_INDEX = ATTACK_GLOBAL_INDEX + 10

    while board[y + r][x + q] == 0:
        map[y + r][x + q] = 8
        if (is_enemy(board[y][x], y + r + w, x + q + z)) and board[y + r + w + w][x + q + z + z] == 0:
            map[y + r + w][x + q + z] = ATTACK_GLOBAL_INDEX - 1
            map[y + r + w + w][x + q + z + z] = ATTACK_GLOBAL_INDEX
            ATTACK_GLOBAL_INDEX = ATTACK_GLOBAL_INDEX + 10
        q += z
        r += w


def move_Rock(y, x, w, z, map):
    global ATTACK_GLOBAL_INDEX
    if (is_enemy(board[y][x], y + w, x + z)) and board[y + w + w][x + z + z] == 0:
        map[y + w][x + z] = ATTACK_GLOBAL_INDEX - 1
        map[y + w + w][x + z + z] = ATTACK_GLOBAL_INDEX
        ATTACK_GLOBAL_INDEX = ATTACK_GLOBAL_INDEX + 10

    if board[y + w][x + z] == 0:
        map[y + w][x + z] = 8


def key(event):
    print('pressed', repr(event.char))


def callback(event):
    global TURN, TAKE_MOVE_POSSIBLE, moves

    xr = int(event.x / SIZE_OF_PIECE)
    yr = int(event.y / SIZE_OF_PIECE)
    end_condition_check_none_left()
    print("clicked at", xr, yr)

    if isinstance(board[yr][xr], BasicRock) and CURRENT_X == -1 and board[yr][xr].isBlack and TURN == BLACK_TURN:
        calculate_moves(xr, yr, moves)
    elif isinstance(board[yr][xr], BasicRock) and CURRENT_X == -1 and board[yr][xr].isWhite and TURN == WHITE_TURN:
        calculate_moves(xr, yr, moves)
    elif moves[yr][xr] == 8:
        board[yr][xr] = board[CURRENT_Y][CURRENT_X]
        board[CURRENT_Y][CURRENT_X] = 0
        clear_map(moves)
        TURN *= -1
    elif int(repr(moves[yr][xr])[-1]) == 0 and moves[yr][xr] > 10:
        board[yr][xr] = board[CURRENT_Y][CURRENT_X]
        board[CURRENT_Y][CURRENT_X] = 0
        kill(moves[yr][xr] - 1)
        TAKE_MOVE_POSSIBLE = True
        calculate_moves(xr, yr, moves)
        if non_killing_move_delete(moves) == False:
            clear_map(moves)
            TURN *= -1
            TAKE_MOVE_POSSIBLE = False
    elif yr == CURRENT_Y and xr == CURRENT_X and not TAKE_MOVE_POSSIBLE:
        end_condition_check_no_moves_left()
        clear_map(moves)

    draw(moves)


def clear_map(map):
    global CURRENT_Y, CURRENT_X
    CURRENT_X = -1
    CURRENT_Y = -1
    for z, row in enumerate(map):
        for zz, column in enumerate(row):
            if map[z][zz] > 7:
                map[z][zz] = 0


def non_killing_move_delete(map):
    Red = False
    for z, row in enumerate(board):
        for zz, column in enumerate(row):
            if map[z][zz] > 19:
                Red = True
    if Red:
        for z, row in enumerate(board):
            for zz, column in enumerate(row):
                if map[z][zz] == 8:
                    map[z][zz] = 0
    return Red


def kill(number):
    for z, row in enumerate(board):
        for zz, column in enumerate(row):
            if moves[z][zz] == number:
                board[z][zz] = 0


def is_enemy(me, y, x):
    if isinstance(me, BasicRock) and isinstance(board[y][x], BasicRock):
        return me.isHostile(board[y][x])


def end_condition_check_none_left():
    global WINNER, TURN
    end_condition_fulfill_black = True
    end_condition_fulfill_white = True

    for x, row in enumerate(board):
        for y, column in enumerate(row):
            if isinstance(board[x][y], BasicRock):
                if board[x][y].isBlack:
                    end_condition_fulfill_black = False
                if board[x][y].isWhite:
                    end_condition_fulfill_white = False
    if end_condition_fulfill_black:
        WINNER = 2
    if end_condition_fulfill_white:
        WINNER = 1


def end_condition_check_no_moves_left():
    global WINNER, TURN

    end_condition_fulfill_black = True
    end_condition_fulfill_white = True

    for z, row in enumerate(board):
        for zz, column in enumerate(row):
            if isinstance(board[z][zz], BasicRock):
                if board[z][zz].isWhite:
                    calculate_moves(z, zz, moves)
                    if (max([max(r) for r in moves])) > 7:
                        end_condition_fulfill_black = False
                if board[z][zz].isBlack:
                    calculate_moves(z, zz, moves)
                    if max([max(r) for r in moves]) > 7:
                        end_condition_fulfill_white = False
    clear_map(moves)
    if end_condition_fulfill_black and TURN == WHITE_TURN:
        WINNER = -1
    if end_condition_fulfill_white and TURN == BLACK_TURN:
        WINNER = -1

def to_tuple(square):
    return (ord(square[0]) - 65+1, int(square[1]) - 1 + 1)

if __name__ == '__main__':
    canvas.bind("<Key>", key)
    canvas.bind("<Button-1>", callback)
    board = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
    moves = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

    if len(sys.argv) == 2:
        with open(sys.argv[1]) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')

            for row in csv_reader:

                print(to_tuple(row[0])[0])
                if row[1] == "bb":
                        board[int(to_tuple(row[0])[0])][int(to_tuple(row[0])[1])] = BlackRock(True)
                if row[1] == "b":
                    board[int(to_tuple(row[0])[0])][int(to_tuple(row[0])[1])] = BlackRock(False)
                if row[1] == "ww":
                    board[int(to_tuple(row[0])[0])][int(to_tuple(row[0])[1])] = WhiteRock(True)
                if row[1] == "w":
                    board[int(to_tuple(row[0])[0])][int(to_tuple(row[0])[1])] = WhiteRock(False)

    canvas.pack()
    draw(moves)
    canvas.pack()
    root.mainloop()