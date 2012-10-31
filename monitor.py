#!/usr/bin/env python

import control

import curses
import sys
from collections import defaultdict

import gevent

WINSIZE = {'height':2, 'width':16}

def proc_default(win, *args):
    pass

def proc_buf(win, bank, freq, step, dir_, rev, tone, ctcss, dcs, tone_idx,
             dcs_idx, ctcss_idx, offset, mode):
    freq = "%-3d.%03d" % (int(freq[2:5]), int(freq[5:8]))
    dir_ = int(dir_)
    win.addstr(int(bank),1,freq+(' ', '+', '-')[dir_])

def proc_mc(win, bank, chan_num):
    win.addstr(int(bank),9,"%03d" % (int(chan_num)))

def proc_bc(win, ct, tx):
    ct = bool(int(ct))
    tx = bool(int(ct))
    win.addstr(0,0, ' ')
    win.addstr(1,0, ' ')
    win.addstr(int(ct),0, 'C')
    win.addstr(int(tx),0, '*')

def proc_by(win, bank, status):
    bank = int(bank)
    status = bool(int(status))
    win.addstr(bank, 0, 'B' if status else ' ')

def proc_vmc(win, bank, mode):
    bank = int(bank)
    mode = int(mode)
    if mode == 0:
        win.addstr(bank,9,"   ")

procs = defaultdict(lambda: proc_default)
procs.update({
    'BUF': proc_buf,
    'MC': proc_mc,
    'BC': proc_bc,
    'BY': proc_by,
    'VMC': proc_vmc,
})

def update_screen(win, msg):
    parts=msg.split()
    proc = procs[parts[0]]
    args = ()
    if len(parts) > 1:
        args = parts[1].split(',')
    proc(win, *args)
    win.refresh()

def main(win=None, argv=None):
    if argv is None:
        argv = sys.argv
    curses.curs_set(0)
    curses.resize_term(2, 16)
    dev = argv[1]
    win = curses.newwin(WINSIZE['height'], WINSIZE['width'], 0, 0)
    rig = control.Rig(dev)
    rig.sendline('PS 1'); rig.rxlines.get()
    rig.sendline('PS 1'); rig.rxlines.get()
    rig.sendline('AI 1'); rig.rxlines.get()
    rig.sendline('DL 1'); rig.rxlines.get()
    rig.sendline('AG 0,10'); rig.rxlines.get()
    rig.sendline('AG 1,10'); rig.rxlines.get()
    rig.sendline('SQ 0,0A'); rig.rxlines.get()
    rig.sendline('SQ 1,0A'); rig.rxlines.get()
    rig.sendline('BC')
    for n in xrange(2):
        rig.sendline('BUF %s' % n)
        rig.sendline('MC %s' % n)
        rig.sendline('VMC %s' % n)
    def rxloop():
        while True:
            msg = rig.rxlines.get()
            update_screen(win, msg)
    gevent.spawn(rxloop).join()
    raw_input()

if __name__ == '__main__':
    print "starting"
    curses.wrapper(main)

