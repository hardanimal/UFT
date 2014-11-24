#!/usr/bin/env python
# encoding: utf-8
"""Description: Initilize the logger
"""

__version__ = "0.1"
__author__ = "@boqiling"
__all__ = [""]

import sys
import logging
import os
import ctypes
#from PyQt4 import QtCore


class ColorizingStreamHandler(logging.StreamHandler):
    """color names to indices
    """
    color_map = {
        'black': 0,
        'red': 1,
        'green': 2,
        'yellow': 3,
        'blue': 4,
        'magenta': 5,
        'cyan': 6,
        'white': 7,
        }

    #levels to (background, foreground, bold/intense)
    if os.name == 'nt':
        level_map = {
            logging.DEBUG: (None, 'blue', True),
            logging.INFO: (None, 'white', False),
            logging.WARNING: (None, 'yellow', True),
            logging.ERROR: (None, 'red', True),
            logging.CRITICAL: ('red', 'white', True),
            }
    else:
        level_map = {
            logging.DEBUG: (None, 'blue', False),
            logging.INFO: (None, 'white', False),
            logging.WARNING: (None, 'yellow', False),
            logging.ERROR: (None, 'red', False),
            logging.CRITICAL: ('red', 'white', True),
            }
    csi = '\x1b['
    reset = '\x1b[0m'

    @property
    def is_tty(self):
        isatty = getattr(self.stream, 'isatty', None)
        return isatty and isatty()

    def emit(self, record):
        try:
            message = self.format(record)
            stream = self.stream
            if not self.is_tty:
                stream.write(message)
            else:
                self.output_colorized(message)
            stream.write(getattr(self, 'terminator', '\n'))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    if os.name != 'nt':
        def output_colorized(self, message):
            self.stream.write(message)
    else:
        import re
        ansi_esc = re.compile(r'\x1b\[((?:\d+)(?:;(?:\d+))*)m')

        nt_color_map = {
            0: 0x00,    # black
            1: 0x04,    # red
            2: 0x02,    # green
            3: 0x06,    # yellow
            4: 0x01,    # blue
            5: 0x05,    # magenta
            6: 0x03,    # cyan
            7: 0x07,    # white
        }

        def output_colorized(self, message):
            parts = self.ansi_esc.split(message)
            write = self.stream.write
            h = None
            fd = getattr(self.stream, 'fileno', None)
            if fd is not None:
                fd = fd()
                if fd in (1, 2):    # stdout or stderr
                    h = ctypes.windll.kernel32.GetStdHandle(-10 - fd)
            while parts:
                text = parts.pop(0)
                if text:
                    write(text)
                if parts:
                    params = parts.pop(0)
                    if h is not None:
                        params = [int(p) for p in params.split(';')]
                        color = 0
                        for p in params:
                            if 40 <= p <= 47:
                                color |= self.nt_color_map[p - 40] << 4
                            elif 30 <= p <= 37:
                                color |= self.nt_color_map[p - 30]
                            elif p == 1:
                                color |= 0x08   # foreground intensity on
                            elif p == 0:    # reset to default color
                                color = 0x07
                            else:
                                pass    # error condition ignored
                        ctypes.windll.kernel32.SetConsoleTextAttribute(h, color)

    def colorize(self, message, record):
        if record.levelno in self.level_map:
            bg, fg, bold = self.level_map[record.levelno]
            params = []
            if bg in self.color_map:
                params.append(str(self.color_map[bg] + 40))
            if fg in self.color_map:
                params.append(str(self.color_map[fg] + 30))
            if bold:
                params.append('1')
            if params:
                message = ''.join((self.csi, ';'.join(params),
                                   'm', message, self.reset))
        return message

    def format(self, record):
        message = logging.StreamHandler.format(self, record)
        if self.is_tty:
            # Don't colorize any traceback
            parts = message.split('\n', 1)
            parts[0] = self.colorize(parts[0], record)
            message = '\n'.join(parts)
        return message


#class QtHandler(logging.Handler):
#
#    def __init__(self):
#        logging.Handler.__init__(self)
#
#    def emit(self, record):
#        record = self.format(record)
#        if record:
#            XStream.stdout().write('{0}\n'.format(record))


#class XStream(QtCore.QObject):
#    _stdout = None
#    _stderr = None
#    messageWritten = QtCore.pyqtSignal(str)
#
#    def flush(self):
#        pass
#
#    def fileno(self):
#        return -1
#
#    def write(self, msg):
#        if (not self.signalsBlocked()):
#            self.messageWritten.emit(unicode(msg))
#
#    @staticmethod
#    def stdout():
#        if (not XStream._stdout):
#            XStream._stdout = XStream()
#            sys.stdout = XStream._stdout
#        return XStream._stdout
#
#    @staticmethod
#    def stderr():
#        if (not XStream._stderr):
#            XStream._stderr = XStream()
#            sys.stderr = XStream._stderr
#        return XStream._stderr


def init_logger(mylogger, level=logging.INFO):
    formatter = logging.Formatter('[ %(asctime)s ] %(levelname)s %(message)s')

    # stdout handler
    #stdhl = logging.StreamHandler(sys.stdout)
    stdhl = ColorizingStreamHandler(sys.stdout)
    stdhl.setFormatter(formatter)
    stdhl.setLevel(logging.DEBUG)    # print everything

    # file handler
    #hdlr = logging.FileHandler("./uft.log")
    #hdlr.setFormatter(formatter)
    # save WARNING, EEROR and CRITICAL to file
    #hdlr.setLevel(logging.WARNING)

    # qt handler
    #qthl = QtHandler()
    #qthl.setFormatter(formatter)
    #qthl.setLevel(logging.DEBUG)

    # add handlers
    #mylogger.addHandler(hdlr)
    mylogger.addHandler(stdhl)
    mylogger.setLevel(level)
