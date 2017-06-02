"""Sourcetrail server"""

import socket
import errno
import threading
import os.path
import encodings.idna
import subprocess
import time
import vim

try:
    # Python 3
    import socketserver
except ImportError:
    # Python 2
    import SocketServer as socketserver

MESSAGE_SPLIT_STRING = ">>"

class Options:
    """Option class for sourcetrail"""
    instance = None
    def __init__(self):
        self.port_vim_to_sourcetrail = int(vim.eval('sourcetrail#get("vim_to_sourcetrail_port")'))
        self.port_sourcetrail_to_vim = int(vim.eval('sourcetrail#get("sourcetrail_to_vim_port")'))
        self.ip_addr = vim.eval('sourcetrail#get("sourcetrail_ip")')

    @classmethod
    def reload(cls):
        """Reload the options"""
        cls.instance = Options()

    @classmethod
    def inst(cls):
        """ Get the instance of Options"""
        if cls.instance is None:
            cls.reload()
        return cls.instance

    @classmethod
    def get_port_vim_to_sourcetrail(cls):
        """Returns the port sourcetrail listens to"""
        return cls.inst().port_vim_to_sourcetrail

    @classmethod
    def get_port_sourcetrail_to_vim(cls):
        """Returns the port vim listens to"""
        return cls.inst().port_sourcetrail_to_vim

    @classmethod
    def get_ip(cls):
        """Return the ip address"""
        return cls.inst().ip_addr

    @classmethod
    def print_settings(cls):
        """Prints the options"""
        print("Sourcetrail Settings: \n--------------------")
        print("Ports: ")
        print("g:sourcetrail_to_vim_port: " + str(cls.inst().port_sourcetrail_to_vim))
        print("g:vim_to_sourcetrail_port: " + str(cls.inst().port_vim_to_sourcetrail))
        print("Ip: ")
        print("g:sourcetrail_ip         : " + cls.inst().ip_addr)
        print("--------------------")

class ConnectionHandler(socketserver.BaseRequestHandler):
    # This class is instantiated once per connection to the server
    """Handler for incomming messages"""
    timeout = 5
    def handle(self):
        data = self.request.recv(1024).strip()
        text = data.decode('utf-8')
        eom_index = text.find("<EOM>")
        if not eom_index == 0:
            message_string = text[0:eom_index]
            message_fields = message_string.split(MESSAGE_SPLIT_STRING)
            if message_fields[0] == "moveCursor":
                Sourcetrail.set_new_buffer(message_fields[1], \
                                     int(message_fields[2]), int(message_fields[3]))
            if message_fields[0] == "ping":
                Sourcetrail.send_message("ping>>Vim<EOM>")
        else:
            print("asdfasfd")

class Sourcetrail:
    """Sourcetrail class for structur"""
    _instance = None
    def __init__(self):
        self.__col = 0
        self.__row = 0
        self.__file = ""
        self.__update = False
        self.__server = None

    def __del__(self):
        self.stop_server()

    @classmethod
    def inst(cls):
        """get a instance of Sourcetrail"""
        if cls._instance is None:
            cls._instance = Sourcetrail()
        return cls._instance

    @classmethod
    def row(cls):
        """returns the current row"""
        return cls.inst().__row

    @classmethod
    def col(cls):
        """returns the current column"""
        return cls.inst().__col


    @classmethod
    def file(cls):
        """returns the current file"""
        return cls.inst().__file

    @classmethod
    def start_server(cls):
        """starting the server to listen"""
        if cls.inst().__server is None:
            try:
                socketserver.ThreadingTCPServer.allow_reuse_address = True
                address = (Options.get_ip(), Options.get_port_sourcetrail_to_vim())
                cls.inst().__server = socketserver.ThreadingTCPServer(address, ConnectionHandler)
                server_thread = threading.Thread(target=cls.inst().__server.serve_forever)
                server_thread.daemon = True
                server_thread.start()
            except socket.error:
                print("Socket needed for Sourcetrail plugin already in use")

    @classmethod
    def stop_server(cls):
        """stop listening to the port"""
        if cls.inst().__server is not None:
            cls.inst().__server.shutdown()
            cls.inst().__server.server_close()

    @classmethod
    def restart_server(cls):
        """restart the server"""
        cls.inst().stop_server()
        Options.reload()
        cls.inst().start_server()

    @classmethod
    def send_activate_token(cls):
        """send activate token to sourcetrail"""
        cls.inst().start_server()
        filepath = vim.current.buffer.name
        (row, col) = vim.current.window.cursor

        col += 1 # cols returned by rowcol() are 0-based.

        text = "setActiveToken" + MESSAGE_SPLIT_STRING \
               + filepath + MESSAGE_SPLIT_STRING + str(row) \
               + MESSAGE_SPLIT_STRING + str(col) + "<EOM>"
        data = text.encode()
        try:
            cls.inst().send_message(data)
            print("Current Position sent to Sourcetrail")
        except socket.error:
            print("Counld not send to Sourcetrail")


    @classmethod
    def send_message(cls, message):
        """sends a message to sourcetrail"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((Options.get_ip(), Options.get_port_vim_to_sourcetrail()))
            sock.send(message)
            sock.close()
        except socket.error:
            raise socket.error

    @classmethod
    def set_new_buffer(cls, filepath, row, col):
        """set currents data"""
        cls.inst().__col = col
        cls.inst().__row = row
        cls.inst().__file = filepath
        cls.inst().__update = True

    @classmethod
    def update_buffer(cls):
        """update"""
        if cls.inst().__server is None:
            cls.inst().start_server()
            print("Vim was not listening to Sourcetrail. Vim is listening now.")
            print("Try to send again from Sourcetrail.")
        else:
            if cls.inst().__update:
                vim.command("e! " + cls.inst().__file)
                vim.current.window.cursor = (cls.inst().__row, cls.inst().__col)
                cls.inst().__update = False

    @classmethod
    def print_settings(cls):
        """ Prints Settings """
        Options.inst().print_settings()

