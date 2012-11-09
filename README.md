pytmd700
========

Application and library for use with the Kenwood TM-D700a (and others?)

Description
-----------
This may also work with the TM-D710A, which I assume uses a similar or
identical protocol.  I'd appreciate any reports of success or failure there.

It should also work on Windows, but again I have no way to test it.

There are two main scripts in this distribution; program.py and monitor.py.

### Programming
program.py is for programming the memories. It reads from a CSV file in ARRL
Repeater Travel Plus format. I certainly would not want to program 200 memories
with the mic controls.

Usage: python program.py /dev/ttyUSB0 /home/jeff/repeaters.csv

### Controlling
monitor.py is the main user interface. It just displays the radio's basic
status information in a terminal window. It doesn't actually control anything.
But when used in conjunction with mic control, this is sufficient to operate
the basic functions and turn a paperweight into a useful radio. I've been using
it daily for a week.

Usage: python monitor.py /dev/ttyUSB0

### Commanding
control.py may be used to send raw commands to the radio and display the results. 

Usage: python control.py /dev/ttyUSB0 'PS 1;PS 1;MON 1'

Backstory
---------

I bought a TM-D700a RF deck at a hamfest for $60 after the seller reported that
the control head had been stolen out of his car. Kenwood doesn't sell it as a
part.  Supposedly the B2000 mobile control head is compatible, but it's over
$300. This makes used control heads as rare as hen's teeth, for obvious
reasons. I couldn't find any existing Linux compatible control software, and I
enjoy coding in Python, so I wrote this.

Requirements
------------

* Python 2.7 
* gevent
* pyserial

Files
-----

monitor.py: Simple curses app to display radio status. Together with mic
            control, it makes a headless radio useable.

program.py: Reads a .CSV file in ARRL Travel Plus for Repeaters format and
            programs it into the radio's memory channels.

control.py: Core radio comms framework built on gevent for performance. Also
            useful for sending commands to radio and monitoring it's status.

