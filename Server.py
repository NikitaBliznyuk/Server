import socket
import os.path
from datetime import datetime


def send_message(socket, message):
    socket.sendall(message.encode("utf-8") + b'END')


def parse(conn):  # обработка соединения в отдельной функции
    data = b""

    while not b"\r\n" in data:  # ждём первую строку
        try:
            tmp = conn.recv(1024)
        except socket.error:
            break
        else:
            if not tmp:  # сокет закрыли, пустой объект
                break
            else:
                data += tmp

    udata = data.decode("utf-8").strip()

    if len(udata) == 0:
        return

    try:
        command, other = udata.split(" ", 1)
    except ValueError:
        if udata.upper() == "TIME":
            time(conn)
        elif udata.upper() == "CLOSE":
            print("Closed")
            conn.close()
        else:
            no_such_command(conn)
    else:
        if command.upper() == "ECHO":
            echo(conn, (other + "\r\n").encode("utf-8"))
        elif command.upper() == "DOWNLOAD":
            download(conn, other)
        else:
            no_such_command(conn)


def echo(conn, data):
    conn.sendall(data)
    conn.send(b'END')


def time(conn):
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    send_message(conn, date + "\r\n")


def no_such_command(conn):
    send_message(conn, "No such command\r\n")


def download(conn, command):
    args = command.split(" ", 1)
    filename = "Downloads/" + args[0]
    if not os.path.isfile(filename):
        send_message(conn, "No such file.")
    elif os.stat(filename).st_size > int(args[1]):
        file = open(filename, 'rb')
        file.seek(int(args[1]))
        part = file.read(1024 * 256)
        conn.sendall(b"TRUE " + part + b'END')
        file.close()
    else:
        send_message(conn, "FALSE")


# main
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind(("", 6000))
serverSocket.listen(5)
serverSocket.setblocking(0)
clientSockets = []

try:
    while 1:
        try:
            conn, addr = serverSocket.accept()
        except socket.error:
            for s in clientSockets:
                if s.fileno() != -1:
                    parse(s)
                else:
                    clientSockets.remove(s)
        else:
            conn.setblocking(0)
            clientSockets.append(conn)
finally:
    for s in clientSockets:
        s.close()
    serverSocket.close()
