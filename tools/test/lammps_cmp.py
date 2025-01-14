#!/usr/bin/env python

"""
Run lammps and compare output with golden
"""

import sys, os

def compare_lines (gline, line):
    gline = gline.split()
    line = line.split()
    if len(line) != len(gline):
        return 1

    for (val1,val2) in zip(gline,line):
        if val1 == val2: continue
        try:
            val1 = float(val1)
            val2 = float(val2)
            if val1 == 0.0: return 1
            err = abs(val1 - val2) / val1
            if err < 1.0e-4:
                pass
            else:
                print "val1=%s, val2=%s Err=%s" % (val1, val2, err)                
                return 1
        except:
            return 1
    return 0
        
# Read the next line.
# skip empty lines and comments
# and lines with "time" in them
def nextline(f):
    while True:
        line = f.readline()
        if line == '':
            break
        line = line.strip()
        if line == '' or line[0] == '#':
            continue
        elif line.find("time") >= 0:
            continue
        elif line.find("(sec)") >= 0:
            continue
        else:
            break
    return line

err = 0
datafile = 'log.lammps'
args = []
for a in sys.argv:
    if datafile =='':
        datafile = a
    elif a == '--datafile':
        datafile = ''
    else:
        args.append(a)

if len(args) != 5:
    print "USAGE: %s lammps_executable mpi_args input golden_output" % args[0]
    sys.exit(-1)

try:
    gf = open(args[4])
except:
    print "Failed to open golden file %s" % args[4]
    sys.exit(-1)

filename = os.popen("which %s" % args[1]).read().strip()
cmd = "mpirun %s %s -log %s < %s > /dev/null" % (args[2], filename, datafile, args[3])
exe = os.popen(cmd)
retstr = exe.read()
if exe.close():
    print "ERROR: execution of mpirun cmd: \"%s\" failed.\n" % cmd
    print retstr
    sys.exit(-1)

try:
    f = open(datafile)
except:
    print "Failed to open output file %s", datafile
    sys.exit(-1)

errs = 0
while True:
    line = nextline(f)
    gline = nextline(gf)
    if line != gline:
        err = compare_lines(gline, line)
        if err:
            print "ERROR: Got\n%s\nExpected\n%s\n" % (line, gline)
            errs += 1
    if line == '' or gline == '':
        break

if errs:
    print "FAILED"
else:
    print "OK"
sys.exit(errs)
