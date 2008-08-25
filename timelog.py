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
    project = config.get('main', 'default project')
    if os.path.isfile(databaseName) == False:
        print ansioutput.fuscia('Database not found, initializing...')
        initDatabase(databaseName)
    conn = sqlite3.connect(databaseName)
    c = conn.cursor()
    t = (project,'Did something that was really important')
    c.execute('insert into timelog (project, note) values (?, ?)', t)
    conn.commit()
    #c.execute('select * from timelog')
    #for row in c:
    #    print row
    c.close()
    print "done"


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt, e:
        # Ctrl-c
        raise e
    except SystemExit, e:
        # sys.exit()
        raise e
    except Exception, e:
        print "ERROR, UNEXPECTED EXCEPTION"
        print str(e)
        traceback.print_exc()
        sys.exit(1)
    else:
        # Main function is done, exit cleanly
        sys.exit(0)
