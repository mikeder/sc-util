#!/usr/bin/env python

# Shoutcast Playlist/Transcoder Roller - Mike Eder 2014

# Imports
import sys, getopt
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
def pids():
 transPid = []
 servPid = ''
 transCmd = 'ps x | pgrep sc_trans'
 servCmd = 'ps x | pgrep sc_serv'
 try:
  serv = subprocess.check_output([servCmd], shell=True).split()
  print 'Found sc_serv running with PID %d' % (serv)
 except:
  print 'Server is not running.         (sc_serv)'
 try:
  trans = subprocess.check_output([transCmd], shell=True).split()
  for i in range(len(trans)):
   transPid.append(trans[i])
   i += 1
 except:
  print 'Transcoders are not running.   (sc_trans)'
 return (transPid, servPid)

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
   reload()
  elif opt in ('-f', '--flush'):
   print 'Flushing logs with HUP'
   flush()
  elif opt in ('-n', '--next'):
   print 'Jumping to next song on stream %d' % (arg)
   next(arg)
  elif opt in ('-sh', '--shuffle'):
   print 'Toggle shuffle on stream %d' % (arg)
   shuf(arg)
  elif opt in ('-st', '--stop'):
   print 'Stopping stream %d' % (arg)
   stop(arg)
  elif opt in ('-k', '--kill'):
   print 'Killing sc_serv and sc_trans'
   kill()
  elif opt in ('-p', '--process'):
   print 'Checking for running processes..'
   pids()
  else:
   print 'Invalid option %s' % (opt)
   usage()

def start(sCount):
 i = 1
 while i < sCount:
  try:
   transPath = '/home/shoutcast/trans/'
   servPath = '/home/shoutcast/serv/'
   cmd1 = '%ssc_trans %sstream%d.conf &' % (transPath, transPath, i)
   cmd2 = '%ssc_serv %ssc_serv.conf &' % (servPath, servPath)
   print 'Starting stream %d' % (i)
   subprocess.call(cmd1, shell=True)
   i += 1
  except:
   print 'Unable to start transcoders'
   sys.exit(2)

def generate():
 i = 0
 srcPath = '/home/music/source/out/'
 while i < sCount:
  try:
   plist = '/home/shoutcast/trans/playlists/stream%d.lst' % (i+1)
   cmd = 'find %s%d -name *.mp3 -print > %s' % (srcPath, i+1, plist)
   subprocess.call(cmd, shell=True)
   print 'Generating new playlist for stream%d' % (i+1)
   i += 1
  except:
   print 'Error while generating playlists'

def kill():
 i = 0
 transPid, servPid = pids()
 try:
  while i < len(transPid):
   cmd = 'kill %s' % (transPid[i])
   subprocess.check_call(cmd, shell=True)
   i += 1
 except subprocess.CalledProcessError:
  print 'Unable to kill processes'
  i += 1
# def rollPlay():
# Function to do:
# - Find new mp3 files in source folders for sCount
# find /path/to/mp3/directory -type f -name "*.mp3" > playlist.lst
# - put paths to new mp3 in stream playlist
# - change symlink for playlist file
# - send KILL -HUP to PID's to reload list
# - return how many songs added to list and how many total

def rollPlay(sCount):
 i = 1
 while i <= sCount:
  print '-- Generating new playlist files'
  
# def rollTrans(sCount):
# Function to do:
# - Check for PID's
# - if not running start
# - if running restart

def rollTrans(sCount):
 pids = pids() 
 if not pids:
  print '-- No running transcoders found'
  print '-- Attempting to start %d stream transcoders' % (sCount)
#  try:
#   i = 1
#   for i in range(sCount):
#    startCmd = '/home/music/shoutcast/trans/sc_trans stream%d.conf &' % (i)
 elif len(pids) >= sCount:
  print '-- Found %d running transcoders..' % (len(pids))
 else:
  print '-- Expected %d, only found %d running..' % (sCount, len(pids))

if __name__ == "__main__":
 main(sys.argv[1:])

print 'Exiting.'
