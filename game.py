import curses
import time

def print_board(stdscr, board, cursor_pos, show_cursor):
    stdscr.clear()
    stdscr.addstr("---------\n")
    for row_index, row in enumerate(board):
        stdscr.addstr("| ")
        for col_index, cell in enumerate(row):
            if cursor_pos == (row_index, col_index) and show_cursor:
                stdscr.addstr("_ ")
            else:
                stdscr.addstr(f"{cell} ")
        stdscr.addstr("|\n")
        stdscr.addstr("---------\n")


def move_cursor(cursor_pos, direction):
    row, col = cursor_pos
    if direction == "up":
        row = max(0, row - 1)
    elif direction == "down":
        row = min(2, row + 1)
    elif direction == "left":
        col = max(0, col - 1)
    elif direction == "right":
        col = min(2, col + 1)
    return row, col


def get_move(stdscr):
    key = stdscr.getch()
    if key == curses.KEY_ENTER or key in [10, 13]:
        return "enter"
    elif key == curses.KEY_UP:
        return "up"
    elif key == curses.KEY_DOWN:
        return "down"
    elif key == curses.KEY_LEFT:
        return "left"
    elif key == curses.KEY_RIGHT:
        return "right"
    elif key == -1:
        stdscr.refresh()
    else:
        stdscr.addstr("Invalid input. Please use arrow keys or press Enter.\n")


def check_winner(board):
    # Check rows
    for row in board:
        if row[0] == row[1] == row[2] != " ":
            return row[0]

    # Check columns
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != " ":
            return board[0][col]

    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] != " ":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != " ":
        return board[0][2]

    return None


def is_board_full(board):
    for row in board:
        if " " in row:
            return False
    return True


def play_game(stdscr):
    board = [[" " for _ in range(3)] for _ in range(3)]
    cursor_pos = (0, 0)
    current_player = "X"

    stdscr.nodelay(True)
    stdscr.keypad(True)

    show_cursor = True

    delta_sec = 0
    current_time = time.time()

    while True:
        delta_sec = time.time() - current_time
        if delta_sec > 0.5:
            current_time = time.time()
            show_cursor = not show_cursor

        print_board(stdscr, board, cursor_pos, show_cursor)
        stdscr.addstr("Current player: {}\n".format(current_player))

        move = get_move(stdscr)

        if move == "enter":
            row, col = cursor_pos
            if board[row][col] == " ":
                board[row][col] = current_player
                winner = check_winner(board)
                if winner:
                    print_board(stdscr, board, cursor_pos, show_cursor)
                    stdscr.addstr("Player {} wins!\n".format(winner))
                    break

                if is_board_full(board):
                    print_board(stdscr, board, cursor_pos, show_cursor)
                    stdscr.addstr("It's a tie!\n")
                    break

                current_player = "O" if current_player == "X" else "X"
        else:
            cursor_pos = move_cursor(cursor_pos, move)


def main(stdscr):
    curses.curs_set(0)
    try:
        play_game(stdscr)
    except curses.error:
        pass
    stdscr.refresh()
    stdscr.getch()


curses.wrapper(main)
