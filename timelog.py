#!/usr/bin/env python
# vim:ts=4:sw=4:ft=python:fileencoding=utf-8
"""TimeLog

Simple command line interface to track what tasks are worked on throughout the
day.

"""

# $Id$
__version__ = "$Rev$"

import sys
import os
import traceback
import ConfigParser
import sqlite3

import ansioutput


def gb():
    """Global variables."""
    gb.conn = ''
    gb.c = ''
    gb.project = ''


def usage():
    """Usage information (called with -h option)."""
    print "Usage:  %s" % os.path.basename(sys.argv[0])
    print ' -h  This help message'


def initDatabase(db):
    """Initializes the database."""
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''create table if not exists timelog
        (id integer primary key autoincrement, 
        project text,
        created_at text default CURRENT_TIMESTAMP,
        note text)''')
    conn.commit()
    c.close()


def getCurrentProject():
    """Retrieves and formats the project name"""
    return ansioutput.darkgreen('Current project: ') + ansioutput.green(gb.project)


def processUserInput():
    """Takes the user input and processes it"""
    msg = raw_input('timelog> ')
    # todo: check a dict instead
    if msg == 'h':
        print 'Use the following special keywords:'
        print 'h  - This help message'
        print 'r  - Show all entries'
        print 'rd - Show all entries from today'
        print 'rp - List all known projects'
        print 'p  - Show current project name'
        print 'p <project name> - Set a new project name'
        print 'q  - Quit program'
        print
        print 'All other text will be considered a note'
    elif msg == 'q':
        return True
    elif msg == 'r':
        gb.c.execute("""select datetime(created_at, 'localtime') as created_at_local,
            project, note from timelog""")
        for row in gb.c:
            print '%s : %-12s : %s' % row
    elif msg == 'rd':
        gb.c.execute("""select datetime(created_at, 'localtime') as created_at_local,
            project, note from timelog 
            where date(created_at, 'localtime') like date('now', 'localtime')""")
        for row in gb.c:
            print '%s : %-12s : %s' % row
    elif msg == 'rp':
        gb.c.execute("""select distinct project from timelog""")
        for row in gb.c:
            print '%s' % row
    elif msg == 'p':
        print getCurrentProject()
    elif msg.startswith('p ') == True:
        # drop first two characters and set rest to project name
        gb.project = msg[2:]
        print getCurrentProject()
    else:
        t = (gb.project, msg)
        gb.c.execute('insert into timelog (project, note) values (?, ?)', t)
        gb.conn.commit()
    processUserInput()


def doCleanup():
    """Cleanup functions to run before exiting"""
    gb.conn.commit()
    gb.c.close()


def main():
    """The main function."""
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        usage()
        sys.exit(2)
    # rest of code here
    config = ConfigParser.ConfigParser()
    config.read('./options.cfg')
    databaseName = config.get('main', 'database')
    gb.project = config.get('main', 'default project')
    if os.path.isfile(databaseName) == False:
        print ansioutput.fuscia('Database not found, initializing...')
        initDatabase(databaseName)
    gb.conn = sqlite3.connect(databaseName)
    gb.c = gb.conn.cursor()
    print getCurrentProject()
    print ansioutput.turquoise('Main Menu')
    print ansioutput.teal('Enter h for help or enter note')
    processUserInput()
    # if we're here then user pressed q to quit
    doCleanup()
    print "goodbye"


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt, e:
        # Ctrl-c
        doCleanup()
        # need an extra line break
        print
        print "User requested shutdown. Please consider using the q option instead"
        sys.exit(0)
    except SystemExit, e:
        # sys.exit()
        doCleanup()
        sys.exit(0)
    except Exception, e:
        print "ERROR, UNEXPECTED EXCEPTION"
        print str(e)
        traceback.print_exc()
        sys.exit(1)
    else:
        # Main function is done, exit cleanly
        sys.exit(0)
