import socket

def client(address):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address))
    running = True
    while running:
        try:
            message = input("Your message (max 64 chars): ")
            if len(message) > 64:
                print("Message longer than 64 chars, try again")
                continue
            s.sendall(message.encode('ascii'))
            response = s.recv(64).decode('ascii')
            print(f"response: {response}")
        except KeyboardInterrupt:
            running = False

    s.close()
    print("Client shut down")

if __name__ == "__main__":
    client(('127.0.0.1', 8000))
