#!/usr/bin/env python

import control

import curses
import sys
from collections import defaultdict

import gevent

WINSIZE = {'height':5, 'width':32}

def proc_default(rig, win, *args):
    pass

def proc_buf(rig, win, bank, freq, step, dir_, rev, tone, ctcss, dcs, tone_idx,
             dcs_idx, ctcss_idx, offset, mode):
    freq = "%-3d.%03d" % (int(freq[2:5]), int(freq[5:8]))
    dir_ = int(dir_)
    win.addstr(int(bank),2,freq+(' ', '+', '-')[dir_])

def proc_mc(rig, win, bank, chan_num):
    bank = int(bank)
    chan_num = int(chan_num)
    rig.vfos[bank].chan_num = chan_num
    win.addstr(int(bank),11,"%03d" % (chan_num))
    # get channel name
    rig.sendline('MNA 0,%03d' % (chan_num))

def proc_mna(rig, win, bank, chan_num, chan_name):
    bank = int(bank)
    chan_num = int(chan_num)
    # bah, need to save some state to do this properly :(
    for n, vfo in enumerate(rig.vfos):
        if vfo.chan_num == chan_num:
            win.addstr(n, 15, ' ' * 8)
            win.addstr(n, 15, chan_name)

def proc_bc(rig, win, ct, tx):
    ct = bool(int(ct))
    tx = bool(int(ct))
    win.addstr(0,1, ' ')
    win.addstr(1,1, ' ')
    win.addstr(int(ct),1, 'C')
    win.addstr(int(tx),1, '*')

def proc_by(rig, win, bank, status):
    bank = int(bank)
    status = bool(int(status))
    win.addstr(bank, 0, 'B' if status else ' ')
    #proc_bc(rig, win, '0', '0')

def proc_vmc(rig, win, bank, mode):
    bank = int(bank)
    mode = int(mode)
    if mode == 0:
        win.addstr(bank,11,"   ")
        win.addstr(bank,15," " * 8)

procs = defaultdict(lambda: proc_default)
procs.update({
    'BUF': proc_buf,
    'MC': proc_mc,
    'BC': proc_bc,
    'BY': proc_by,
    'VMC': proc_vmc,
    'MNA': proc_mna,
})

def update_screen(rig, win, msg):
    head, sep, tail=msg.partition(' ')
    proc = procs[head]
    args = ()
    if tail != '':
        args = tail.split(',')
    proc(rig, win, *args)
    win.refresh()

def main(win=None, argv=None):
    if argv is None:
        argv = sys.argv
    curses.curs_set(0)
    curses.resize_term(WINSIZE['height'], WINSIZE['width'])
    dev = argv[1]
    win = curses.newwin(WINSIZE['height'], WINSIZE['width'], 0, 0)
    rig = control.Rig(dev)
    for n in xrange(5):
        rig.sendline('PS 1'); rig.rxlines.get()
    while True:
        try:
            rig.rxlines.get(block=False)
        except gevent.queue.Empty:
            break
    rig.sendline('AI 1'); rig.rxlines.get()
    rig.sendline('DL 1'); rig.rxlines.get()
    rig.sendline('AG 0,1E'); rig.rxlines.get()
    rig.sendline('AG 1,1B'); rig.rxlines.get()
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
            update_screen(rig, win, msg)
    gevent.spawn(rxloop).join()
    raw_input()

if __name__ == '__main__':
    print "starting"
    curses.wrapper(main)

