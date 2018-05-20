import socket, select, queue

def server(ip, port):
    # create TCP socket for server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # set the socket to be non-blocking
    server.setblocking(0)
    # bind the socket to the IP and port provided in function call
    server.bind((ip, port))
    # set server to listen to incoming client connections
    server.listen(5)
    # create two lists - inputs and outputs, first will be used to store all
    # sockets pending reading action (receive message) and second writing action
    # (send message)
    ins, outs = [server], []
    # create dictionary for storing messages to action
    msg_queues = {}

    # client serving functionality is implemented as endless while loop that can
    # be ended by keyboard interrupt (ctrl + c) and hence try, except
    running = True
    while running:
        try:
            # select.select uses os(unix) select system call to check if sockets
            # in supplied ins/outs lists are ready for reading/writing or
            # in exceptional state, as no parameter for timeot is selected this
            # call blocks further program execution until one of the sockets is
            # ready, 4th optional parameter might be passed in to specify timeout,
            # if set to 0, call will only check immediate status of sockets
            readable, writable, exceptional = select.select(
                    ins, outs, ins)
            # loop through all sockets readable sockets
            for s in readable:
                # for server perform actions to accept incoming client connection,
                # set it to nonblocking, assing it to ins list and create message
                # queue in message queues dictionary
                if s is server:
                    conn, client_ip = s.accept()
                    conn.setblocking(0)
                    ins.append(conn)
                    msg_queues[conn] = queue.Queue()
                # for non server socket
                else:
                    # receive message data from socket
                    msg = s.recv(64)
                    # if message exists, put it into corresponing queue
                    if msg:
                        msg_queues[s].put(msg)
                        # append socket into outs list, so it can be checked
                        # for writable in next iteration
                        outs.append(s)
                    # else remove socket from ins and outs, close it and delete
                    # coresponding message queue
                    else:
                        if s in outs:
                            outs.remove(s)
                        ins.remove(s)
                        s.close()
                        del msg_queues[s]
            # for writbale sockets, get message from corresponging message queue,
            # send mesage back to client - converted to upper case and remove
            # socket from outs as the message is processed and there is no need
            # to keep it in there until new message is received
            for s in writable:
                next_msg = msg_queues[s].get_nowait()
                print(f"message received: {next_msg}")
                s.send(next_msg.upper())
                outs.remove(s)
            # if socket is exceptional/erronous delete it, close socket and delete
            # corrensponing message queue
            for s in exceptional:
                ins.remove(s)
                if s in outs:
                    outs.remove(s)
                s.close()
                del msg_queues[s]

        except KeyboardInterrupt:
            # close all sockets that are in ins/outs lists
            for s in set(ins + outs):
                s.close()
            running = False
            print("Shutting down server")

if __name__ == "__main__":
    server('127.0.0.1', 8000)
