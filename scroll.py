#!/usr/bin/env python

# Shoutcast Playlist/Transcoder Roller - Mike Eder 2014

# Imports
import sys
import getopt
import os
import time
import glob
import commands
import subprocess
import ConfigParser

# Read the config file
config = ConfigParser.RawConfigParser()
config.readfp(open(r'/usr/local/etc/scroll.config'))

# Get some vars goin
srcPath = config.get('paths', 'srcPATH')
transPath = config.get('paths', 'transPATH')
plistPath = config.get('paths', 'plistPATH')
sCount = int(config.get('numbers', 'srmCOUNT'))

# Define all the things
# Find Server and Transcoder PIDs
def pids():
 transPid = []
 servPid = []
 transCmd = 'ps x | pgrep sc_trans'
 servCmd = 'ps x | pgrep sc_serv'
 try:
  servPid = subprocess.check_output([servCmd], shell=True)
#  print 'Found sc_serv process: %s' % (servPid)
 except:
  print '(sc_serv) : Server is not running.'
 try:
  trans = subprocess.check_output([transCmd], shell=True).split()
  for i in range(len(trans)):
   transPid.append(trans[i])
#   print 'Found sc_trans process: %s' % (trans[i])
   i += 1
 except:
  print '(sc_trans): Transcoders are not running.'
 return (servPid, transPid)

# Options that can be used in this script
def usage():
 print ''
 print 'sc-util accepts the following options:'
 print '(s)tart:	start sc_server and sc_trans'
 print '(g)enerate:	generate new playlists'
 print '(r)eload:	reload playlists'
 print '(f)lush:	flush logfiles (close and reopen) -- will make console logging stop'
 print '(n)ext #: 	jump to next song on stream #'
 print '(sh)uffle #:	toggle shuffle on/off for stream #'
 print '(st)op #:	shutdown sc_trans # (clean)'
 print '(k)ill:		shutdown sc_serv and sc_trans(all) (clean)' 
 print '(p)rocess:	list process info for sc_trans and sc_serv'
 print ''

# Main decision maker!
def main(argv):
 if len(sys.argv) < 2:
  print 'No options were given, I need to know what to do..'
  usage()
 try:
  opts, args = getopt.getopt(sys.argv[1:], 'sgrfn:sh:st:kp', ['start', 'generate', 'reload', 'flush', 'next=', 'shuffle=', 'stop=', 'kill', 'process'])
  print '-= Super Shoucast Utility 5000 =-'
 except getopt.GetoptError:
  usage()
  sys.exit(2)
 for opt, arg in opts:
  if opt == '-h':
   usage()
   sys.exit()
  elif opt in ('-s', '--start'):
   print 'Starting sc_serv and sc_trans'
   start(sCount)
  elif opt in ('-g', '--generate'):
   print 'Generating new playlists'
   generate()
  elif opt in ('-r', '--reload'):
   print 'Reloading playlists'
   reload(arg)
  elif opt in ('-f', '--flush'):
   print 'Flushing logs with HUP'
   flush()
  elif opt in ('-n', '--next'):
   print 'Jumping to next song on stream %s' % (arg)
   next(arg)
  elif opt in ('-sh', '--shuffle'):
   print 'Toggle shuffle on stream %s' % (arg)
   shuf(arg)
  elif opt in ('-st', '--stop'):
   print 'Stopping stream %s' % (arg)
   stop(arg)
  elif opt in ('-k', '--kill'):
   print 'Killing sc_serv and sc_trans'
   kill()
  elif opt in ('-p', '--process'):
   print 'Checking for running processes..'
   serv, trans = pids()
   if serv:
    print '(sc_serv) : Found running at %s\b' % (serv)
   else:
    print '(sc_serv) : Server is not running'
   if trans:
    i = 0
    for i in range(len(trans)):
     print '(sc_trans): Found running at %s' % (trans[i])
     i += 1
   else:
    print '(sc_trans): Transcoders not running.'
  else:
   print 'Invalid option %s' % (opt)
   usage()

# Start Server and Transcoder(s) if not already running
def start(sCount):
 i = 1
 serv, trans = pids()
 if serv == '':
  print 'Starting sc_serv'
  servPath = '/home/shoutcast/serv/'
  cmd2 = 'cd %s && ./sc_serv sc_serv.conf &' % (servPath)
  subprocess.call(cmd2, shell=True)
 else:
  print '(sc_serv) : Server already running.'
 if len(trans) == 0:
  while i <= sCount:
   try:
    transPath = '/home/shoutcast/trans/'
# Quiet command to start trans
    cmd1 = 'cd %s && ./sc_trans stream%d.conf > /dev/null 2> /dev/null &' % (transPath, i)
# Loud command to start trans
#    cmd1 = 'cd %s && ./sc_trans stream%d.conf &' % (transPath, i)
    print 'Starting stream %d' % (i)
    subprocess.call(cmd1, shell=True)
    time.sleep(0.1)
    i += 1
   except:
    print 'Unable to start transcoders'
    sys.exit(2)
 else:
  print '(sc_trans): %s Transcoders already running.' % (len(trans))

# Flush - doesnt do anything right now
def flush():
 serv, trans = pids()
 print trans, serv

# Force transcoder to next song
def next(arg):
 serv, trans = pids()
 cmd = 'kill -WINCH %s' % (trans[int(arg)])
 subprocess.call(cmd, shell=True)
 print 'Using: ' + cmd

# Reload playlists for all or 1 stream
def reload(arg):
 serv, trans = pids()
 try:
  if arg:
   cmd = 'kill -USR1 %s' % (trans[int(arg)])
   subprocess.call(cmd, shell=True)
   print 'Using: ' + cmd
  else:
   for i in range(len(trans)):
    cmd = 'kill -USR1 %s' % (trans[i])
    subprocess.call(cmd, shell=True)
    print 'Reloading playlist for stream %d' % (i+1)
    print 'Using: ' + cmd
    i += 1
 except:
  print 'Something went wrong reloading..'
 
# Generate new playlists from source folders
def generate():
 i = 0
 srcPath = '/home/music/source/out/'
 while i < sCount:
  try:
   plist = '/home/shoutcast/trans/playlists/stream%d.lst' % (i+1)
   cmd = 'find %s%d -name *.mp3 -print > %s' % (srcPath, i+1, plist)
   fin = sum(1 for line in open(plist))
   subprocess.call(cmd, shell=True)
   print 'Generating new playlist for Stream%d' % (i+1)
   fout = sum(1 for line in open(plist))
   print 'Total: %d New: %d' % (fout, fout-fin)
   i += 1
  except:
   print 'Error while generating playlists'
   i += 1
# Kill everything
# Doesnt kill server yet..
def kill():
 i = 0
 servPid, transPid = pids()
 try:
  while i < len(transPid):
   cmd = 'kill %s' % (transPid[i])
   subprocess.check_call(cmd, shell=True)
   i += 1
 except subprocess.CalledProcessError:
  print 'Unable to kill processes'
  i += 1


timerStart = time.time()

if __name__ == "__main__":
 main(sys.argv[1:])

timerEnd = time.time()
print 'Finished in %s seconds' % (str(round(timerEnd - timerStart, 4)))
