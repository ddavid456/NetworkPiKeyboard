#!/usr/bin/env python3
import time
import socket
import threading
import re

__version__ = '1.0.0'

NULL_CHAR = chr(0x00)

'''
To Toggle Shift send KEY_SHIFTTOGGLE
To Query for Shift state send KET_SHIFTSTATE
'''

class Keyboard:

    def __init__(self):
        self.shiftActive = False
        self._keyreference = {
                'KEY_A': 0x04, 'KEY_B': 0x05,
                'KEY_C': 0x06, 'KEY_D': 0x07,
                'KEY_E': 0x08, 'KEY_F': 0x09,
                'KEY_G': 0x0a, 'KEY_H': 0x0b,
                'KEY_I': 0x0c, 'KEY_J': 0x0d,
                'KEY_K': 0x0e, 'KEY_L': 0x0f,
                'KEY_M': 0x10, 'KEY_N': 0x11,
                'KEY_O': 0x12, 'KEY_P': 0x13,
                'KEY_Q': 0x14, 'KEY_R': 0x15,
                'KEY_S': 0x16, 'KEY_T': 0x17,
                'KEY_U': 0x18, 'KEY_V': 0x19,
                'KEY_W': 0x1a, 'KEY_X': 0x1b,
                'KEY_Y': 0x1c, 'KEY_Z': 0x1d,
                'KEY_1': 0x1e, 'KEY_2': 0x1f,
                'KEY_3': 0x20, 'KEY_4': 0x21,
                'KEY_5': 0x22, 'KEY_6': 0x23,
                'KEY_7': 0x24, 'KEY_8': 0x25,
                'KEY_9': 0x26, 'KEY_0': 0x27,
                'KEY_ENTER': 0x28, 'KEY_ESC': 0x29,
                'KEY_BACKSPACE': 0x2a, 'KEY_TAB': 0x2b,
                'KEY_SPACE': 0x2c, 'KEY_MINUS': 0x2d,
                'KEY_EQUAL': 0x2e, 'KEY_LEFTBRACE': 0x2f,
                'KEY_RIGHTBRACE': 0x30, 'KEY_BACKSLASH': 0x31,
                'KEY_HASHTILDE': 0x32, 'KEY_SEMICOLON': 0x33,
                'KEY_APOSTROPHE': 0x34, 'KEY_GRAVE': 0x35,
                'KEY_COMMA': 0x36, 'KEY_DOT': 0x37,
                'KEY_SLASH': 0x38, 'KEY_CAPSLOCK': 0x39,
                'KEY_F1': 0x3a, 'KEY_F2': 0x3b,
                'KEY_F3': 0x3c, 'KEY_F4': 0x3d,
                'KEY_F5': 0x3e, 'KEY_F6': 0x3f,
                'KEY_F7': 0x40, 'KEY_F8': 0x41,
                'KEY_F9': 0x42, 'KEY_F10': 0x43,
                'KEY_F11': 0x44, 'KEY_F12': 0x45,
                'KEY_F13': 0x68, 'KEY_F14': 0x69,
                'KEY_F15': 0x6a, 'KEY_F16': 0x6b,
                'KEY_F17': 0x6c, 'KEY_F18': 0x6d,
                'KEY_F19': 0x6e, 'KEY_F20': 0x6f,
                'KEY_F21': 0x70, 'KEY_F22': 0x71,
                'KEY_F23': 0x72, 'KEY_F24': 0x73,
                'KEY_SYSRQ': 0x46, 'KEY_SCROLLLOCK': 0x47,
                'KEY_PAUSE': 0x48, 'KEY_INSERT': 0x49,
                'KEY_HOME': 0x4a, 'KEY_PAGEUP': 0x4b,
                'KEY_DELETE': 0x4c, 'KEY_END': 0x4d,
                'KEY_PAGEDOWN': 0x4e, 'KEY_RIGHT': 0x4f,
                'KEY_LEFT': 0x50, 'KEY_DOWN': 0x51,
                'KEY_UP': 0x52, 'KEY_MEDIA_PLAYPAUSE': 0xe8,
                'KEY_MEDIA_STOPCD': 0xe9, 'KEY_MEDIA_PREVIOUSSONG': 0xea,
                'KEY_MEDIA_NEXTSONG': 0xeb, 'KEY_MEDIA_EJECTCD': 0xec,
                'KEY_MEDIA_VOLUMEUP': 0xed, 'KEY_MEDIA_VOLUMEDOWN': 0xee,
                'KEY_MEDIA_MUTE': 0xef, 'KEY_MEDIA_WWW': 0xf0,
                'KEY_MEDIA_BACK': 0xf1, 'KEY_MEDIA_FORWARD': 0xf2,
                'KEY_MEDIA_STOP': 0xf3, 'KEY_MEDIA_FIND': 0xf4,
                'KEY_MEDIA_SCROLLUP': 0xf5, 'KEY_MEDIA_SCROLLDOWN': 0xf6,
                'KEY_MEDIA_EDIT': 0xf7, 'KEY_MEDIA_SLEEP': 0xf8,
                'KEY_MEDIA_COFFEE': 0xf9, 'KEY_MEDIA_REFRESH': 0xfa,
                'KEY_MEDIA_CALC': 0xfb, 'KEY_OPEN': 0x74,
                'KEY_HELP': 0x75, 'KEY_PROPS': 0x76,
                'KEY_FRONT': 0x77, 'KEY_STOP': 0x78,
                'KEY_AGAIN': 0x79, 'KEY_UNDO': 0x7a,
                'KEY_CUT': 0x7b, 'KEY_COPY': 0x7c,
                'KEY_PASTE': 0x7d, 'KEY_FIND': 0x7e,
                'KEY_MUTE': 0x7f, 'KEY_VOLUMEUP': 0x80,
                'KEY_VOLUMEDOWN': 0x81
                }

    @property
    def ShiftState(self):
        return self.shiftActive

    def ShiftToggle(self):
        self.shiftActive = not self.shiftActive

    def SendKey(self, value):
        if self.shiftActive:
            # Press
            self.SendToPC(chr(0x20) + NULL_CHAR + chr(self._keyreference[value]) + NULL_CHAR*5)
        else:
            self.SendToPC(NULL_CHAR*2 + chr(self._keyreference[value]) + NULL_CHAR*5)
        # Release
        self.SendToPC(NULL_CHAR*8)

    def SendToPC(self, packet):
        with open('/dev/hidg0', 'rb+') as fd:
            fd.write(packet.encode())


