import socket, select, queue

class Server:
    def __init__(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setblocking(0)
        self.socket.bind((ip, port))
        self.socket.listen(5)
        self.address = f"{ip}:{port}"
        self.in_sockets = [self.socket]
        self.out_sockets = []
        self.msg_queues = {}

    def __repr__(self):
        return "< Server running on {self.address} >"

    def run(self):
        running = True
        while running:
            try:
                readable, writable, exceptional = select.select(self.in_sockets,
                                                self.out_sockets, self.in_sockets)

                for s in readable:
                    if s is self.socket:
                        self.accept_client(s)
                    else:
                        self.receive_msg(s)

                for s in writable:
                    self.send_msg(s)

                for s in exceptional:
                    self.discard_socket(s)

            except KeyboardInterrupt:
                self.shut_down()
                running = False

    def discard_socket(self, socket):
        self.in_sockets.remove(socket)
        if socket in self.out_sockets:
            self.out_sockets.remove(socket)
        socket.close()
        del self.msg_queues[socket]

    def accept_client(self, socket):
        conn, client_ip = socket.accept()
        conn.setblocking(0)
        self.in_sockets.append(conn)
        self.msg_queues[conn] = queue.Queue()

    def send_msg(self, socket):
        next_msg = self.msg_queues[socket].get_nowait()
        print(f"message received: {next_msg}")
        socket.send(next_msg.upper())
        self.out_sockets.remove(socket)

    def receive_msg(self, socket):
        msg = socket.recv(64)
        if msg:
            self.msg_queues[socket].put(msg)
            self.out_sockets.append(socket)
        else:
            self.discard_socket(socket)

    def shut_down(self):
        for s in set(self.in_sockets + self.out_sockets):
            s.close()
        print("Shutting down server...")

if __name__ == "__main__":
    server = Server('127.0.0.1', 8000)
    server.run()
