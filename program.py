#!/usr/bin/env python
#
# Copyright (C) 2012 by Jeffrey M. Laughlin <jeff@jefflaughlinconsulting.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import csv
import control
import gevent
from gevent.coros import Semaphore
import logging
import sys

logging.basicConfig(level=logging.DEBUG)

INFILE = sys.argv.pop()
TTYDEV = sys.argv.pop()

riglock = Semaphore()

OFFSETS = {
    '+': 1,
    '-': 2
}

# there is no tone 02.
# tn 01
# TN 01
# tn 02
# N
# tn 03
# TN 03
TONES = {
    '': 1,
    '67.0': 1,
    '71.9': 3,
    '74.4': 4,
    '77.0': 5,
    '79.7': 6,
    '82.5': 7,
    '85.4': 8,
    '88.5': 9,
    '91.5': 10,
    '94.8': 11,
    '97.4': 12,
    '100.0': 13,
    '103.5': 14,
    '107.2': 15,
    '110.9': 16,
    '114.8': 17,
    '118.8': 18,
    '123.0': 19,
    '127.3': 20,
    '131.8': 21,
    '136.5': 22,
    '141.3': 23,
    '146.2': 24,
    '151.4': 25,
    '156.7': 26,
    '162.2': 27,
    '167.9': 28,
    '173.8': 29,
    '179.9': 30,
    '186.2': 31,
    '192.8': 32,
    '203.5': 33,
    '210.7': 34,
    '218.1': 35,
    '225.7': 36,
    '233.6': 37,
    '241.8': 38,
    '250.3': 39,
}


def program(rec, rig, chan):
    cmdfmt = "MW 0,0,%03d,%011d,%01d,%01d,%01d,%01d,%01d,%01d,%02d,%04d,%02d,%09d,%01d,%01d"
    cmd = cmdfmt % (
        chan,
        int(float(rec['Output Frequency']) * 1000000),
        0,
        OFFSETS[rec['Input Frequency']],
        0,
        1 if TONES[rec['CTCSS Tones']] else 0,
        0,
        0,
        TONES[rec['CTCSS Tones']],
        10,
        TONES[rec['CTCSS Tones']],
        600000 if float(rec['Output Frequency']) < 150 else 5000000,
        0,
        0)
    riglock.acquire()
    rig.sendline(cmd)
    resp = rig.rxlines.get(timeout=1)
    if resp != 'MW':
        raise Exception("Expected %s but got %s" % (repr(cmd), repr(resp)))
    cmd = "MNA 0,%03d,%s" % (chan, rec['Location'][:8])
    rig.sendline(cmd)
    resp = rig.rxlines.get(timeout=1)
    if not resp.startswith('MNA'):
        raise Exception("Expected %s but got %s" % (repr(cmd), repr(resp)))
    riglock.release()

rig = control.Rig(TTYDEV)
rig.sendline('PS 1')
rig.sendline('PS 1')
resp = rig.rxlines.get(timeout=1)
resp = rig.rxlines.get(timeout=1)
with open(INFILE) as infile:
    csvr = csv.DictReader(infile)
    jobs = [gevent.spawn(program, rec, rig, num + 1) for num, rec in enumerate(csvr)]
gevent.joinall(jobs)

