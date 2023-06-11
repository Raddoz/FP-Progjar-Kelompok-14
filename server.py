import socket
import select
import threading
import asyncio


class GameRoom:
    def __init__(self, room_number):
        self.room_number = room_number
        self.clients = []
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.current_player = "X"

    def add_client(self, client_socket):
        self.clients.append(client_socket)

    def remove_client(self, client_socket):
        self.clients.remove(client_socket)

    def broadcast_board(self):
        board_str = ""
        for row in self.board:
            board_str += ",".join(row) + "\n"

        for client_socket in self.clients:
            client_socket.sendall(board_str.encode())

            print("Sent board to client in room", self.room_number)
        

    def handle_move(self, player, row, col):
        if self.board[row][col] == " " and player == self.current_player:
            self.board[row][col] = self.current_player
            self.current_player = "O" if self.current_player == "X" else "X"
            self.broadcast_board()


class TicTacToeServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.game_rooms = []
        self.next_room_number = 1

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(2)
        print("Server started. Waiting for connections...")

        sockets = [self.server_socket]

        while True:
            read_ready, _, _ = select.select(sockets, [], [])

            for socket in read_ready:
                if socket == self.server_socket:
                    client_socket, address = socket.accept()    
                
                    print("Client connected:", address)

                    room_number = self.next_room_number
                    if len(self.game_rooms) == 0 or len(self.game_rooms[-1].clients) == 2:
                        game_room = GameRoom(room_number)
                        self.game_rooms.append(game_room)

                        print("Created new room", room_number)
                    else:
                        game_room = self.game_rooms[-1]
                        self.next_room_number += 1

                        print("Added client to room", room_number)


                    game_room.add_client(client_socket)
                    client_socket.sendall(str(room_number).encode())

                    if len(game_room.clients) == 2:
                        threading.Thread(target=self.handle_game_room, args=(game_room,)).start()

    def handle_game_room(self, game_room):
        player_symbols = ["O", "X"]

        for i, client_socket in enumerate(game_room.clients):
            client_socket.sendall(player_symbols[i].encode())

        for client_socket in game_room.clients:
            threading.Thread(target=self.handle_client, args=(game_room, client_socket)).start()

    def handle_client(self, game_room, client_socket):
        try:
            while True:
                move = client_socket.recv(1024).decode()
                if move == "exit":
                    break

                player, row, col = move.split(",")
                row, col = int(row), int(col)

                print("Player {} in room {} moved to ({}, {})".format(player, game_room.room_number, row, col))
                game_room.handle_move(player, row, col)

        except socket.error:
            pass

        for client_socket in game_room.clients:
            game_room.remove_client(client_socket)
            client_socket.close()
            print("Client disconnected from room", game_room.room_number)

        self.game_rooms.remove(game_room)

    def close(self):
        for game_room in self.game_rooms:
            for client_socket in game_room.clients:
                client_socket.sendall("exit".encode())
                client_socket.close()

        self.server_socket.close()


if __name__ == "__main__":
    server = TicTacToeServer("localhost", 9001)
    try:
        server.start()
    except KeyboardInterrupt:
        server.close()
