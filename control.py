#!/usr/bin/env python

import gevent
import gevent.monkey
gevent.monkey.patch_all()
gevent.monkey.patch_sys()
from gevent.queue import Queue, Empty

import serial

from datetime import datetime
import time
import logging
import readline
import sys

readline.parse_and_bind('set enable-keypad on')
readline.parse_and_bind('set echo-control-characters off')

log = logging.getLogger('control')
log.setLevel(logging.WARNING)

class Rig(object):
    def __init__(self, device):
        self.txlines = Queue()
        self.rxlines = Queue()
        self.tty = serial.Serial(device, 9600, timeout=1)
        gevent.spawn(self.receiver)
        gevent.spawn(self.sender)

    def receiver(self):
        rxbuf = []
        while True:
            char = self.tty.read(1)
            if char == '':
                continue
            elif char == '\r':
                log.debug("read %s" % repr(''.join(rxbuf)))
                self.rxlines.put(''.join(rxbuf))
                rxbuf = []
            elif char != '':
                rxbuf.append(char)

    def sendline(self, line):
        self.txlines.put(line)

    def sender(self):
        while True:
            line = self.txlines.get()
            log.debug("write %s" % repr(line))
            self.tty.write(line + '\r')

    def print_lines(self):
        while True:
            print "AI %s" % repr(self.rxlines.get())

    def close(self):
        self.tty.close()
    def __enter__(self, *args, **kwargs):
        pass
    def __exit__(self, *args, **kwargs):
        self.close()
    @property
    def freq(self):
        self.tty.write('BUF 0\n')
        return self.tty.readline()
    @freq.setter
    def freq(self, hz):
        pass


#                self.rxq = self.rxresponses
#                while True:
#                    try:
#                        r = self.rxresponses.get(timeout=1).strip()
#                    except Empty, e:
#                        raise Exception("No response to command.")
#                    log.debug("%s == %s?" % (repr(line), repr(r)))
#                    if r == line:
#                        self.rxq = self.rxlines
#                        assert r == line
#                        break
#                    elif r == 'N':
#                        raise Exception("Invalid command arguments")
#                        break
#                    elif r == '?':
#                        raise Exception("Unknown command")
#                        break
#                    else:
#                        # Probably got put in the wrong queue
#                        self.rxlines.put(r)
#            except Exception, e:
#                log.error("Error writing", exc_info=True)


def print_lines(rig):
    while True:
        line = rig.rxlines.get()
        print datetime.utcnow().isoformat(), line

def send_cmd(rig):
    while True:
        cmd = raw_input()
        rig.sendline(cmd)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    rig = Rig(sys.argv.pop())
    gevent.spawn(print_lines, rig)
    gevent.spawn(send_cmd, rig)
    while True:
        gevent.sleep(1)
        readline.redisplay()
