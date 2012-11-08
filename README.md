pytmd700
========

Python control lib for Kenwood TM-D700a and similar radios.

Requirements
------------

* Python 2.7 
* gevent
* pyserial

Files
-----

control.py: Core radio comms framework built on gevent for performance. Also
            useful for sending commands to radio and monitoring it's status.

monitor.py: Simple curses app to display radio status. Together with mic
            control, it makes a headless radio useable.

program.py: Reads a .CSV file in ARRL Travel Plus for Repeaters format and
            programs it into the radio's memory channels.

