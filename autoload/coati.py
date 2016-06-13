import threading
import socket
import os.path
import encodings.idna
import vim
import time

try:
    import SocketServer
except ImportError:
    import socketserver as SocketServer

MESSAGE_SPLIT_STRING = ">>"

class Options:
    instance = None
    def __init__(self):
        self.port_vim_to_coati = int(vim.eval('coati#get("vim_to_coati_port")'))
        self.port_coati_to_vim = int(vim.eval('coati#get("coati_to_vim_port")'))
        self.ip = vim.eval('coati#get("coati_ip")')

    @classmethod
    def reload(cls):
        cls.instance = Options()

    @classmethod
    def inst(cls):
        if(cls.instance is None):
            cls.reload()
        return cls.instance

    @classmethod
    def port_vim_to_coati(cls):
        return cls.inst().port_vim_to_coati

    @classmethod
    def port_coati_to_vim(cls):
        return cls.inst().port_coati_to_vim

    @classmethod
    def ip(cls):
        return cls.inst().ip

    @classmethod
    def printSettings(cls):
        print("Coati Settings: \n--------------------")
        print("Ports: ")
        print("g:coati_to_vim_port: " + str(cls.inst().port_coati_to_vim))
        print("g:vim_to_coati_port: " + str(cls.inst().port_vim_to_coati))
        print("Ip: ")
        print("g:coati_ip         : " + cls.inst().ip)
        print("--------------------")

class ConnectionHandler(SocketServer.BaseRequestHandler): # This class is instantiated once per connection to the server
    timeout = 5
    def handle(self):
        data = self.request.recv(1024).strip()
        text = data.decode('utf-8')
        eom_index = text.find("<EOM>")
        if (not eom_index == 0):
            message_string = text[0:eom_index]
            message_fields = message_string.split(MESSAGE_SPLIT_STRING)
            if (message_fields[0] == "moveCursor"):
                Coati.setNewBuffer(message_fields[1], int(message_fields[2]), int(message_fields[3]))
        else:
            print("asdfasfd")

class Coati:
    instance = None
    def __init__(self):
        self.__col = 0
        self.__row = 0
        self.__file = ""
        self.__update = False
        self.__server = None

    def __del__(self):
        self.stopServer()

    @classmethod
    def inst(cls):
        if(cls.instance is None):
            cls.instance = Coati()
        return cls.instance

    @classmethod
    def row(cls):
        return cls.inst().__row

    @classmethod
    def col(cls):
        return cls.inst().__col

    @classmethod
    def file(cls):
        return cls.inst().__file

    @classmethod
    def startServer(cls):
        try:
            SocketServer.ThreadingTCPServer.allow_reuse_address = True
            address = ( Options.ip(), Options.port_coati_to_vim())
            cls.inst().__server = SocketServer.ThreadingTCPServer(address, ConnectionHandler);
            server_thread = threading.Thread(target=cls.inst().__server.serve_forever);
            server_thread.daemon = True;
            server_thread.start();
        except socket.error:
            print("Socket needed for Coati plugin already in use")

    @classmethod
    def stopServer(cls):
        if(cls.inst().__server is not None):
            cls.inst().__server.shutdown()
            cls.inst().__server.server_close()

    @classmethod
    def restartServer(cls):
        cls.inst().stopServer()
        Options.reload()
        cls.inst().startServer()

    @classmethod
    def SendActivateToken(cls):
        filePath = vim.current.buffer.name;
        (row, col) = vim.current.window.cursor;

        col += 1 # cols returned by rowcol() are 0-based.

        text = "setActiveToken" + MESSAGE_SPLIT_STRING + filePath + MESSAGE_SPLIT_STRING + str(row) + MESSAGE_SPLIT_STRING + str(col) + "<EOM>"
        data = text.encode()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((Options.ip(), Options.port_vim_to_coati()))
        s.send(data)
        s.close()
        print("Current Position sent to Coati")

    @classmethod
    def setNewBuffer(cls, filePath, row, col):
        cls.inst().__col = col
        cls.inst().__row = row
        cls.inst().__file = filePath
        cls.inst().__update = True

    @classmethod
    def updateBuffer(cls):
        if(cls.inst().__update):
            vim.command("e! " + cls.inst().__file)
            vim.current.window.cursor = (cls.inst().__row, cls.inst().__col)
            cls.inst().__update = False

