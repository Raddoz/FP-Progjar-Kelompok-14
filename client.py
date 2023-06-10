import socket
import curses
import threading
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


def play_game(stdscr, client_socket):
    global board
    board = [[" " for _ in range(3)] for _ in range(3)]
    cursor_pos = (0, 0)
    current_player = "X"
    show_cursor = True

    stdscr.nodelay(True)
    stdscr.keypad(True)

    prev_time = time.time()
    delta_sec = 0

    threading.Thread(target=receive_board_updates, args=(stdscr, client_socket, board)).start()

    while True:
        delta_sec += time.time() - prev_time
        prev_time = time.time()
        if delta_sec >= 0.5:
            show_cursor = not show_cursor
            delta_sec = 0
            
        print_board(stdscr, board, cursor_pos, show_cursor)
        stdscr.addstr("Curret player: {}\n".format(current_player))

        move = get_move(stdscr)

        if move == "enter":
            row, col = cursor_pos
            if board[row][col] == " ":
                board[row][col] = current_player
                client_socket.sendall("{},{}".format(row, col).encode())

                winner = check_winner(board)
                if winner:
                    print_board(stdscr, board, cursor_pos, show_cursor)
                    stdscr.addstr("Player {} wins!\n".format(winner))
                    stdscr.refresh()
                    break

                if is_board_full(board):
                    print_board(stdscr, board, cursor_pos, show_cursor)
                    stdscr.addstr("It's a tie!\n")
                    stdscr.refresh()
                    break

                current_player = "O" if current_player == "X" else "X"
        else:
            cursor_pos = move_cursor(cursor_pos, move)

def receive_board_updates(stdscr, client_socket, board):
    while True:
        data = client_socket.recv(1024).decode()
        if data == "exit":
            break

        new_board = [row.split(",") for row in data.split("\n")]
        new_board = new_board[:3]

        for i in range(3):
            for j in range(3):
                board[i][j] = new_board[i][j]

        stdscr.clear() 
        print_board(stdscr, board, (0, 0), True)
        stdscr.refresh()


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


def main(stdscr):
    curses.curs_set(0)
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("localhost", 9001))
        play_game(stdscr, client_socket)
    except socket.error as e:
        print("Socket error:", e)
    finally:
        client_socket.sendall("exit".encode())
        client_socket.close()
        stdscr.refresh()
        stdscr.getch()


curses.wrapper(main)