class Server(threading.Thread):
    '''
    This is a threading.Thread object so that multiple servers can run simultaneously.
    '''

    def __init__(self, port):
        '''
        port = the network port to listen for connections.
        '''
        threading.Thread.__init__(self)
        self.port = port
        self.lock = threading.Lock()
        self.masterKeyboard = Keyboard()
        self.start()  # Calls the self.run() method as a thread

    def run(self):
        '''
        Initializes the server
        '''
        host = ''
        port = self.port
        backlog = 5
        self.size = 1024

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((host, port))
        self.s.listen(backlog)

        print('Listening for connections.')
        while True:
            client, address = self.s.accept()
            if not client == None:  # if a client has connected
                ServerThread(client, address, self.lock, self.masterKeyboard).start()  # create a new thread to handle this client
            else:
                print('waiting for client to connect')
                time.sleep(2)
                continue


class ServerThread(threading.Thread):

    def __init__(self, client, address, lock, keyboard):
        threading.Thread.__init__(self)
        self.lock = lock
        self.keyboard = keyboard
        self.regEx = re.compile(r'(KEY_(.{1,}))')
        self.client = client
        self.address = address
        self.size = 1024

    def run(self):
        print('new client=', self.address, 'at', time.asctime())
        self.client.send('WELCOME TO PI HID KEYBOARD\r\nv{} {}\r\n'.format(__version__, time.asctime()).encode())
        # Process the incoming data
        while not self.client == None:  # client is connected
            try:

                data = self.client.recv(self.size).decode().upper()
                self.lock.acquire()
                if data == '':
                    print('Socket Forced Closed')
                    break
            except Exception as e:
                print(e)
                data = None
                time.sleep(1)
                # print(self.address,'no data')
                continue

            if data:
                match = self.regEx.search(str(data))
                #Processes Command
                if match:
                    try:
                        if match.group(1) == 'KEY_SHIFTTOGGLE':
                            self.keyboard.ShiftToggle()
                        elif match.group(1) == 'KEY_SHIFTSTATE':
                            self.client.send('KEY_SHIFT_{}\r\n'.format(self.keyboard.ShiftState).upper().encode())
                        else:
                            self.keyboard.SendKey(match.group(1))
                        self.client.send('OK\r\n'.encode())
                    except Exception as e:
                        print(e)
                elif '\r\n' in data:
                    pass
                else:
                    self.client.send('ERR\r\n'.encode())

            self.lock.release()

        self.lock.release()
        print('Socket destroyed', self.address)

####################
Server(5023)  # Start the server

