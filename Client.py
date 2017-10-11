import socket
import os.path
import time


def make_request(socket, input):
    args = input.split(" ", 1)
    if args[0].upper() == "DOWNLOAD":
        if os.path.isfile(args[1]):
            input += " " + repr(os.stat(args[1]).st_size)
        else:
            input += " 0"
    socket.send((input + "\r\n").encode("utf-8"))


def analyze_server_answer(answer, message):
    args = answer[0:5]
    if args == b'TRUE ':
        filename = message.split(" ", 2)[1]
        file = open(filename, "ab")
        file.write(answer[5:])
        file.close()
        return True
    elif args == b'FALSE':
        print("File loaded.")
        return False
    else:
        print(answer.decode("utf-8").strip())
        return False


def reconnect(m_socket, addr):
    print("Network error. Try to reconnect...")
    m_socket.close()
    m_socket = socket.socket(socket.AF_INET,
                             socket.SOCK_STREAM,
                             socket.IPPROTO_TCP)
    counter = 30
    while counter > 0:
        print("Cycle...")
        try:
            m_socket.connect(addr)
        except ConnectionRefusedError:
            counter -= 1
            time.sleep(1)
        else:
            break
    return m_socket


clientSocket = socket.socket(socket.AF_INET,
                             socket.SOCK_STREAM,
                             socket.IPPROTO_TCP)
try:
    clientSocket.connect(("127.0.0.1", 6000))
    clientSocket.settimeout(30)

    while 1:
        message = input(">")
        result = True
        while result:
            try:
                make_request(clientSocket, message)
                answer = b''
                while True:
                    packet = clientSocket.recv(1024 * 1024)
                    if packet[-3:] == b'END':
                        answer += packet[:-3]
                        break
                    else:
                        answer += packet
                result = analyze_server_answer(answer, message)
            except socket.timeout:
                clientSocket = reconnect(clientSocket, ("127.0.0.1", 6000))
            except ConnectionResetError:
                clientSocket = reconnect(clientSocket, ("127.0.0.1", 6000))
except ConnectionRefusedError:
    print("Can't connect to server.")
except OSError:
    print("Can't reconnect to server.")
finally:
    clientSocket.close()
