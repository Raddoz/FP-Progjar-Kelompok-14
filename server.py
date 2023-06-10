import socket
import threading


class TicTacToeServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.current_player = "X"

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(2)
        print("Server started. Waiting for connections...")

        while True:
            client_socket, address = self.server_socket.accept()
            self.clients.append(client_socket)
            print("Client connected:", address)

            if len(self.clients) == 2:
                threading.Thread(target=self.handle_client, args=(self.clients[0],)).start()
                threading.Thread(target=self.handle_client, args=(self.clients[1],)).start()
                break

    def handle_client(self, client_socket):
        client_socket.sendall(self.current_player.encode())
        self.current_player = "O" if self.current_player == "X" else "X"

        try:
            while True:
                move = client_socket.recv(1024).decode()
                if move == "exit":
                    break

                player, row, col =  move.split(",") 
                row, col = int(row), int(col)

                print("Player {} moved to ({}, {}) {}".format(player, row, col, self.current_player))

                if self.board[row][col] == " " and player == self.current_player:
                    self.board[row][col] = self.current_player
                    self.current_player = "O" if self.current_player == "X" else "X"
                    self.broadcast_board()
                    print(self.board)
        except socket.error:
            pass

        self.clients.remove(client_socket)
        client_socket.close()
        print("Client disconnected")

    def broadcast_board(self):
        board_str = ""
        for row in self.board:
            board_str += ",".join(row) + "\n"

        for client_socket in self.clients:
            client_socket.sendall(board_str.encode())

    def close(self):
        for client_socket in self.clients:
            client_socket.sendall("exit".encode())
            client_socket.close()

        self.server_socket.close()


if __name__ == "__main__":
    server = TicTacToeServer("localhost", 9001)
    try:
        server.start()
    except KeyboardInterrupt:
        server.close()
